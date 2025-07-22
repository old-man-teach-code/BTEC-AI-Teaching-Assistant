from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any, Tuple
import os
import uuid
from datetime import datetime
import requests

from models.document import Document, DocumentStatus
from schemas.document import DocumentCreate, DocumentUpdate, DocumentListResponse, DocumentResponse
from crud.document import (
    create_document, 
    get_document, 
    get_user_documents,
    get_total_user_documents,
    update_document,
    soft_delete_document,
    delete_document
)
from utils.file_handler import save_file, get_file_extension, get_file_size, validate_file
from core.config import settings


def _validate_document_access(db: Session, document_id: int, owner_id: int, action_name: str = "truy cập") -> Document:
    """
    Kiểm tra document tồn tại và quyền sở hữu
    
    Args:
        db: Database session
        document_id: ID của document cần kiểm tra
        owner_id: ID của user để kiểm tra quyền sở hữu
        action_name: Tên hành động để hiển thị trong thông báo lỗi
        
    Returns:
        Document: Document đã được kiểm tra
        
    Raises:
        HTTPException: Nếu document không tồn tại hoặc user không có quyền
    """
    # Lấy document từ database
    document = get_document(db, document_id)
    
    # Kiểm tra document tồn tại
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document với ID {document_id} không tồn tại"
        )
    
    # Kiểm tra quyền sở hữu
    if document.owner_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Bạn không có quyền {action_name} document này"
        )
    
    return document


async def service_upload_document(
    db: Session, 
    file: UploadFile, 
    owner_id: int
) -> DocumentResponse:
    """
    Service xử lý upload document
    
    Args:
        db: Database session
        file: File được upload
        owner_id: ID người dùng upload
    
    Returns:
        DocumentResponse: Thông tin document đã tạo
        
    Raises:
        HTTPException: Nếu có lỗi khi upload
    """
    # Kiểm tra tính hợp lệ của file
    error_message = validate_file(file)
    if error_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    try:
        # Lưu file và lấy đường dẫn trả về
        file_path = save_file(file, owner_id)
        
        # Lấy thông tin file để lưu vào DB
        file_size = get_file_size(file)
        filename = os.path.basename(file_path)
        
        # Tạo document data
        document_data = {
            "filename": filename,
            "original_name": file.filename,
            "file_path": file_path,
            "file_size": file_size,
            "file_type": file.content_type,
            "status": DocumentStatus.UPLOADED.value
        }
        
        # Lưu vào database
        db_document = create_document(db, document_data, owner_id)
        
        # Trả về thông tin document đã tạo
        return DocumentResponse.from_orm(db_document)
        
    except Exception as e:
        # Nếu có lỗi, xử lý và ném exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi upload file: {str(e)}"
        )


def service_get_user_documents(
    db: Session, 
    owner_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> DocumentListResponse:
    """
    Lấy danh sách documents của user
    
    Args:
        db: Database session
        owner_id: ID của user
        skip: Số lượng records bỏ qua (phân trang)
        limit: Số lượng records lấy tối đa
        
    Returns:
        DocumentListResponse: Danh sách documents và metadata
    """
    # Lấy tổng số documents của user
    total = get_total_user_documents(db, owner_id)
    
    # Lấy danh sách documents theo phân trang
    documents = get_user_documents(db, owner_id, skip, limit)
    
    # Trả về kết quả
    return DocumentListResponse(
        total=total,
        items=[DocumentResponse.from_orm(doc) for doc in documents]
    )


def service_get_document(db: Session, document_id: int, owner_id: int) -> DocumentResponse:
    """
    Lấy thông tin chi tiết về một document
    
    Args:
        db: Database session
        document_id: ID của document cần lấy
        owner_id: ID của user để kiểm tra quyền sở hữu
        
    Returns:
        DocumentResponse: Thông tin document
        
    Raises:
        HTTPException: Nếu document không tồn tại hoặc user không có quyền
    """
    # Kiểm tra document và quyền truy cập
    document = _validate_document_access(db, document_id, owner_id)
    
    # Trả về thông tin document
    return DocumentResponse.from_orm(document)


def service_update_document(
    db: Session, 
    document_id: int, 
    document_update: DocumentUpdate, 
    owner_id: int
) -> DocumentResponse:
    """
    Cập nhật thông tin document
    
    Args:
        db: Database session
        document_id: ID của document cần cập nhật
        document_update: Dữ liệu cập nhật
        owner_id: ID của user để kiểm tra quyền sở hữu
        
    Returns:
        DocumentResponse: Thông tin document sau cập nhật
        
    Raises:
        HTTPException: Nếu document không tồn tại hoặc user không có quyền
    """
    # Kiểm tra document và quyền truy cập
    document = _validate_document_access(db, document_id, owner_id, "cập nhật")
    
    # Cập nhật document
    updated_document = update_document(db, document, document_update)
    
    # Trả về document đã cập nhật
    return DocumentResponse.from_orm(updated_document)


def service_delete_document(db: Session, document_id: int, owner_id: int, hard_delete: bool = False) -> Dict[str, Any]:
    """
    Xóa document (mềm hoặc cứng)
    
    Args:
        db: Database session
        document_id: ID của document cần xóa
        owner_id: ID của user để kiểm tra quyền sở hữu
        hard_delete: Nếu True sẽ xóa cứng, ngược lại là xóa mềm
        
    Returns:
        Dict: Kết quả xóa document
        
    Raises:
        HTTPException: Nếu document không tồn tại hoặc user không có quyền
    """
    # Kiểm tra document và quyền truy cập
    document = _validate_document_access(db, document_id, owner_id, "xóa")
    
    if hard_delete:
        # Xóa cứng document khỏi database
        delete_document(db, document)
        # Có thể thêm logic xóa file khỏi storage ở đây
        return {"message": f"Document {document_id} đã được xóa vĩnh viễn"}
    else:
        # Xóa mềm document
        soft_delete_document(db, document)
        return {"message": f"Document {document_id} đã được đánh dấu là đã xóa"}


def service_download_document(db: Session, document_id: int, owner_id: int) -> Dict[str, Any]:
    """
    Lấy thông tin file để download document
    
    Args:
        db: Database session
        document_id: ID của document cần download
        owner_id: ID của user để kiểm tra quyền sở hữu
        
    Returns:
        Dict: Thông tin file để download
        
    Raises:
        HTTPException: Nếu document không tồn tại hoặc user không có quyền
    """
    # Kiểm tra document và quyền truy cập
    document = _validate_document_access(db, document_id, owner_id, "download")
    
    # Kiểm tra file có tồn tại không
    file_path = document.file_path
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File không tồn tại trên server"
        )
    
    # Trả về thông tin file để download
    return {
        "file_path": file_path,
        "filename": document.original_name,
        "content_type": document.file_type
    } 


def service_process_document(db: Session, document_id: int, owner_id: int) -> Dict[str, Any]:
    """
    Gửi document sang AI để xử lý
    
    Args:
        db: Database session
        document_id: ID của document cần xử lý
        owner_id: ID của user để kiểm tra quyền sở hữu
        
    Returns:
        Dict: Kết quả xử lý document
        
    Raises:
        HTTPException: Nếu document không tồn tại hoặc user không có quyền
    """
    # Kiểm tra document và quyền truy cập
    document = _validate_document_access(db, document_id, owner_id, "xử lý")
    
    # Kiểm tra trạng thái hiện tại
    if document.status == DocumentStatus.READY.value:
        return {
            "message": f"Document {document_id} đã được xử lý trước đó",
            "status": document.status
        }
    
    # Cập nhật trạng thái document sang processing
    document_update = DocumentUpdate(status=DocumentStatus.PROCESSING.value)
    updated_document = update_document(db, document, document_update)
    
    # TODO: Gọi API sang AI để xử lý document
    # Trong thực tế, đây là nơi sẽ gọi API sang AI service
    
    # Trả về kết quả 
    return {
        "id": document_id,
        "status": "processing",
        "message": f"Document {document_id} đang được xử lý"
    } 