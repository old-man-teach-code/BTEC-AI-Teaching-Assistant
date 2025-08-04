from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from dependencies.deps import get_db, get_current_user
from schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationStatusUpdate,
    NotificationResponse,
    NotificationListResponse,
    NotificationMarkAsReadRequest,
    NotificationStatsResponse
)
from services.notification_service import (
    service_create_notification,
    service_get_user_notifications,
    service_get_notification,
    service_update_notification,
    service_update_notification_status,
    service_mark_notifications_as_read,
    service_delete_notification,
    service_get_notification_stats
)
from models.user import User
from models.notification import NotificationStatus, NotificationCategory

# Khởi tạo router
router = APIRouter()


@router.post("/", response_model=NotificationResponse)
def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db)
):
    """
    Tạo notification mới
    
    Args:
        notification_data: Dữ liệu notification cần tạo
        db: Database session
        
    Returns:
        NotificationResponse: Thông tin notification đã tạo
        
    Raises:
        HTTPException 400: Nếu dữ liệu không hợp lệ
        HTTPException 404: Nếu user hoặc event không tồn tại
    """
    return service_create_notification(db, notification_data)


@router.get("/", response_model=NotificationListResponse)
def get_notifications(
    user_id: int = Query(..., description="ID của user"),
    skip: int = Query(0, ge=0, description="Số lượng records bỏ qua"),
    limit: int = Query(100, ge=1, le=1000, description="Số lượng records lấy tối đa"),
    status: Optional[NotificationStatus] = Query(None, description="Lọc theo trạng thái"),
    category: Optional[NotificationCategory] = Query(None, description="Lọc theo danh mục"),
    unread_only: bool = Query(False, description="Chỉ lấy notifications chưa đọc"),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách notifications của user
    
    Args:
        user_id: ID của user
        skip: Số lượng records bỏ qua (cho phân trang)
        limit: Số lượng records lấy tối đa (cho phân trang)
        status: Lọc theo trạng thái
        category: Lọc theo danh mục
        unread_only: Chỉ lấy notifications chưa đọc
        db: Database session
        
    Returns:
        NotificationListResponse: Danh sách notifications kèm metadata phân trang
        
    Example:
        GET /notifications?user_id=1&status=unread&category=event_reminder&skip=0&limit=10
    """
    return service_get_user_notifications(
        db, user_id, skip, limit, status, category, unread_only
    )


@router.get("/stats", response_model=NotificationStatsResponse)
def get_notification_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy thống kê notifications của user hiện tại
    
    Args:
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        NotificationStatsResponse: Thống kê notifications
    """
    return service_get_notification_stats(db, current_user.id)


@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy số lượng notifications chưa đọc của user hiện tại
    
    Args:
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        dict: Số lượng notifications chưa đọc
    """
    from crud.notification import get_unread_count
    count = get_unread_count(db, current_user.id)
    
    return {"unread_count": count}


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int = Path(..., description="ID của notification"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy thông tin chi tiết notification
    
    Args:
        notification_id: ID của notification
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        NotificationResponse: Thông tin notification
        
    Raises:
        HTTPException 404: Nếu notification không tồn tại
        HTTPException 403: Nếu user không có quyền truy cập
    """
    return service_get_notification(db, notification_id, current_user.id)


@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification(
    notification_id: int = Path(..., description="ID của notification"),
    notification_update: NotificationUpdate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cập nhật notification
    
    Args:
        notification_id: ID của notification
        notification_update: Dữ liệu cập nhật
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        NotificationResponse: Notification đã cập nhật
        
    Raises:
        HTTPException 404: Nếu notification không tồn tại
        HTTPException 403: Nếu user không có quyền
    """
    return service_update_notification(db, notification_id, notification_update, current_user.id)


@router.patch("/{notification_id}/status", response_model=NotificationResponse)
def update_notification_status(
    notification_id: int = Path(..., description="ID của notification"),
    status_update: NotificationStatusUpdate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cập nhật trạng thái notification
    
    Args:
        notification_id: ID của notification
        status_update: Trạng thái mới
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        NotificationResponse: Notification đã cập nhật
        
    Raises:
        HTTPException 404: Nếu notification không tồn tại
        HTTPException 403: Nếu user không có quyền
    """
    return service_update_notification_status(db, notification_id, status_update, current_user.id)


@router.patch("/mark-as-read")
def mark_notifications_as_read(
    request: NotificationMarkAsReadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Đánh dấu nhiều notifications là đã đọc
    
    Args:
        request: Danh sách ID notifications cần đánh dấu
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        dict: Thông tin về số notifications đã cập nhật
    """
    return service_mark_notifications_as_read(db, request.notification_ids, current_user.id)


@router.patch("/mark-all-as-read")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Đánh dấu tất cả notifications chưa đọc của user là đã đọc
    
    Args:
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        dict: Thông tin về số notifications đã cập nhật
    """
    # Lấy tất cả notifications chưa đọc
    from crud.notification import get_user_notifications
    from models.notification import NotificationStatus
    
    unread_notifications, _ = get_user_notifications(
        db, current_user.id, 0, 1000, NotificationStatus.UNREAD
    )
    
    notification_ids = [notif.id for notif in unread_notifications]
    
    if not notification_ids:
        return {
            "message": "No unread notifications found",
            "updated_count": 0,
            "requested_count": 0
        }
    
    return service_mark_notifications_as_read(db, notification_ids, current_user.id)


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int = Path(..., description="ID của notification"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Xóa notification
    
    Args:
        notification_id: ID của notification
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        dict: Thông báo xóa thành công
        
    Raises:
        HTTPException 404: Nếu notification không tồn tại
        HTTPException 403: Nếu user không có quyền
    """
    return service_delete_notification(db, notification_id, current_user.id)
