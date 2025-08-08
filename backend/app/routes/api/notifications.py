from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from dependencies.deps import get_db, get_current_user
from models.user import User
from schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationListResponse,
    NotificationRespondStatusUpdate,
    NotificationGeneralStatusUpdate,
    NotificationStatsResponse
)
from services.notification_service import (
    service_create_notification,
    service_get_all_notifications,
    service_get_notification,
    service_update_notification,
    service_delete_notification,
    service_update_respond_status_by_message,
    service_update_general_status_by_message,
    service_get_notification_stats,
    service_get_notifications_by_type_and_status
)
from models.notification import (
    NotificationType,
    NotificationEventStatus,
    NotificationRespondStatus,
    NotificationGeneralStatus
)

router = APIRouter()


@router.post("/", response_model=NotificationResponse, summary="Tạo thông báo mới")
def create_notification_endpoint(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Tạo thông báo mới với các loại:
    
    1. RESPOND: Thông báo cần phản hồi
       - event_id: null (bắt buộc)
       - scheduled_at: null (bắt buộc)
       - Trạng thái tự động: event_status=unread, respond_status=pending_response
       
    2. EVENT: Thông báo sự kiện
       - event_id: ID của sự kiện (bắt buộc)
       - scheduled_at: null (bắt buộc)
       - Trạng thái tự động: event_status=unread

       
    3. GENERAL: Thông báo chung có lập lịch
       - event_id: null (bắt buộc)
       - scheduled_at: thời gian tương lai (bắt buộc)
       - Trạng thái tự động: event_status=unread, general_status=pending
    
    **Lưu ý:** Tất cả thông báo khi tạo mới đều có event_status="unread"

    
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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


@router.get("/filter-by-status", response_model=NotificationListResponse, summary="Lọc thông báo theo loại và trạng thái")
def get_notifications_by_type_and_status_endpoint(
    notification_type: NotificationType = Query(..., description="Loại thông báo (event/respond/general)"),
    status: Optional[str] = Query(None, description="Trạng thái tương ứng với loại thông báo"),
    user_id: Optional[int] = Query(None, gt=0, description="Lọc theo user ID"),
    skip: int = Query(0, ge=0, description="Số lượng bỏ qua"),
    limit: int = Query(100, ge=1, le=1000, description="Số lượng tối đa"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lọc thông báo theo loại và trạng thái tương ứng:
    
    **EVENT type (status):**
    - "unread" (chưa đọc)
    - "read" (đã đọc)
    
    **RESPOND type (status):**
    - "pending_response" (chưa phản hồi)
    - "responded" (đã phản hồi)
    
    **GENERAL type (status):**
    - "pending" (chưa gửi)
    - "sent" (đã gửi)
    
    **Ví dụ:**
    - `/filter-by-status?notification_type=event&status=unread`
    - `/filter-by-status?notification_type=respond&status=pending_response&user_id=1`
    - `/filter-by-status?notification_type=general&status=sent`
    - `/filter-by-status?notification_type=event` (lấy tất cả EVENT, không lọc status)
    """
    # Chuyển đổi status string thành enum tương ứng
    event_status = None
    respond_status = None
    general_status = None
    
    if status:
        if notification_type == NotificationType.EVENT:
            try:
                event_status = NotificationEventStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid event_status: {status}. Valid values: unread, read"
                )
        elif notification_type == NotificationType.RESPOND:
            try:
                respond_status = NotificationRespondStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid respond_status: {status}. Valid values: pending_response, responded"
                )
        elif notification_type == NotificationType.GENERAL:
            try:
                general_status = NotificationGeneralStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid general_status: {status}. Valid values: pending, sent"
                )
    
    return service_get_notifications_by_type_and_status(
        db=db,
        notification_type=notification_type,
        event_status=event_status,
        respond_status=respond_status,
        general_status=general_status,
        user_id=user_id,
        skip=skip,
        limit=limit
    )


@router.get("/filter-all-status", response_model=NotificationListResponse, summary="Lọc tất cả thông báo theo tất cả trạng thái")
def get_all_notifications_with_status_filter_endpoint(
    event_status: Optional[NotificationEventStatus] = Query(None, description="Trạng thái EVENT (unread/read)"),
    respond_status: Optional[NotificationRespondStatus] = Query(None, description="Trạng thái RESPOND (pending_response/responded)"),
    general_status: Optional[NotificationGeneralStatus] = Query(None, description="Trạng thái GENERAL (pending/sent)"),
    user_id: Optional[int] = Query(None, gt=0, description="Lọc theo user ID"),
    skip: int = Query(0, ge=0, description="Số lượng bỏ qua"),
    limit: int = Query(100, ge=1, le=1000, description="Số lượng tối đa"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lọc tất cả thông báo theo tất cả các trạng thái có thể:
    
    **Có thể kết hợp các filter:**
    - event_status: "unread" hoặc "read" (cho loại EVENT)
    - respond_status: "pending_response" hoặc "responded" (cho loại RESPOND)  
    - general_status: "pending" hoặc "sent" (cho loại GENERAL)
    - user_id: Lọc theo user cụ thể
    
    **Ví dụ:**
    - `/filter-all-status?event_status=unread&respond_status=pending_response`
    - `/filter-all-status?general_status=sent&user_id=1`
    - `/filter-all-status?event_status=read&respond_status=responded&general_status=pending`
    - `/filter-all-status` (lấy tất cả không lọc)
    """
    return service_get_notifications_by_type_and_status(
        db=db,
        notification_type=None,  # Không lọc theo type, lấy tất cả
        event_status=event_status,
        respond_status=respond_status,
        general_status=general_status,
        user_id=user_id,
        skip=skip,
        limit=limit
    )


@router.get("/{notification_id}", response_model=NotificationResponse, summary="Lấy thông báo theo ID")
def get_notification_endpoint(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy thông tin chi tiết của một thông báo"""
    return service_get_notification(db, notification_id)


@router.put("/{notification_id}", response_model=NotificationResponse, summary="Cập nhật thông báo")
def update_notification_endpoint(
    notification_id: int,
    notification_update: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cập nhật thông tin thông báo"""
    return service_update_notification(db, notification_id, notification_update)


@router.delete("/{notification_id}", summary="Xóa thông báo")
def delete_notification_endpoint(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Xóa một thông báo"""
    return service_delete_notification(db, notification_id)


@router.patch("/respond-status", summary="Cập nhật trạng thái RESPOND theo message")
def update_respond_status_by_message_endpoint(
    status_update: NotificationRespondStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cập nhật trạng thái phản hồi cho tất cả thông báo RESPOND có cùng message
    Dành riêng cho loại RESPOND
    """
    return service_update_respond_status_by_message(
        db, status_update.message, status_update.respond_status
    )


@router.patch("/general-status", summary="Cập nhật trạng thái GENERAL theo message")
def update_general_status_by_message_endpoint(
    status_update: NotificationGeneralStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cập nhật trạng thái cho tất cả thông báo GENERAL có cùng message
    Dành riêng cho loại GENERAL
    """
    return service_update_general_status_by_message(
        db, status_update.message, status_update.general_status
    )


@router.get("/stats/{user_id}", response_model=NotificationStatsResponse, summary="Thống kê thông báo")
def get_notification_stats_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy thống kê thông báo của user"""
    return service_get_notification_stats(db, user_id)
