from fastapi import APIRouter, Depends, UploadFile, File, Query, Path, HTTPException, status, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import os

from dependencies.deps import get_db, get_current_user
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