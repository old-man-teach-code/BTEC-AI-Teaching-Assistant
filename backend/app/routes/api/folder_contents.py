from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional, List
from enum import Enum

from dependencies.deps import get_db, get_current_user
from models.user import User
from schemas.folder import FolderContentResponse, FolderContentItem
from services.folder_content_service import service_get_folder_contents

router = APIRouter()

class SortBy(str, Enum):
    """Enum cho các loại sorting"""
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    SIZE_ASC = "size_asc" 
    SIZE_DESC = "size_desc"
    DATE_ASC = "date_asc"
    DATE_DESC = "date_desc"
    TYPE_ASC = "type_asc"
    TYPE_DESC = "type_desc"

class FilterBy(str, Enum):
    """Enum cho các loại filter"""
    ALL = "all"
    FOLDER = "folder"
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    XLSX = "xlsx"
    IMAGE = "image"


@router.get("/contents", response_model=FolderContentResponse)
def get_folder_contents(
    folder_id: Optional[int] = Query(None, description="ID của folder (None = root level)"),
    skip: int = Query(0, ge=0, description="Số lượng records bỏ qua"),
    limit: int = Query(100, ge=1, le=1000, description="Số lượng records lấy tối đa"),
    sort_by: SortBy = Query(SortBy.DATE_DESC, description="Sắp xếp theo"),
    filter_by: FilterBy = Query(FilterBy.ALL, description="Lọc theo loại"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy nội dung folder (bao gồm subfolders và documents) với sorting và filtering
    
    Args:
        folder_id: ID của folder (None = root level)
        skip: Số records bỏ qua (phân trang)
        limit: Số records tối đa trả về
        sort_by: Sắp xếp theo (name, size, date, type)
        filter_by: Lọc theo loại (all, folder, pdf, docx, etc.)
        search: Tìm kiếm theo tên
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        FolderContentResponse: Nội dung folder với metadata
    """
    return service_get_folder_contents(
        db=db,
        owner_id=current_user.id,
        folder_id=folder_id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        filter_by=filter_by,
        search=search
    )


@router.get("/contents", response_model=FolderContentResponse)
def get_root_contents(
    skip: int = Query(0, ge=0, description="Số lượng records bỏ qua"),
    limit: int = Query(100, ge=1, le=1000, description="Số lượng records lấy tối đa"),
    sort_by: SortBy = Query(SortBy.DATE_DESC, description="Sắp xếp theo"),
    filter_by: FilterBy = Query(FilterBy.ALL, description="Lọc theo loại"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy nội dung root level (folders và documents không thuộc folder nào)
    
    Args:
        skip: Số records bỏ qua (phân trang)
        limit: Số records tối đa trả về
        sort_by: Sắp xếp theo (name, size, date, type)
        filter_by: Lọc theo loại (all, folder, pdf, docx, etc.)
        search: Tìm kiếm theo tên
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        FolderContentResponse: Nội dung root level với metadata
    """
    return service_get_folder_contents(
        db=db,
        owner_id=current_user.id,
        folder_id=None,  # Root level
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        filter_by=filter_by,
        search=search
    )