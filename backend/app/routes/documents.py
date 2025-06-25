from fastapi import APIRouter, Depends, UploadFile, File, Query, Path, HTTPException, status, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
import os

from dependencies.deps import get_db, get_current_user
from schemas.document import DocumentResponse, DocumentListResponse, DocumentUpdate
from services.document_service import (
    service_upload_document,
    service_get_user_documents,
    service_get_document,
    service_update_document,
    service_delete_document,
    service_download_document
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách documents của user hiện tại
    
    Args:
        skip: Số records bỏ qua (phân trang)
        limit: Số records tối đa trả về
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        DocumentListResponse: Danh sách documents và metadata
    """
    return service_get_user_documents(db, current_user.id, skip, limit)


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