from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional

from dependencies.deps import get_db, get_current_user
from models.user import User
from schemas.folder import (
    FolderCreate, FolderUpdate, FolderResponse, FolderListResponse,
    FolderTreeResponse, FolderMove, FolderTrashResponse
)
from services.folder_service import (
    service_create_folder, service_get_user_folders, service_get_folder_tree,
    service_get_folder_details, service_update_folder, service_delete_folder,
    service_restore_folder, service_move_folder, service_cleanup_expired_folders,
    service_get_user_trash_folders
)

router = APIRouter()


@router.post("/", response_model=dict)
def create_folder(
    folder_data: FolderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Tạo folder mới
    
    Args:
        folder_data: Dữ liệu folder cần tạo
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        Dict: Thông tin folder vừa tạo
    """
    return service_create_folder(db, folder_data, current_user.id)


@router.get("/", response_model=FolderListResponse)
def get_folders(
    skip: int = Query(0, ge=0, description="Số lượng records bỏ qua"),
    limit: int = Query(100, ge=1, le=1000, description="Số lượng records lấy tối đa"),
    parent_id: Optional[int] = Query(None, description="ID của parent folder (None = root level)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách folders của user hiện tại
    
    Args:
        skip: Số records bỏ qua (phân trang)
        limit: Số records tối đa trả về
        parent_id: ID của parent folder
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        FolderListResponse: Danh sách folders với metadata
    """
    return service_get_user_folders(db, current_user.id, skip, limit, parent_id)


@router.get("/tree", response_model=FolderTreeResponse)
def get_folder_tree(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy cây thư mục của user hiện tại
    
    Args:
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        FolderTreeResponse: Cây thư mục
    """
    return service_get_folder_tree(db, current_user.id)


@router.get("/trash", response_model=FolderTrashResponse)
def get_trash_folders(
    skip: int = Query(0, ge=0, description="Số lượng records bỏ qua"),
    limit: int = Query(100, ge=1, le=1000, description="Số lượng records lấy tối đa"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách folders trong trash của user hiện tại

    Args:
        skip: Số records bỏ qua (phân trang)
        limit: Số records tối đa trả về
        db: Database session
        current_user: User hiện tại (từ token)

    Returns:
        FolderTrashResponse: Danh sách folders trong trash
    """
    return service_get_user_trash_folders(db, current_user.id, skip, limit)


@router.get("/{folder_id}", response_model=FolderResponse)
def get_folder_details(
    folder_id: int = Path(..., description="ID của folder"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy chi tiết folder
    
    Args:
        folder_id: ID của folder
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        FolderResponse: Chi tiết folder
    """
    return service_get_folder_details(db, folder_id, current_user.id)


@router.put("/{folder_id}", response_model=dict)
def update_folder(
    folder_id: int = Path(..., description="ID của folder cần cập nhật"),
    folder_update: FolderUpdate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cập nhật thông tin folder
    
    Args:
        folder_id: ID của folder cần cập nhật
        folder_update: Dữ liệu cập nhật
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        Dict: Kết quả cập nhật
    """
    return service_update_folder(db, folder_id, folder_update, current_user.id)


@router.delete("/{folder_id}")
def delete_folder(
    folder_id: int = Path(..., description="ID của folder cần xóa"),
    hard_delete: bool = Query(False, description="True = xóa vĩnh viễn, False = chuyển vào trash"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Xóa folder (soft hoặc hard delete)
    
    Args:
        folder_id: ID của folder cần xóa
        hard_delete: True = xóa vĩnh viễn, False = chuyển vào trash
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        Dict: Kết quả xóa
    """
    return service_delete_folder(db, folder_id, current_user.id, hard_delete)


@router.post("/{folder_id}/restore")
def restore_folder(
    folder_id: int = Path(..., description="ID của folder cần khôi phục"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Khôi phục folder từ trash
    
    Args:
        folder_id: ID của folder cần khôi phục
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        Dict: Kết quả khôi phục
    """
    return service_restore_folder(db, folder_id, current_user.id)


@router.post("/{folder_id}/move")
def move_folder(
    folder_id: int = Path(..., description="ID của folder cần di chuyển"),
    move_data: FolderMove = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Di chuyển folder vào parent folder khác
    
    Args:
        folder_id: ID của folder cần di chuyển
        move_data: Thông tin di chuyển
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        Dict: Kết quả di chuyển
    """
    return service_move_folder(db, folder_id, move_data, current_user.id)


@router.post("/trash/cleanup")
def cleanup_expired_folders(
    days: int = Query(30, ge=1, le=365, description="Số ngày hết hạn"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Tự động xóa cứng các folders đã hết hạn trong trash
    
    Args:
        days: Số ngày hết hạn (mặc định 30 ngày)
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        Dict: Kết quả cleanup
        
    Note: Chỉ admin hoặc user có quyền mới có thể thực hiện cleanup
    """
    # TODO: Thêm kiểm tra quyền admin nếu cần
    return service_cleanup_expired_folders(db, days)
