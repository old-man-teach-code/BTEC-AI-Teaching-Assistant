from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func, case
from models.notification import Notification, NotificationStatus, NotificationCategory
from schemas.notification import NotificationCreate, NotificationUpdate, NotificationStatusUpdate
from typing import List, Optional, Dict, Any
from datetime import datetime


def create_notification(db: Session, notification_data: NotificationCreate) -> Notification:
    """
    Tạo notification mới trong database
    
    Args:
        db: Database session
        notification_data: Dữ liệu notification cần tạo
        
    Returns:
        Notification: Notification đã được tạo
    """
    # Chuyển đổi notification_data thành dict
    notification_dict = notification_data.dict()
    db_notification = Notification(**notification_dict)
    
    # Thêm vào database và commit
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    
    return db_notification


def get_notification(db: Session, notification_id: int) -> Optional[Notification]:
    """
    Lấy notification theo ID
    
    Args:
        db: Database session
        notification_id: ID của notification cần lấy
        
    Returns:
        Notification hoặc None nếu không tìm thấy
    """
    return db.query(Notification).filter(Notification.id == notification_id).first()


def get_user_notifications(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[NotificationStatus] = None,
    category: Optional[NotificationCategory] = None,
    unread_only: bool = False
) -> tuple[List[Notification], int]:
    """
    Lấy danh sách notifications của một user với filter
    
    Args:
        db: Database session
        user_id: ID của user
        skip: Số lượng records bỏ qua (cho phân trang)
        limit: Số lượng records lấy tối đa
        status: Lọc theo trạng thái (optional)
        category: Lọc theo danh mục (optional)
        unread_only: Chỉ lấy notifications chưa đọc
        
    Returns:
        tuple: (danh sách notifications, tổng số records)
    """
    # Xây dựng query cơ bản
    query = db.query(Notification).filter(Notification.user_id == user_id)
    
    # Thêm filters
    if status:
        query = query.filter(Notification.status == status)
    
    if category:
        query = query.filter(Notification.category == category)
        
    if unread_only:
        query = query.filter(Notification.status == NotificationStatus.UNREAD)
    
    # Đếm tổng số records (trước khi skip/limit)
    total = query.count()
    
    # Áp dụng ordering, skip và limit
    notifications = (
        query.order_by(desc(Notification.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return notifications, total


def update_notification(
    db: Session, 
    notification_id: int, 
    notification_update: NotificationUpdate
) -> Optional[Notification]:
    """
    Cập nhật thông tin notification
    
    Args:
        db: Database session
        notification_id: ID của notification cần cập nhật
        notification_update: Dữ liệu cập nhật
        
    Returns:
        Notification đã cập nhật hoặc None nếu không tìm thấy
    """
    db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
    
    if db_notification is None:
        return None
    
    # Cập nhật các trường có giá trị
    update_data = notification_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_notification, field, value)
    
    # Nếu trạng thái chuyển sang READ, set read_at
    if notification_update.status == NotificationStatus.READ and db_notification.read_at is None:
        db_notification.read_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_notification)
    
    return db_notification


def update_notification_status(
    db: Session, 
    notification_id: int, 
    status_update: NotificationStatusUpdate
) -> Optional[Notification]:
    """
    Cập nhật trạng thái notification
    
    Args:
        db: Database session
        notification_id: ID của notification cần cập nhật
        status_update: Trạng thái mới
        
    Returns:
        Notification đã cập nhật hoặc None nếu không tìm thấy
    """
    db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
    
    if db_notification is None:
        return None
    
    # Cập nhật trạng thái
    db_notification.status = status_update.status
    
    # Nếu trạng thái chuyển sang READ, set read_at
    if status_update.status == NotificationStatus.READ and db_notification.read_at is None:
        db_notification.read_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_notification)
    
    return db_notification


def mark_notifications_as_read(db: Session, notification_ids: List[int], user_id: int) -> int:
    """
    Đánh dấu nhiều notifications là đã đọc
    
    Args:
        db: Database session
        notification_ids: Danh sách ID notifications
        user_id: ID user (để bảo mật)
        
    Returns:
        Số notifications đã được cập nhật
    """
    current_time = datetime.utcnow()
    
    updated_count = (
        db.query(Notification)
        .filter(
            and_(
                Notification.id.in_(notification_ids),
                Notification.user_id == user_id,
                Notification.status == NotificationStatus.UNREAD
            )
        )
        .update(
            {
                "status": NotificationStatus.READ,
                "read_at": current_time,
                "updated_at": current_time
            },
            synchronize_session=False
        )
    )
    
    db.commit()
    return updated_count


def delete_notification(db: Session, notification_id: int) -> bool:
    """
    Xóa notification
    
    Args:
        db: Database session
        notification_id: ID của notification cần xóa
        
    Returns:
        True nếu xóa thành công, False nếu không tìm thấy
    """
    db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
    
    if db_notification is None:
        return False
    
    db.delete(db_notification)
    db.commit()
    
    return True


def get_user_notification_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Lấy thống kê notifications của user
    
    Args:
        db: Database session
        user_id: ID của user
        
    Returns:
        Dictionary chứa thống kê
    """
    # Query để đếm theo status
    status_stats = (
        db.query(
            Notification.status,
            func.count(Notification.id).label('count')
        )
        .filter(Notification.user_id == user_id)
        .group_by(Notification.status)
        .all()
    )
    
    # Query để đếm theo category
    category_stats = (
        db.query(
            Notification.category,
            func.count(Notification.id).label('count')
        )
        .filter(Notification.user_id == user_id)
        .group_by(Notification.category)
        .all()
    )
    
    # Tổng số notifications
    total = db.query(Notification).filter(Notification.user_id == user_id).count()
    
    # Tạo dict kết quả
    stats = {
        "total": total,
        "unread": 0,
        "read": 0,
        "pending_response": 0,
        "responded": 0,
        "by_category": {}
    }
    
    # Điền thống kê theo status
    for status, count in status_stats:
        if status == NotificationStatus.UNREAD:
            stats["unread"] = count
        elif status == NotificationStatus.READ:
            stats["read"] = count
        elif status == NotificationStatus.PENDING_RESPONSE:
            stats["pending_response"] = count
        elif status == NotificationStatus.RESPONDED:
            stats["responded"] = count
    
    # Điền thống kê theo category
    for category, count in category_stats:
        stats["by_category"][category.value] = count
    
    return stats


def get_unread_count(db: Session, user_id: int) -> int:
    """
    Lấy số lượng notifications chưa đọc của user
    
    Args:
        db: Database session
        user_id: ID của user
        
    Returns:
        Số lượng notifications chưa đọc
    """
    return (
        db.query(Notification)
        .filter(
            and_(
                Notification.user_id == user_id,
                Notification.status == NotificationStatus.UNREAD
            )
        )
        .count()
    )


def get_notifications_by_event(db: Session, event_id: int) -> List[Notification]:
    """
    Lấy tất cả notifications liên quan đến một event
    
    Args:
        db: Database session
        event_id: ID của event
        
    Returns:
        Danh sách notifications liên quan đến event
    """
    return (
        db.query(Notification)
        .filter(Notification.event_id == event_id)
        .order_by(desc(Notification.created_at))
        .all()
    )
