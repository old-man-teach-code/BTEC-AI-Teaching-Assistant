from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Any

from models.event_type import EventType
from schemas.event_type import EventTypeCreate, EventTypeUpdate, EventTypeResponse, EventTypeListResponse
from crud.event_type import (
    get_event_type,
    get_event_type_by_code,
    get_all_event_types,
    count_event_types,
    create_event_type,
    update_event_type,
    delete_event_type,
    seed_default_event_types
)


def service_get_event_types(db: Session, skip: int = 0, limit: int = 100) -> EventTypeListResponse:
    """
    Service lấy danh sách event types
    
    Args:
        db: Database session
        skip: Số lượng records bỏ qua
        limit: Số lượng records lấy tối đa
        
    Returns:
        EventTypeListResponse: Danh sách event types kèm metadata
    """
    try:
        # Lấy danh sách event types
        event_types = get_all_event_types(db, skip, limit)
        
        # Lấy tổng số event types
        total = count_event_types(db)
        
        # Chuyển đổi sang response format
        event_type_responses = [EventTypeResponse.from_orm(event_type) for event_type in event_types]
        
        return EventTypeListResponse(
            total=total,
            items=event_type_responses
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể lấy danh sách event types: {str(e)}"
        )


def service_get_event_type(db: Session, event_type_id: int) -> EventTypeResponse:
    """
    Service lấy thông tin chi tiết một event type
    
    Args:
        db: Database session
        event_type_id: ID của event type cần lấy
        
    Returns:
        EventTypeResponse: Thông tin event type
        
    Raises:
        HTTPException: Nếu không tìm thấy event type
    """
    try:
        # Lấy event type từ database
        db_event_type = get_event_type(db, event_type_id)
        
        if not db_event_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy event type với ID {event_type_id}"
            )
        
        return EventTypeResponse.from_orm(db_event_type)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể lấy thông tin event type: {str(e)}"
        )


def service_create_event_type(db: Session, event_type_data: EventTypeCreate) -> EventTypeResponse:
    """
    Service tạo event type mới
    
    Args:
        db: Database session
        event_type_data: Dữ liệu event type cần tạo
        
    Returns:
        EventTypeResponse: Thông tin event type đã tạo
        
    Raises:
        HTTPException: Nếu code đã tồn tại
    """
    try:
        # Kiểm tra code đã tồn tại chưa
        existing_event_type = get_event_type_by_code(db, event_type_data.code)
        if existing_event_type:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Event type với code '{event_type_data.code}' đã tồn tại"
            )
        
        # Tạo event type mới
        db_event_type = create_event_type(db, event_type_data)
        
        return EventTypeResponse.from_orm(db_event_type)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể tạo event type: {str(e)}"
        )


def service_update_event_type(
    db: Session,
    event_type_id: int,
    event_type_update: EventTypeUpdate
) -> EventTypeResponse:
    """
    Service cập nhật thông tin event type
    
    Args:
        db: Database session
        event_type_id: ID của event type cần cập nhật
        event_type_update: Dữ liệu cập nhật
        
    Returns:
        EventTypeResponse: Thông tin event type đã cập nhật
        
    Raises:
        HTTPException: Nếu không tìm thấy event type
    """
    try:
        # Lấy event type hiện tại
        db_event_type = get_event_type(db, event_type_id)
        
        if not db_event_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy event type với ID {event_type_id}"
            )
        
        # Cập nhật event type
        updated_event_type = update_event_type(db, db_event_type, event_type_update)
        
        return EventTypeResponse.from_orm(updated_event_type)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể cập nhật event type: {str(e)}"
        )


def service_delete_event_type(db: Session, event_type_id: int) -> Dict[str, Any]:
    """
    Service xóa event type
    
    Args:
        db: Database session
        event_type_id: ID của event type cần xóa
        
    Returns:
        Dict[str, Any]: Thông báo kết quả
        
    Raises:
        HTTPException: Nếu không tìm thấy event type hoặc không thể xóa
    """
    try:
        # Lấy event type từ database
        db_event_type = get_event_type(db, event_type_id)
        
        if not db_event_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy event type với ID {event_type_id}"
            )
        
        # Kiểm tra xem có events nào đang sử dụng event type này không
        if db_event_type.events and len(db_event_type.events) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Không thể xóa event type này vì có {len(db_event_type.events)} events đang sử dụng"
            )
        
        # Xóa event type
        delete_event_type(db, db_event_type)
        
        return {
            "message": f"Event type '{db_event_type.name}' đã được xóa thành công",
            "id": event_type_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể xóa event type: {str(e)}"
        )


def service_seed_default_event_types(db: Session) -> Dict[str, Any]:
    """
    Service seed dữ liệu mặc định cho event types
    
    Args:
        db: Database session
        
    Returns:
        Dict[str, Any]: Thông báo kết quả
    """
    try:
        # Seed dữ liệu mặc định
        created_types = seed_default_event_types(db)
        
        return {
            "message": f"Đã seed {len(created_types)} event types mặc định",
            "created_count": len(created_types)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể seed dữ liệu mặc định: {str(e)}"
        ) 