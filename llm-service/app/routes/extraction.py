import logging
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
import time

from models.schemas import (
    DocumentUploadRequest,
    ExtractionResult,
    BatchExtractionRequest,
    BatchExtractionResponse,
    ProcessingStatus,
    ErrorResponse,
    SearchRequest,
    SearchResponse,
    KnowledgeStats,
    DeleteKnowledgeRequest
)
from services.document_processor import DocumentProcessor
from services.rag_service import RAGService
from database.mysql_client import get_mysql_client, MySQLClient
from core.config import settings

logger = logging.getLogger(__name__)

# Khởi tạo router
router = APIRouter()

# Khởi tạo services
document_processor = DocumentProcessor()
rag_service = RAGService()


@router.post("/extract", response_model=ExtractionResult)
async def extract_knowledge(
    request: DocumentUploadRequest,
    background_tasks: BackgroundTasks,
    mysql: MySQLClient = Depends(get_mysql_client)
):
    """
    Extract knowledge từ một document
    
    API này sẽ:
    1. Kiểm tra document tồn tại trong backend DB
    2. Đọc và parse file document
    3. Chia document thành chunks
    4. Tạo embeddings và lưu vào vector store
    5. Cập nhật status trong backend DB
    
    Args:
        request: Thông tin document cần extract
        background_tasks: FastAPI background tasks
        mysql: MySQL client dependency
        
    Returns:
        ExtractionResult: Kết quả extraction
    """
    try:
        # Kiểm tra user tồn tại
        if not mysql.check_user_exists(request.user_id):
            raise HTTPException(
                status_code=404,
                detail=f"User với ID {request.user_id} không tồn tại"
            )
        
        # Kiểm tra document tồn tại và thuộc về user
        doc_info = mysql.get_document_by_id(request.document_id)
        if not doc_info:
            raise HTTPException(
                status_code=404,
                detail=f"Document với ID {request.document_id} không tồn tại"
            )
        
        if doc_info["owner_id"] != request.user_id:
            raise HTTPException(
                status_code=403,
                detail="Bạn không có quyền truy cập document này"
            )
        
        # Cập nhật status = processing
        mysql.update_document_status(request.document_id, "processing")
        
        # Thực hiện extraction trong background
        background_tasks.add_task(
            _process_document_extraction,
            request,
            doc_info,
            mysql
        )
        
        # Trả về response ngay lập tức
        return ExtractionResult(
            document_id=request.document_id,
            status=ProcessingStatus.PROCESSING,
            chunks_extracted=0,
            error_message=None,
            processing_time=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi extract document {request.document_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi server: {str(e)}"
        )


async def _process_document_extraction(
    request: DocumentUploadRequest,
    doc_info: dict,
    mysql: MySQLClient
):
    """
    Background task để xử lý extraction
    
    Args:
        request: Document upload request
        doc_info: Thông tin document từ DB
        mysql: MySQL client
    """
    start_time = time.time()
    
    try:
        # Merge metadata
        metadata = {
            **request.metadata,
            "document_id": request.document_id,
            "original_name": doc_info["original_name"],
            "file_type": doc_info["file_type"],
            "owner_name": doc_info.get("owner_name", ""),
            "owner_email": doc_info.get("owner_email", "")
        }
        
        # Process document
        chunks_extracted = await document_processor.process_document(
            file_path=request.file_path,
            user_id=request.user_id,
            metadata=metadata
        )
        
        # Cập nhật status = ready
        mysql.update_document_status(request.document_id, "ready")
        
        processing_time = time.time() - start_time
        logger.info(
            f"✅ Hoàn thành extraction document {request.document_id}: "
            f"{chunks_extracted} chunks trong {processing_time:.2f}s"
        )
        
    except Exception as e:
        # Cập nhật status = error
        mysql.update_document_status(request.document_id, "error")
        logger.error(f"❌ Lỗi extraction document {request.document_id}: {str(e)}")


@router.post("/extract-batch", response_model=BatchExtractionResponse)
async def extract_knowledge_batch(
    request: BatchExtractionRequest,
    background_tasks: BackgroundTasks,
    mysql: MySQLClient = Depends(get_mysql_client)
):
    """
    Extract knowledge từ nhiều documents cùng lúc
    
    Args:
        request: Batch extraction request
        background_tasks: FastAPI background tasks
        mysql: MySQL client dependency
        
    Returns:
        BatchExtractionResponse: Kết quả batch extraction
    """
    try:
        # Kiểm tra user tồn tại
        if not mysql.check_user_exists(request.user_id):
            raise HTTPException(
                status_code=404,
                detail=f"User với ID {request.user_id} không tồn tại"
            )
        
        results = []
        
        # Process từng document
        for doc_id in request.document_ids:
            try:
                # Lấy thông tin document
                doc_info = mysql.get_document_by_id(doc_id)
                
                if not doc_info:
                    results.append(ExtractionResult(
                        document_id=doc_id,
                        status=ProcessingStatus.ERROR,
                        chunks_extracted=0,
                        error_message="Document không tồn tại"
                    ))
                    continue
                
                if doc_info["owner_id"] != request.user_id:
                    results.append(ExtractionResult(
                        document_id=doc_id,
                        status=ProcessingStatus.ERROR,
                        chunks_extracted=0,
                        error_message="Không có quyền truy cập"
                    ))
                    continue
                
                # Tạo request cho từng document
                doc_request = DocumentUploadRequest(
                    user_id=request.user_id,
                    document_id=doc_id,
                    file_path=doc_info["file_path"],
                    metadata={}
                )
                
                # Add background task
                background_tasks.add_task(
                    _process_document_extraction,
                    doc_request,
                    doc_info,
                    mysql
                )
                
                results.append(ExtractionResult(
                    document_id=doc_id,
                    status=ProcessingStatus.PROCESSING,
                    chunks_extracted=0
                ))
                
            except Exception as e:
                logger.error(f"Lỗi khi xử lý document {doc_id}: {str(e)}")
                results.append(ExtractionResult(
                    document_id=doc_id,
                    status=ProcessingStatus.ERROR,
                    chunks_extracted=0,
                    error_message=str(e)
                ))
        
        # Tính toán summary
        successful = sum(1 for r in results if r.status != ProcessingStatus.ERROR)
        failed = len(results) - successful
        
        return BatchExtractionResponse(
            total=len(results),
            successful=successful,
            failed=failed,
            results=results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi batch extraction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi server: {str(e)}"
        )


@router.post("/search", response_model=SearchResponse)
async def search_knowledge(
    request: SearchRequest,
    mysql: MySQLClient = Depends(get_mysql_client)
):
    """
    Tìm kiếm trong knowledge base
    
    Args:
        request: Search request
        mysql: MySQL client dependency
        
    Returns:
        SearchResponse: Kết quả tìm kiếm
    """
    try:
        # Kiểm tra user tồn tại
        if not mysql.check_user_exists(request.user_id):
            raise HTTPException(
                status_code=404,
                detail=f"User với ID {request.user_id} không tồn tại"
            )
        
        # Thực hiện search
        start_time = time.time()
        
        results = await rag_service.search(
            query=request.query,
            user_id=request.user_id if request.search_scope == "user" else None,
            top_k=request.top_k,
            filters=request.filters
        )
        
        search_time = time.time() - start_time
        
        return SearchResponse(
            query=request.query,
            total_results=len(results),
            results=results,
            search_time=search_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi search: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi server: {str(e)}"
        )


@router.get("/stats/{user_id}", response_model=KnowledgeStats)
async def get_knowledge_stats(
    user_id: int,
    mysql: MySQLClient = Depends(get_mysql_client)
):
    """
    Lấy thống kê về knowledge base của user
    
    Args:
        user_id: ID của user
        mysql: MySQL client dependency
        
    Returns:
        KnowledgeStats: Thống kê knowledge
    """
    try:
        # Kiểm tra user tồn tại
        if not mysql.check_user_exists(user_id):
            raise HTTPException(
                status_code=404,
                detail=f"User với ID {user_id} không tồn tại"
            )
        
        # Lấy thống kê từ vector store
        stats = await rag_service.get_user_stats(user_id)
        
        # Lấy thông tin documents từ MySQL
        documents = mysql.get_user_documents(user_id)
        
        return KnowledgeStats(
            user_id=user_id,
            total_documents=len(documents),
            total_chunks=stats.get("total_chunks", 0),
            last_updated=stats.get("last_updated"),
            storage_used_mb=stats.get("storage_used_mb", 0.0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi get stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi server: {str(e)}"
        )


@router.post("/delete-knowledge")
async def delete_knowledge(
    request: DeleteKnowledgeRequest,
    mysql: MySQLClient = Depends(get_mysql_client)
):
    """
    Xóa knowledge của user
    
    Args:
        request: Delete request
        mysql: MySQL client dependency
        
    Returns:
        Success message
    """
    try:
        # Kiểm tra confirm
        if not request.confirm:
            raise HTTPException(
                status_code=400,
                detail="Phải set confirm=true để xóa knowledge"
            )
        
        # Kiểm tra user tồn tại
        if not mysql.check_user_exists(request.user_id):
            raise HTTPException(
                status_code=404,
                detail=f"User với ID {request.user_id} không tồn tại"
            )
        
        # Xóa knowledge
        if request.document_ids:
            # Xóa specific documents
            deleted_count = await rag_service.delete_documents(
                user_id=request.user_id,
                document_ids=request.document_ids
            )
            message = f"Đã xóa knowledge của {deleted_count} documents"
        else:
            # Xóa tất cả
            success = await rag_service.clear_user_knowledge(request.user_id)
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail="Không thể xóa knowledge"
                )
            message = f"Đã xóa toàn bộ knowledge của user {request.user_id}"
        
        return {"message": message, "success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi delete knowledge: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi server: {str(e)}"
        )


@router.get("/extraction-status/{document_id}")
async def get_extraction_status(
    document_id: int,
    mysql: MySQLClient = Depends(get_mysql_client)
):
    """
    Kiểm tra trạng thái extraction của document
    
    Args:
        document_id: ID của document
        mysql: MySQL client dependency
        
    Returns:
        Status information
    """
    try:
        # Lấy thông tin document
        doc_info = mysql.get_document_by_id(document_id)
        
        if not doc_info:
            raise HTTPException(
                status_code=404,
                detail=f"Document với ID {document_id} không tồn tại"
            )
        
        # Lấy số chunks từ vector store nếu status = ready
        chunks_count = 0
        if doc_info["status"] == "ready":
            chunks_count = await rag_service.get_document_chunks_count(
                document_id=document_id,
                user_id=doc_info["owner_id"]
            )
        
        return {
            "document_id": document_id,
            "status": doc_info["status"],
            "chunks_extracted": chunks_count,
            "original_name": doc_info["original_name"],
            "created_at": doc_info["created_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi get extraction status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi server: {str(e)}"
        )