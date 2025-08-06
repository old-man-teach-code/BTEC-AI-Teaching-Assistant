from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict
from datetime import datetime

from models.notification import (
    Notification, 
    NotificationType,
    NotificationEventStatus,
    NotificationRespondStatus, 
    NotificationGeneralStatus
)
from schemas.notification import NotificationCreate, NotificationUpdate


def auto_set_status(notification_type: NotificationType, event_id: Optional[int] = None) -> Dict:
    """Tự động set status dựa trên notification_type"""
    status_dict = {
        'event_status': None,
        'respond_status': None, 
        'general_status': None
    }
    
    if notification_type == NotificationType.EVENT:
        status_dict['event_status'] = NotificationEventStatus.UNREAD
    elif notification_type == NotificationType.RESPOND:
        status_dict['respond_status'] = NotificationRespondStatus.PENDING_RESPONSE
    elif notification_type == NotificationType.GENERAL:
        status_dict['general_status'] = NotificationGeneralStatus.PENDING
    
    return status_dict


def validate_status_for_type(notification_type: NotificationType, status_update: dict) -> bool:
    """Validate status update theo notification type"""
    if notification_type == NotificationType.EVENT:
        return 'event_status' in status_update and status_update['event_status'] is not None
    elif notification_type == NotificationType.RESPOND:
        return 'respond_status' in status_update and status_update['respond_status'] is not None
    elif notification_type == NotificationType.GENERAL:
        return 'general_status' in status_update and status_update['general_status'] is not None
    return False


def create_notification(db: Session, notification: NotificationCreate) -> Notification:
    """Tạo notification mới với auto-status"""
    # Auto-set status dựa trên notification_type
    status_dict = auto_set_status(notification.notification_type, notification.event_id)
    
    db_notification = Notification(
        notification_type=notification.notification_type,
        title=notification.title,
        message=notification.message,
        user_id=notification.user_id,
        event_id=notification.event_id,
        scheduled_at=notification.scheduled_at,
        event_status=status_dict['event_status'],
        respond_status=status_dict['respond_status'],
        general_status=status_dict['general_status']
    )
    
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def get_notification(db: Session, notification_id: int) -> Optional[Notification]:
    """Lấy notification theo ID"""
    return db.query(Notification).filter(Notification.id == notification_id).first()


def get_all_notifications(
    db: Session, 
    skip: int = 0, 
    limit: int = 100
) -> List[Notification]:
    """Lấy tất cả notifications"""
    return db.query(Notification).order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()


def get_notifications_by_user(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100,
    notification_type: Optional[NotificationType] = None
) -> List[Notification]:
    """Lấy danh sách notifications của user với filter"""
    query = db.query(Notification).filter(Notification.user_id == user_id)
    
    if notification_type:
        query = query.filter(Notification.notification_type == notification_type)
    
    return query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()


def get_notifications_by_message(db: Session, message: str) -> List[Notification]:
    """Lấy notifications theo message content"""
    return db.query(Notification).filter(Notification.message == message).all()


def get_respond_notifications_by_message(db: Session, message: str) -> List[Notification]:
    """Lấy RESPOND notifications theo message content"""
    return db.query(Notification).filter(
        and_(
            Notification.message == message,
            Notification.notification_type == NotificationType.RESPOND
        )
    ).all()


def get_general_notifications_by_message(db: Session, message: str) -> List[Notification]:
    """Lấy GENERAL notifications theo message content"""
    return db.query(Notification).filter(
        and_(
            Notification.message == message,
            Notification.notification_type == NotificationType.GENERAL
        )
    ).all()


def update_notification(db: Session, notification_id: int, notification_update: NotificationUpdate) -> Optional[Notification]:
    """Cập nhật notification"""
    db_notification = get_notification(db, notification_id)
    if not db_notification:
        return None
    
    update_data = notification_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_notification, field, value)
    
    db_notification.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_notification)
    return db_notification


def update_notification_status_by_message(
    db: Session, 
    message: str, 
    status_update: dict
) -> List[Notification]:
    """Cập nhật status theo message content"""
    notifications = get_notifications_by_message(db, message)
    updated_notifications = []
    
    for notification in notifications:
        # Validate status update cho notification type
        if validate_status_for_type(notification.notification_type, status_update):
            for field, value in status_update.items():
                if hasattr(notification, field):
                    setattr(notification, field, value)
            
            notification.updated_at = datetime.utcnow()
            updated_notifications.append(notification)
    
    db.commit()
    
    for notification in updated_notifications:
        db.refresh(notification)
    
    return updated_notifications


def update_respond_notification_status_by_message(
    db: Session, 
    message: str, 
    respond_status: NotificationRespondStatus
) -> List[Notification]:
    """Cập nhật status cho RESPOND notifications theo message"""
    notifications = get_respond_notifications_by_message(db, message)
    updated_notifications = []
    
    for notification in notifications:
        notification.respond_status = respond_status
        notification.updated_at = datetime.utcnow()
        updated_notifications.append(notification)
    
    db.commit()
    
    for notification in updated_notifications:
        db.refresh(notification)
    
    return updated_notifications


def update_general_notification_status_by_message(
    db: Session, 
    message: str, 
    general_status: NotificationGeneralStatus
) -> List[Notification]:
    """Cập nhật status cho GENERAL notifications theo message"""
    notifications = get_general_notifications_by_message(db, message)
    updated_notifications = []
    
    for notification in notifications:
        notification.general_status = general_status
        notification.updated_at = datetime.utcnow()
        updated_notifications.append(notification)
    
    db.commit()
    
    for notification in updated_notifications:
        db.refresh(notification)
    
    return updated_notifications


def update_notification_status_by_id(
    db: Session, 
    notification_id: int, 
    status_update: dict
) -> Optional[Notification]:
    """Cập nhật status theo notification ID"""
    notification = get_notification(db, notification_id)
    if not notification:
        return None
    
    # Validate status update cho notification type
    if not validate_status_for_type(notification.notification_type, status_update):
        return None
    
    for field, value in status_update.items():
        if hasattr(notification, field):
            setattr(notification, field, value)
    
    notification.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(notification)
    return notification


def delete_notification(db: Session, notification_id: int) -> bool:
    """Xóa notification"""
    db_notification = get_notification(db, notification_id)
    if not db_notification:
        return False
    
    db.delete(db_notification)
    db.commit()
    return True


def get_notifications_stats(db: Session, user_id: int) -> Dict:
    """Lấy thống kê notifications của user"""
    total = db.query(Notification).filter(Notification.user_id == user_id).count()
    
    # Thống kê theo type
    by_type = {}
    for ntype in NotificationType:
        type_count = db.query(Notification).filter(
            and_(Notification.user_id == user_id, Notification.notification_type == ntype)
        ).count()
        by_type[ntype.value] = type_count
    
    return {
        "total": total,
        "by_type": by_type
    }


def get_notifications_by_type_and_status(
    db: Session,
    notification_type: NotificationType,
    event_status: Optional[NotificationEventStatus] = None,
    respond_status: Optional[NotificationRespondStatus] = None,
    general_status: Optional[NotificationGeneralStatus] = None,
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Notification]:
    """Lọc notifications theo loại và trạng thái tương ứng"""
    query = db.query(Notification).filter(
        Notification.notification_type == notification_type
    )
    
    # Lọc theo user nếu có
    if user_id:
        query = query.filter(Notification.user_id == user_id)
    
    # Lọc theo trạng thái tương ứng với loại
    if notification_type == NotificationType.EVENT and event_status:
        query = query.filter(Notification.event_status == event_status)
    elif notification_type == NotificationType.RESPOND and respond_status:
        query = query.filter(Notification.respond_status == respond_status)
    elif notification_type == NotificationType.GENERAL and general_status:
        query = query.filter(Notification.general_status == general_status)
    
    return query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()


def count_notifications_by_type_and_status(
    db: Session,
    notification_type: NotificationType,
    event_status: Optional[NotificationEventStatus] = None,
    respond_status: Optional[NotificationRespondStatus] = None,
    general_status: Optional[NotificationGeneralStatus] = None,
    user_id: Optional[int] = None
) -> int:
    """Đếm số lượng notifications theo loại và trạng thái"""
    query = db.query(Notification).filter(
        Notification.notification_type == notification_type
    )
    
    # Lọc theo user nếu có
    if user_id:
        query = query.filter(Notification.user_id == user_id)
    
    # Lọc theo trạng thái tương ứng với loại
    if notification_type == NotificationType.EVENT and event_status:
        query = query.filter(Notification.event_status == event_status)
    elif notification_type == NotificationType.RESPOND and respond_status:
        query = query.filter(Notification.respond_status == respond_status)
    elif notification_type == NotificationType.GENERAL and general_status:
        query = query.filter(Notification.general_status == general_status)
    
    return query.count()
