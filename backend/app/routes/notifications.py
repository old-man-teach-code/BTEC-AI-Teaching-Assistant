from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from dependencies.deps import get_db
from schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationListResponse,
    NotificationRespondStatusUpdate,
    NotificationStatsResponse
)
from services.notification_service import (
    service_create_notification,
    service_get_all_notifications,
    service_get_notification,
    service_update_notification,
    service_delete_notification,
    service_update_respond_status_by_message,
    service_get_notification_stats
)
from models.notification import NotificationType

router = APIRouter()


@router.post("/", response_model=NotificationResponse, summary="Tạo thông báo mới")
def create_notification_endpoint(
    notification: NotificationCreate,
    db: Session = Depends(get_db)
):
    """
    Tạo thông báo mới với các loại:
    
    1. RESPOND: Thông báo cần phản hồi
       - event_id: null (bắt buộc)
       - scheduled_at: null (bắt buộc)
       
    2. EVENT: Thông báo sự kiện
       - event_id: ID của sự kiện (bắt buộc)
       - scheduled_at: null (bắt buộc)
       
    3. GENERAL: Thông báo chung có lập lịch
       - event_id: null (bắt buộc)
       - scheduled_at: thời gian tương lai (bắt buộc)
    
    Example:
    ```json
    {
      "notification_type": "respond",
      "title": "Thông báo cần phản hồi",
      "message": "Vui lòng xác nhận tham gia",
      "user_id": 1,
      "event_id": null,
      "scheduled_at": null
    }
    ```
    """
    return service_create_notification(db, notification)


@router.get("/", response_model=NotificationListResponse, summary="Lấy tất cả thông báo")
def get_all_notifications_endpoint(
    skip: int = Query(0, ge=0, description="Số lượng bỏ qua"),
    limit: int = Query(100, ge=1, le=1000, description="Số lượng tối đa"),
    user_id: Optional[int] = Query(None, gt=0, description="Lọc theo user ID"),
    notification_type: Optional[NotificationType] = Query(None, description="Lọc theo loại thông báo (respond/event/general)"),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách tất cả thông báo với các bộ lọc:
    - user_id: Lọc theo người dùng
    - notification_type: Lọc theo loại thông báo
      - "respond": Thông báo cần phản hồi
      - "event": Thông báo sự kiện  
      - "general": Thông báo chung có lập lịch
    """
    return service_get_all_notifications(
        db, skip, limit, user_id, notification_type
    )


@router.get("/{notification_id}", response_model=NotificationResponse, summary="Lấy thông báo theo ID")
def get_notification_endpoint(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Lấy thông tin chi tiết của một thông báo"""
    return service_get_notification(db, notification_id)


@router.put("/{notification_id}", response_model=NotificationResponse, summary="Cập nhật thông báo")
def update_notification_endpoint(
    notification_id: int,
    notification_update: NotificationUpdate,
    db: Session = Depends(get_db)
):
    """Cập nhật thông tin thông báo"""
    return service_update_notification(db, notification_id, notification_update)


@router.delete("/{notification_id}", summary="Xóa thông báo")
def delete_notification_endpoint(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Xóa một thông báo"""
    return service_delete_notification(db, notification_id)


@router.patch("/respond-status", summary="Cập nhật trạng thái RESPOND theo message")
def update_respond_status_by_message_endpoint(
    status_update: NotificationRespondStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Cập nhật trạng thái phản hồi cho tất cả thông báo RESPOND có cùng message
    Dành riêng cho loại RESPOND
    """
    return service_update_respond_status_by_message(
        db, status_update.message, status_update.respond_status
    )


@router.get("/stats/{user_id}", response_model=NotificationStatsResponse, summary="Thống kê thông báo")
def get_notification_stats_endpoint(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Lấy thống kê thông báo của user"""
    return service_get_notification_stats(db, user_id)
