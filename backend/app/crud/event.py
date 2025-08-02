from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from models.event import Event
from schemas.event import EventCreate, EventUpdate, EventOverlapCheck
from typing import List, Optional
from datetime import datetime



def create_event(db: Session, event_data: EventCreate, owner_id: int) -> Event:
    """
    Tạo event mới trong database
    
    Args:
        db: Database session
        event_data: Dữ liệu event cần tạo
        owner_id: ID của user sở hữu event
        
    Returns:
        Event: Event đã được tạo
    """
    # Chuyển đổi event_data thành dict và thêm owner_id
    event_dict = event_data.dict()
    db_event = Event(**event_dict, owner_id=owner_id)
    
    # Thêm vào database và commit
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    return db_event


def get_event(db: Session, event_id: int) -> Optional[Event]:
    """
    Lấy event theo ID
    
    Args:
        db: Database session
        event_id: ID của event cần lấy
        
    Returns:
        Event hoặc None nếu không tìm thấy
    """
    return db.query(Event).filter(Event.id == event_id).first()


def get_user_events(
    db: Session, 
    owner_id: int, 
    skip: int = 0, 
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Event]:
    """
    Lấy danh sách events của một user với phân trang và filter theo thời gian
    
    Args:
        db: Database session
        owner_id: ID của user sở hữu events
        skip: Số lượng records bỏ qua
        limit: Số lượng records lấy tối đa
        start_date: Lọc events từ thời gian này trở đi
        end_date: Lọc events đến thời gian này
        
    Returns:
        List[Event]: Danh sách events
    """
    # Query cơ bản
    query = db.query(Event).filter(Event.owner_id == owner_id)
    
    # Thêm filter theo thời gian nếu có
    if start_date:
        query = query.filter(Event.end_time >= start_date)
    if end_date:
        query = query.filter(Event.start_time <= end_date)
    
    # Sắp xếp theo thời gian bắt đầu
    return query.order_by(Event.start_time).offset(skip).limit(limit).all()


def get_total_user_events(
    db: Session, 
    owner_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> int:
    """
    Lấy tổng số events của một user (để phục vụ phân trang)
    
    Args:
        db: Database session
        owner_id: ID của user sở hữu events
        start_date: Lọc events từ thời gian này trở đi
        end_date: Lọc events đến thời gian này
        
    Returns:
        int: Tổng số events
    """
    # Query cơ bản
    query = db.query(Event).filter(Event.owner_id == owner_id)
    
    # Thêm filter theo thời gian nếu có
    if start_date:
        query = query.filter(Event.end_time >= start_date)
    if end_date:
        query = query.filter(Event.start_time <= end_date)
    
    return query.count()


def update_event(
    db: Session, 
    event: Event, 
    event_update: EventUpdate
) -> Event:
    """
    Cập nhật thông tin event
    
    Args:
        db: Database session
        event: Event object cần cập nhật
        event_update: Dữ liệu cập nhật
        
    Returns:
        Event: Event đã được cập nhật
    """
    # Lấy các trường có giá trị (không phải None) để cập nhật
    update_data = event_update.dict(exclude_unset=True)
    
    # Cập nhật từng trường
    for field, value in update_data.items():
        setattr(event, field, value)
    
    # Commit thay đổi
    db.commit()
    db.refresh(event)
    
    return event


def delete_event(db: Session, event: Event) -> None:
    """
    Xóa event khỏi database (hard delete)
    
    Args:
        db: Database session
        event: Event object cần xóa
    """
    db.delete(event)
    db.commit()
    
    

def check_event_overlap(
    db: Session,
    owner_id: int,
    overlap_check: EventOverlapCheck
) -> List[Event]:
    """
    Kiểm tra xung đột thời gian với các events khác

    Chỉ kiểm tra xung đột nếu cùng loại event (event_type).
    Các loại event khác nhau có thể trùng thời gian.

    Args:
        db: Database session
        owner_id: ID của user sở hữu events
        overlap_check: Dữ liệu để kiểm tra xung đột

    Returns:
        List[Event]: Danh sách events bị xung đột (cùng loại)
    """
    # Query để tìm events xung đột
    query = db.query(Event).filter(
        Event.owner_id == owner_id,
        # Logic kiểm tra overlap: start_time < other_end_time AND end_time > other_start_time
        and_(
            Event.start_time < overlap_check.end_time,
            Event.end_time > overlap_check.start_time
        )
    )

    # 🆕 CHỈ KIỂM TRA XUNG ĐỘT NẾU CÙNG LOẠI EVENT
    if hasattr(overlap_check, 'event_type') and overlap_check.event_type:
        query = query.filter(Event.event_type == overlap_check.event_type)

    # Loại trừ event hiện tại nếu đang update
    if overlap_check.exclude_event_id:
        query = query.filter(Event.id != overlap_check.exclude_event_id)

    return query.all()


def get_upcoming_events(
    db: Session, 
    owner_id: int, 
    from_time: datetime,
    limit: int = 10
) -> List[Event]:
    """
    Lấy các events sắp tới từ thời gian nhất định
    
    Args:
        db: Database session
        owner_id: ID của user sở hữu events
        from_time: Thời gian bắt đầu tìm kiếm
        limit: Số lượng events tối đa
        
    Returns:
        List[Event]: Danh sách events sắp tới
    """
    return db.query(Event).filter(
        Event.owner_id == owner_id,
        Event.start_time >= from_time
    ).order_by(Event.start_time).limit(limit).all()


def get_events_with_reminder(
    db: Session, 
    reminder_time: datetime,
    tolerance_minutes: int = 5
) -> List[Event]:
    """
    Lấy các events cần nhắc nhở trong khoảng thời gian nhất định
    
    Args:
        db: Database session
        reminder_time: Thời gian cần nhắc nhở
        tolerance_minutes: Khoảng dung sai (phút)
        
    Returns:
        List[Event]: Danh sách events cần nhắc nhở
    """
    from datetime import timedelta
    
    # Tính toán khoảng thời gian cần nhắc nhở
    # Event cần nhắc nhở = start_time - reminder_minutes = reminder_time (± tolerance)
    tolerance = timedelta(minutes=tolerance_minutes)
    
    return db.query(Event).filter(
        # Kiểm tra thời gian nhắc nhở có nằm trong khoảng tolerance không
        and_(
            Event.start_time >= reminder_time - tolerance,
            Event.start_time <= reminder_time + tolerance
        )
    ).all() 