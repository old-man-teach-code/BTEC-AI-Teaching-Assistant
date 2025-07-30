from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from datetime import datetime

from models.event import Event
from schemas.event import EventCreate, EventUpdate, EventListResponse, EventResponse, EventOverlapCheck
from crud.event import (
    create_event,
    get_event,
    get_user_events,
    get_total_user_events,
    update_event,
    delete_event,
    check_event_overlap,
    get_upcoming_events
)


def service_create_event(
    db: Session,
    event_data: EventCreate,
    owner_id: int
) -> EventResponse:
    """
    Service tạo event mới
    
    Args:
        db: Database session
        event_data: Dữ liệu event cần tạo
        owner_id: ID người dùng tạo event
        
    Returns:
        EventResponse: Thông tin event đã tạo
        
    Raises:
        HTTPException: Nếu có xung đột thời gian với event khác
    """
    try:
        # Kiểm tra xung đột thời gian trước khi tạo
        overlap_check = EventOverlapCheck(
            start_time=event_data.start_time,
            end_time=event_data.end_time
        )
        
        conflicting_events = check_event_overlap(db, owner_id, overlap_check)
        
        if conflicting_events:
            # Lấy thông tin event bị xung đột đầu tiên để thông báo
            first_conflict = conflicting_events[0]
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Event bị xung đột thời gian với event '{first_conflict.title}' từ {first_conflict.start_time} đến {first_conflict.end_time}"
            )
        
        # Tạo event mới nếu không có xung đột
        db_event = create_event(db, event_data, owner_id)
        
        return EventResponse.from_orm(db_event)
        
    except ValueError as e:
        # Lỗi validation từ schema
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Lỗi khác
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể tạo event: {str(e)}"
        )


def service_get_events(
    db: Session,
    owner_id: int,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> EventListResponse:
    """
    Service lấy danh sách events của user
    
    Args:
        db: Database session
        owner_id: ID người dùng sở hữu events
        skip: Số lượng records bỏ qua
        limit: Số lượng records lấy tối đa
        start_date: Lọc events từ thời gian này trở đi
        end_date: Lọc events đến thời gian này
        
    Returns:
        EventListResponse: Danh sách events kèm metadata
    """
    try:
        # Lấy danh sách events
        events = get_user_events(db, owner_id, skip, limit, start_date, end_date)
        
        # Lấy tổng số events
        total = get_total_user_events(db, owner_id, start_date, end_date)
        
        # Chuyển đổi sang response format
        event_responses = [EventResponse.from_orm(event) for event in events]
        
        return EventListResponse(
            total=total,
            items=event_responses
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể lấy danh sách events: {str(e)}"
        )


def service_get_event(db: Session, event_id: int, owner_id: int) -> EventResponse:
    """
    Service lấy thông tin chi tiết một event
    
    Args:
        db: Database session
        event_id: ID của event cần lấy
        owner_id: ID người dùng sở hữu event
        
    Returns:
        EventResponse: Thông tin event
        
    Raises:
        HTTPException: Nếu không tìm thấy event hoặc không có quyền truy cập
    """
    try:
        # Lấy event từ database
        db_event = get_event(db, event_id)
        
        if not db_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy event với ID {event_id}"
            )
        
        # Kiểm tra quyền truy cập
        if db_event.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền truy cập event này"
            )
        
        return EventResponse.from_orm(db_event)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể lấy thông tin event: {str(e)}"
        )


def service_update_event(
    db: Session,
    event_id: int,
    event_update: EventUpdate,
    owner_id: int
) -> EventResponse:
    """
    Service cập nhật thông tin event
    
    Args:
        db: Database session
        event_id: ID của event cần cập nhật
        event_update: Dữ liệu cập nhật
        owner_id: ID người dùng sở hữu event
        
    Returns:
        EventResponse: Thông tin event đã cập nhật
        
    Raises:
        HTTPException: Nếu không tìm thấy event hoặc có xung đột thời gian
    """
    try:
        # Lấy event hiện tại
        db_event = get_event(db, event_id)
        
        if not db_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy event với ID {event_id}"
            )
        
        # Kiểm tra quyền truy cập
        if db_event.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền cập nhật event này"
            )
        
        # Kiểm tra xung đột thời gian nếu có cập nhật thời gian
        if event_update.start_time is not None or event_update.end_time is not None:
            # Sử dụng thời gian mới nếu có, ngược lại dùng thời gian cũ
            new_start_time = event_update.start_time if event_update.start_time is not None else db_event.start_time
            new_end_time = event_update.end_time if event_update.end_time is not None else db_event.end_time
            
            overlap_check = EventOverlapCheck(
                start_time=new_start_time,
                end_time=new_end_time,
                exclude_event_id=event_id  # Loại trừ event hiện tại
            )
            
            conflicting_events = check_event_overlap(db, owner_id, overlap_check)
            
            if conflicting_events:
                first_conflict = conflicting_events[0]
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Event bị xung đột thời gian với event '{first_conflict.title}' từ {first_conflict.start_time} đến {first_conflict.end_time}"
                )
        
        # Cập nhật event
        updated_event = update_event(db, db_event, event_update)
        
        return EventResponse.from_orm(updated_event)
        
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
            detail=f"Không thể cập nhật event: {str(e)}"
        )


def service_delete_event(db: Session, event_id: int, owner_id: int) -> Dict[str, Any]:
    """
    Service xóa event
    
    Args:
        db: Database session
        event_id: ID của event cần xóa
        owner_id: ID người dùng sở hữu event
        
    Returns:
        Dict[str, Any]: Thông báo kết quả
        
    Raises:
        HTTPException: Nếu không tìm thấy event hoặc không có quyền truy cập
    """
    try:
        # Lấy event hiện tại
        db_event = get_event(db, event_id)
        
        if not db_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy event với ID {event_id}"
            )
        
        # Kiểm tra quyền truy cập
        if db_event.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền xóa event này"
            )
        
        # Xóa event
        delete_event(db, db_event)
        
        return {
            "message": f"Event '{db_event.title}' đã được xóa thành công",
            "event_id": event_id,
            "deleted_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể xóa event: {str(e)}"
        )


def service_check_event_overlap(
    db: Session,
    owner_id: int,
    overlap_check: EventOverlapCheck
) -> List[EventResponse]:
    """
    Service kiểm tra xung đột thời gian
    
    Args:
        db: Database session
        owner_id: ID người dùng sở hữu events
        overlap_check: Dữ liệu để kiểm tra xung đột
        
    Returns:
        List[EventResponse]: Danh sách events bị xung đột
    """
    try:
        conflicting_events = check_event_overlap(db, owner_id, overlap_check)
        return [EventResponse.from_orm(event) for event in conflicting_events]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể kiểm tra xung đột thời gian: {str(e)}"
        )


def service_get_upcoming_events(
    db: Session,
    owner_id: int,
    limit: int = 10
) -> List[EventResponse]:
    """
    Service lấy các events sắp tới
    
    Args:
        db: Database session
        owner_id: ID người dùng sở hữu events
        limit: Số lượng events tối đa
        
    Returns:
        List[EventResponse]: Danh sách events sắp tới
    """
    try:
        current_time = datetime.now()
        upcoming_events = get_upcoming_events(db, owner_id, current_time, limit)
        return [EventResponse.from_orm(event) for event in upcoming_events]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể lấy danh sách events sắp tới: {str(e)}"
        ) 