from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from models.notification import (
    Notification,
    NotificationType,
    NotificationEventStatus,
    NotificationRespondStatus,
    NotificationGeneralStatus
)
from schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationListResponse,
    NotificationRespondStatusUpdate,
    NotificationStatsResponse
)
from crud.notification import (
    create_notification,
    get_notification,
    get_all_notifications,
    get_notifications_by_user,
    update_notification,
    update_respond_notification_status_by_message,
    delete_notification,
    get_notifications_stats
)


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
        HTTPException: Nếu có lỗi validation hoặc tạo notification
    """
    try:
        # Validate business rules
        if notification_data.notification_type == NotificationType.EVENT and not notification_data.event_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="event_id is required for EVENT notifications"
            )
        
        if notification_data.notification_type != NotificationType.EVENT and notification_data.event_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="event_id should only be set for EVENT notifications"
            )
        
        if notification_data.notification_type == NotificationType.GENERAL and notification_data.scheduled_at:
            # Xử lý so sánh datetime với timezone
            if notification_data.scheduled_at.tzinfo is not None:
                # scheduled_at có timezone, convert datetime.now() sang UTC
                current_time = datetime.now(timezone.utc)
            else:
                # scheduled_at không có timezone, dùng datetime.now() local
                current_time = datetime.now()
                
            if notification_data.scheduled_at <= current_time:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="scheduled_at must be in the future for GENERAL notifications"
                )
        
        # Tạo notification
        db_notification = create_notification(db, notification_data)
        
        return NotificationResponse.from_orm(db_notification)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể tạo notification: {str(e)}"
        )


def service_get_all_notifications(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    notification_type: Optional[NotificationType] = None
) -> NotificationListResponse:
    """
    Service lấy danh sách notifications
    
    Args:
        db: Database session
        skip: Số lượng records bỏ qua
        limit: Số lượng records lấy tối đa
        user_id: Lọc theo user ID
        notification_type: Lọc theo loại notification
        
    Returns:
        NotificationListResponse: Danh sách notifications
    """
    try:
        if user_id:
            notifications = get_notifications_by_user(
                db, user_id, skip, limit, notification_type
            )
        else:
            notifications = get_all_notifications(db, skip, limit)
        
        # Chuyển đổi sang response format
        notification_responses = [NotificationResponse.from_orm(notif) for notif in notifications]
        
        return NotificationListResponse(
            total=len(notification_responses),
            notifications=notification_responses
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể lấy danh sách notifications: {str(e)}"
        )


def service_get_notification(db: Session, notification_id: int) -> NotificationResponse:
    """
    Service lấy thông tin chi tiết một notification
    
    Args:
        db: Database session
        notification_id: ID của notification cần lấy
        
    Returns:
        NotificationResponse: Thông tin notification
        
    Raises:
        HTTPException: Nếu không tìm thấy notification
    """
    try:
        db_notification = get_notification(db, notification_id)
        
        if not db_notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy notification với ID {notification_id}"
            )
        
        return NotificationResponse.from_orm(db_notification)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể lấy thông tin notification: {str(e)}"
        )


def service_update_notification(
    db: Session,
    notification_id: int,
    notification_update: NotificationUpdate
) -> NotificationResponse:
    """
    Service cập nhật thông tin notification
    
    Args:
        db: Database session
        notification_id: ID của notification cần cập nhật
        notification_update: Dữ liệu cập nhật
        
    Returns:
        NotificationResponse: Thông tin notification đã cập nhật
        
    Raises:
        HTTPException: Nếu không tìm thấy notification
    """
    try:
        # Kiểm tra notification tồn tại
        db_notification = get_notification(db, notification_id)
        if not db_notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy notification với ID {notification_id}"
            )
        
        # Validate scheduled_at cho GENERAL notifications
        if (notification_update.scheduled_at is not None and 
            db_notification.notification_type == NotificationType.GENERAL):
            if notification_update.scheduled_at <= datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="scheduled_at must be in the future"
                )
        
        # Cập nhật notification
        updated_notification = update_notification(db, notification_id, notification_update)
        
        if not updated_notification:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Không thể cập nhật notification"
            )
        
        return NotificationResponse.from_orm(updated_notification)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể cập nhật notification: {str(e)}"
        )


def service_delete_notification(db: Session, notification_id: int) -> Dict[str, Any]:
    """
    Service xóa notification
    
    Args:
        db: Database session
        notification_id: ID của notification cần xóa
        
    Returns:
        Dict[str, Any]: Thông báo kết quả
        
    Raises:
        HTTPException: Nếu không tìm thấy notification
    """
    try:
        # Kiểm tra notification tồn tại
        db_notification = get_notification(db, notification_id)
        if not db_notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy notification với ID {notification_id}"
            )
        
        # Xóa notification
        success = delete_notification(db, notification_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Không thể xóa notification"
            )
        
        return {
            "message": f"Notification ID {notification_id} đã được xóa thành công",
            "notification_id": notification_id,
            "deleted_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể xóa notification: {str(e)}"
        )


def service_update_respond_status_by_message(
    db: Session,
    message: str,
    respond_status: NotificationRespondStatus
) -> Dict[str, Any]:
    """
    Service cập nhật trạng thái RESPOND theo message
    
    Args:
        db: Database session
        message: Nội dung message cần tìm
        respond_status: Trạng thái respond mới
        
    Returns:
        Dict[str, Any]: Thông tin cập nhật
        
    Raises:
        HTTPException: Nếu không tìm thấy notifications
    """
    try:
        updated_notifications = update_respond_notification_status_by_message(
            db, message, respond_status
        )
        
        if not updated_notifications:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy RESPOND notifications với message này"
            )
        
        # Chuyển đổi sang response format
        notification_responses = [NotificationResponse.from_orm(notif) for notif in updated_notifications]
        
        return {
            "message": f"Đã cập nhật {len(updated_notifications)} RESPOND notifications",
            "updated_count": len(updated_notifications),
            "notifications": notification_responses,
            "updated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể cập nhật trạng thái: {str(e)}"
        )


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
        stats = get_notifications_stats(db, user_id)
        return NotificationStatsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể lấy thống kê notifications: {str(e)}"
        )
