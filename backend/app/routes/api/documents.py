from fastapi import APIRouter, Depends, UploadFile, File, Query, Path, HTTPException, status, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import os
import shutil

from dependencies.deps import get_db, get_current_user
from cache.redis_client import redis_client
from schemas.document import (
    DocumentResponse, DocumentListResponse, DocumentUpdate,
    DocumentTrashResponse, DocumentRestoreRequest
)
from schemas.folder import DocumentMove
from services.document_service import (
    service_upload_document,
    service_get_user_documents,
    service_get_document,
    service_update_document,
    service_delete_document,
    service_download_document,
    service_download_latest_document,
    service_process_document,
    service_get_user_trash_documents,
    service_restore_document,
    service_cleanup_expired_documents,
    service_move_document_to_folder
)
from models.user import User

# Khởi tạo router với prefix mặc định
router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload file document mới
    
    Args:
        file: File cần upload
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        DocumentResponse: Thông tin document đã upload
    """
    return await service_upload_document(db, file, current_user.id)


@router.get("/", response_model=DocumentListResponse)
def get_documents(
    skip: int = Query(0, ge=0, description="Số lượng records bỏ qua"),
    limit: int = Query(100, ge=1, le=1000, description="Số lượng records lấy tối đa"),
    folder_id: Optional[int] = Query(None, description="Lọc theo folder (None = root level)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách documents của user hiện tại

    Args:
        skip: Số records bỏ qua (phân trang)
        limit: Số records tối đa trả về
        folder_id: Lọc theo folder (None = root level)
        db: Database session
        current_user: User hiện tại (từ token)

    Returns:
        DocumentListResponse: Danh sách documents và metadata
    """
    return service_get_user_documents(db, current_user.id, skip, limit, folder_id)


# ========== TRASH SYSTEM ENDPOINTS ==========
# Note: These routes must be defined before /{document_id} to avoid path conflicts

@router.get("/trash", response_model=DocumentTrashResponse)
def get_trash_documents(
    skip: int = Query(0, ge=0, description="Số lượng records bỏ qua"),
    limit: int = Query(100, ge=1, le=1000, description="Số lượng records lấy tối đa"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách documents trong trash của user hiện tại

    Args:
        skip: Số records bỏ qua (phân trang)
        limit: Số records tối đa trả về
        db: Database session
        current_user: User hiện tại (từ token)

    Returns:
        DocumentTrashResponse: Danh sách documents trong trash
    """
    return service_get_user_trash_documents(db, current_user.id, skip, limit)


@router.post("/trash/cleanup")
def cleanup_expired_documents(
    days: int = Query(30, ge=1, le=365, description="Số ngày hết hạn"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Tự động xóa cứng các documents đã hết hạn trong trash

    Args:
        days: Số ngày hết hạn (mặc định 30 ngày)
        db: Database session
        current_user: User hiện tại (từ token)

    Returns:
        Dict: Kết quả cleanup

    Note: Chỉ admin hoặc user có quyền mới có thể thực hiện cleanup
    """
    # TODO: Thêm kiểm tra quyền admin nếu cần
    return service_cleanup_expired_documents(db, days)


@router.post("/{document_id}/restore")
def restore_document(
    document_id: int = Path(..., description="ID của document cần khôi phục"),
    restore_request: DocumentRestoreRequest = DocumentRestoreRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Khôi phục document từ trash

    Args:
        document_id: ID của document cần khôi phục
        restore_request: Thông tin khôi phục (folder đích)
        db: Database session
        current_user: User hiện tại (từ token)

    Returns:
        Dict: Kết quả khôi phục document
    """
    return service_restore_document(db, document_id, current_user.id, restore_request)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int = Path(..., gt=0, description="ID của document cần lấy"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy thông tin chi tiết một document
    
    Args:
        document_id: ID của document
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        DocumentResponse: Thông tin document
    """
    return service_get_document(db, document_id, current_user.id)


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_update: DocumentUpdate,
    document_id: int = Path(..., gt=0, description="ID của document cần cập nhật"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cập nhật thông tin document
    
    Args:
        document_update: Dữ liệu cập nhật
        document_id: ID của document
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        DocumentResponse: Thông tin document sau khi cập nhật
    """
    return service_update_document(db, document_id, document_update, current_user.id)


@router.delete("/{document_id}")
def delete_document(
    document_id: int = Path(..., gt=0, description="ID của document cần xóa"),
    hard_delete: bool = Query(False, description="Nếu True sẽ xóa cứng, ngược lại là xóa mềm"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Xóa document (mặc định là soft delete)
    
    Args:
        document_id: ID của document
        hard_delete: Nếu True sẽ xóa cứng, ngược lại là xóa mềm
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        Dict: Thông báo kết quả
    """
    return service_delete_document(db, document_id, current_user.id, hard_delete)


@router.get("/latest/download")
def download_latest_document(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download file document mới nhất theo created_at
    Tránh tải xuống file trùng lặp bằng cách kiểm tra cache
    
    Args:
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        FileResponse: File mới nhất để download hoặc False nếu file trùng lặp
    """
    try:
        # Lấy thông tin file mới nhất cần download
        file_info = service_download_latest_document(db, current_user.id)
        
        # Tạo cache key cho user hiện tại
        cache_key = f"last_downloaded_file:user_{current_user.id}"
        
        # Thử lấy tên file đã tải xuống gần nhất từ cache
        try:
            last_downloaded_filename = redis_client.get(cache_key)
        except Exception as e:
            print(f"Redis error: {e}")
            last_downloaded_filename = None
        
        # Kiểm tra nếu file hiện tại trùng với file đã tải xuống gần nhất
        current_filename = file_info["filename"]
        if last_downloaded_filename == current_filename:
            # Trả về file response nếu là lần thứ 2 cùng file
            return FileResponse(
                path=file_info["file_path"],
                filename=file_info["filename"],
                media_type=file_info["content_type"]
            )
        
        # Thử lưu tên file hiện tại vào cache (TTL 5 giây)
        try:
            redis_client.setex(cache_key, 5, current_filename)
        except Exception as e:
            print(f"Redis error when saving: {e}")
        
        # Trả về response với status false nếu là lần đầu
        return {
            "success": False,
            "message": "File này đã được tải xuống gần nhất, không có file mới",
            "filename": current_filename
        }
    except Exception as e:
        print(f"Error in download_latest_document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi server: {str(e)}"
        )


@router.delete("/latest/download/cache")
def clear_download_cache(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Quản lý lưu trữ file: lưu file mới hoặc xóa file trùng lặp
    
    Args:
        current_user: User hiện tại (từ token)
        db: Database session
        
    Returns:
        Dict: Thông báo kết quả
    """
    try:
        # Lấy thông tin file mới nhất
        file_info = service_download_latest_document(db, current_user.id)
        current_filename = file_info["filename"]
        
        # Tạo thư mục lưu trữ cho user nếu chưa có
        storage_dir = f"uploads/user_{current_user.id}_storage"
        os.makedirs(storage_dir, exist_ok=True)
        
        # Đường dẫn file trong thư mục lưu trữ
        stored_file_path = os.path.join(storage_dir, current_filename)
        
        # Kiểm tra nếu file đã tồn tại trong thư mục lưu trữ
        if os.path.exists(stored_file_path):
            # File đã tồn tại → không lưu nữa, trả về thông báo đã tồn tại
            return {
                "success": False,
                "action": "already_exists",
                "message": f"File đã tồn tại trong storage: {current_filename}",
                "filename": current_filename,
                "storage_path": stored_file_path
            }
        else:
            # File chưa tồn tại → sao chép file vào thư mục lưu trữ
            shutil.copy2(file_info["file_path"], stored_file_path)
            
            return {
                "success": True,
                "action": "stored",
                "message": f"Đã lưu file mới vào storage: {current_filename}",
                "filename": current_filename,
                "storage_path": stored_file_path
            }
            
    except Exception as e:
        print(f"Error in clear_download_cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi server: {str(e)}"
        )


@router.get("/{document_id}/download")
def download_document(
    document_id: int = Path(..., gt=0, description="ID của document cần download"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download file document
    
    Args:
        document_id: ID của document
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        FileResponse: File để download
    """
    # Lấy thông tin file cần download
    file_info = service_download_document(db, document_id, current_user.id)
    
    # Trả về file response
    return FileResponse(
        path=file_info["file_path"],
        filename=file_info["filename"],
        media_type=file_info["content_type"]
    ) 


@router.post("/{document_id}/process")
def process_document(
    document_id: int = Path(..., gt=0, description="ID của document cần xử lý"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Gửi document sang AI để xử lý

    Args:
        document_id: ID của document cần xử lý
        db: Database session
        current_user: User hiện tại (từ token)

    Returns:
        Dict: Kết quả xử lý document
    """
    return service_process_document(db, document_id, current_user.id)


# Duplicate trash endpoints removed - they are now defined earlier in the file


# ========== FOLDER SYSTEM ENDPOINTS ==========

@router.post("/{document_id}/move")
def move_document_to_folder(
    document_id: int = Path(..., description="ID của document cần di chuyển"),
    move_data: DocumentMove = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Di chuyển document vào folder khác

    Args:
        document_id: ID của document cần di chuyển
        move_data: Thông tin di chuyển (folder đích)
        db: Database session
        current_user: User hiện tại (từ token)

    Returns:
        Dict: Kết quả di chuyển document
    """
    return service_move_document_to_folder(db, document_id, current_user.id, move_data.folder_id)