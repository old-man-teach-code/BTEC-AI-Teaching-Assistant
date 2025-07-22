from sqlalchemy.orm import Session
from models.event_type import EventType, EventTypeEnum
from schemas.event_type import EventTypeCreate, EventTypeUpdate
from typing import List, Optional
from utils.db_utils import reset_auto_increment


def get_event_type(db: Session, event_type_id: int) -> Optional[EventType]:
    """
    Lấy event type theo ID
    
    Args:
        db: Database session
        event_type_id: ID của event type cần lấy
        
    Returns:
        EventType hoặc None nếu không tìm thấy
    """
    return db.query(EventType).filter(EventType.id == event_type_id).first()


def get_event_type_by_code(db: Session, code: str) -> Optional[EventType]:
    """
    Lấy event type theo code
    
    Args:
        db: Database session
        code: Mã code của event type cần lấy
        
    Returns:
        EventType hoặc None nếu không tìm thấy
    """
    return db.query(EventType).filter(EventType.code == code).first()


def get_all_event_types(db: Session, skip: int = 0, limit: int = 100) -> List[EventType]:
    """
    Lấy tất cả event types với phân trang
    
    Args:
        db: Database session
        skip: Số lượng records bỏ qua
        limit: Số lượng records lấy tối đa
        
    Returns:
        List[EventType]: Danh sách event types
    """
    return db.query(EventType).offset(skip).limit(limit).all()


def count_event_types(db: Session) -> int:
    """
    Đếm tổng số event types
    
    Args:
        db: Database session
        
    Returns:
        int: Tổng số event types
    """
    return db.query(EventType).count()


def create_event_type(db: Session, event_type_data: EventTypeCreate) -> EventType:
    """
    Tạo event type mới
    
    Args:
        db: Database session
        event_type_data: Dữ liệu event type cần tạo
        
    Returns:
        EventType: Event type đã được tạo
    """
    # Chuyển đổi event_type_data thành dict
    event_type_dict = event_type_data.dict()
    db_event_type = EventType(**event_type_dict)
    
    # Thêm vào database và commit
    db.add(db_event_type)
    db.commit()
    db.refresh(db_event_type)
    
    return db_event_type


def update_event_type(db: Session, event_type: EventType, event_type_update: EventTypeUpdate) -> EventType:
    """
    Cập nhật thông tin event type
    
    Args:
        db: Database session
        event_type: Event type object cần cập nhật
        event_type_update: Dữ liệu cập nhật
        
    Returns:
        EventType: Event type đã được cập nhật
    """
    # Lấy các trường có giá trị (không phải None) để cập nhật
    update_data = event_type_update.dict(exclude_unset=True)
    
    # Cập nhật từng trường
    for field, value in update_data.items():
        setattr(event_type, field, value)
    
    # Commit thay đổi
    db.commit()
    db.refresh(event_type)
    
    return event_type


def delete_event_type(db: Session, event_type: EventType) -> None:
    """
    Xóa event type khỏi database
    
    Args:
        db: Database session
        event_type: Event type object cần xóa
    """
    db.delete(event_type)
    db.commit()
    
    # Reset auto-increment để ID tiếp theo bắt đầu từ ID cao nhất hiện có + 1
    reset_auto_increment(db, "event_types")


def seed_default_event_types(db: Session) -> List[EventType]:
    """
    Seed dữ liệu mặc định cho event types
    Chỉ tạo những loại chưa tồn tại trong DB
    
    Args:
        db: Database session
        
    Returns:
        List[EventType]: Danh sách event types đã được tạo
    """
    created_types = []
    
    # Lấy danh sách default types từ model
    default_types = EventType.get_default_types()
    
    # Tạo từng loại nếu chưa tồn tại
    for type_data in default_types:
        # Kiểm tra xem đã có chưa
        existing = db.query(EventType).filter(EventType.code == type_data["code"]).first()
        
        if not existing:
            # Tạo mới nếu chưa có
            db_event_type = EventType(**type_data)
            db.add(db_event_type)
            created_types.append(db_event_type)
    
    # Commit nếu có event types mới
    if created_types:
        db.commit()
        for event_type in created_types:
            db.refresh(event_type)
    
    return created_types 