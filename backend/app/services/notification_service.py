from sqlalchemy.orm import Session
from crud.notification import (
    create_notification,
    get_notification,
    get_user_notifications,
    update_notification,
    update_notification_status,
    mark_notifications_as_read,
    delete_notification,
    get_user_notification_stats,
    get_unread_count,
    get_notifications_by_event
)
from schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationStatusUpdate,
    NotificationResponse,
    NotificationListResponse,
    NotificationStatsResponse
)
from models.notification import NotificationStatus, NotificationCategory
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime


def service_create_notification(
    db: Session, 
    notification_data: NotificationCreate
) -> NotificationResponse:
    """
    Service tạo notification mới
    
    Args:
        db: Database session
        notification_data: Dữ liệu notification cần tạo
        
    Returns:
        NotificationResponse: Thông tin notification đã tạo
        
    Raises:
        HTTPException 400: Nếu dữ liệu không hợp lệ
        HTTPException 404: Nếu user hoặc event không tồn tại
    """
    try:
        # Kiểm tra user tồn tại
        from crud.user import get_user
        user = get_user(db, notification_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Kiểm tra event tồn tại (nếu có)
        if notification_data.event_id:
            from crud.event import get_event
            event = get_event(db, notification_data.event_id)
            if not event:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Event not found"
                )
        
        # Tạo notification
        db_notification = create_notification(db, notification_data)
        return NotificationResponse.from_orm(db_notification)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating notification: {str(e)}"
        )


def service_get_user_notifications(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[NotificationStatus] = None,
    category_filter: Optional[NotificationCategory] = None,
    unread_only: bool = False
) -> NotificationListResponse:
    """
    Service lấy danh sách notifications của user
    
    Args:
        db: Database session
        user_id: ID của user
        skip: Số lượng records bỏ qua
        limit: Số lượng records lấy tối đa
        status_filter: Lọc theo trạng thái
        category_filter: Lọc theo danh mục
        unread_only: Chỉ lấy notifications chưa đọc
        
    Returns:
        NotificationListResponse: Danh sách notifications kèm metadata
    """
    try:
        notifications, total = get_user_notifications(
            db, user_id, skip, limit, status_filter, category_filter, unread_only
        )
        
        # Đếm số notifications chưa đọc
        unread_count = get_unread_count(db, user_id)
        
        return NotificationListResponse(
            total=total,
            unread_count=unread_count,
            items=[NotificationResponse.from_orm(notif) for notif in notifications]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error fetching notifications: {str(e)}"
        )


def service_get_notification(db: Session, notification_id: int, user_id: int) -> NotificationResponse:
    """
    Service lấy thông tin chi tiết notification
    
    Args:
        db: Database session
        notification_id: ID của notification
        user_id: ID của user (để kiểm tra quyền)
        
    Returns:
        NotificationResponse: Thông tin notification
        
    Raises:
        HTTPException 404: Nếu notification không tồn tại
        HTTPException 403: Nếu user không có quyền truy cập
    """
    db_notification = get_notification(db, notification_id)
    
    if not db_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Kiểm tra quyền truy cập
    if db_notification.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return NotificationResponse.from_orm(db_notification)


def service_update_notification(
    db: Session,
    notification_id: int,
    notification_update: NotificationUpdate,
    user_id: int
) -> NotificationResponse:
    """
    Service cập nhật notification
    
    Args:
        db: Database session
        notification_id: ID của notification
        notification_update: Dữ liệu cập nhật
        user_id: ID của user (để kiểm tra quyền)
        
    Returns:
        NotificationResponse: Notification đã cập nhật
        
    Raises:
        HTTPException 404: Nếu notification không tồn tại
        HTTPException 403: Nếu user không có quyền
    """
    # Kiểm tra notification tồn tại và quyền truy cập
    db_notification = get_notification(db, notification_id)
    
    if not db_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    if db_notification.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Cập nhật notification
    updated_notification = update_notification(db, notification_id, notification_update)
    
    if not updated_notification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error updating notification"
        )
    
    return NotificationResponse.from_orm(updated_notification)


def service_update_notification_status(
    db: Session,
    notification_id: int,
    status_update: NotificationStatusUpdate,
    user_id: int
) -> NotificationResponse:
    """
    Service cập nhật trạng thái notification
    
    Args:
        db: Database session
        notification_id: ID của notification
        status_update: Trạng thái mới
        user_id: ID của user (để kiểm tra quyền)
        
    Returns:
        NotificationResponse: Notification đã cập nhật
        
    Raises:
        HTTPException 404: Nếu notification không tồn tại
        HTTPException 403: Nếu user không có quyền
    """
    # Kiểm tra notification tồn tại và quyền truy cập
    db_notification = get_notification(db, notification_id)
    
    if not db_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    if db_notification.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Cập nhật trạng thái
    updated_notification = update_notification_status(db, notification_id, status_update)
    
    if not updated_notification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error updating notification status"
        )
    
    return NotificationResponse.from_orm(updated_notification)


def service_mark_notifications_as_read(
    db: Session,
    notification_ids: List[int],
    user_id: int
) -> dict:
    """
    Service đánh dấu nhiều notifications là đã đọc
    
    Args:
        db: Database session
        notification_ids: Danh sách ID notifications
        user_id: ID của user
        
    Returns:
        dict: Thông tin về số notifications đã cập nhật
    """
    try:
        updated_count = mark_notifications_as_read(db, notification_ids, user_id)
        
        return {
            "message": f"Marked {updated_count} notifications as read",
            "updated_count": updated_count,
            "requested_count": len(notification_ids)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error marking notifications as read: {str(e)}"
        )


def service_delete_notification(db: Session, notification_id: int, user_id: int) -> dict:
    """
    Service xóa notification
    
    Args:
        db: Database session
        notification_id: ID của notification
        user_id: ID của user (để kiểm tra quyền)
        
    Returns:
        dict: Thông báo xóa thành công
        
    Raises:
        HTTPException 404: Nếu notification không tồn tại
        HTTPException 403: Nếu user không có quyền
    """
    # Kiểm tra notification tồn tại và quyền truy cập
    db_notification = get_notification(db, notification_id)
    
    if not db_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    if db_notification.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Xóa notification
    success = delete_notification(db, notification_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error deleting notification"
        )
    
    return {"message": "Notification deleted successfully"}


def service_get_notification_stats(db: Session, user_id: int) -> NotificationStatsResponse:
    """
    Service lấy thống kê notifications của user
    
    Args:
        db: Database session
        user_id: ID của user
        
    Returns:
        NotificationStatsResponse: Thống kê notifications
    """
    try:
        stats = get_user_notification_stats(db, user_id)
        return NotificationStatsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error fetching notification stats: {str(e)}"
        )


def service_create_event_notification(
    db: Session,
    user_id: int,
    event_id: int,
    title: str,
    message: str,
    category: NotificationCategory = NotificationCategory.EVENT_REMINDER
) -> NotificationResponse:
    """
    Service tạo notification liên quan đến event
    
    Args:
        db: Database session
        user_id: ID của user nhận notification
        event_id: ID của event liên quan
        title: Tiêu đề notification
        message: Nội dung notification
        category: Danh mục notification
        
    Returns:
        NotificationResponse: Notification đã tạo
    """
    notification_data = NotificationCreate(
        title=title,
        category=category,
        message=message,
        user_id=user_id,
        event_id=event_id
    )
    
    return service_create_notification(db, notification_data)
