from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from dependencies.deps import get_db, get_current_user
from schemas.event import EventCreate, EventUpdate, EventResponse, EventListResponse, EventOverlapCheck
from services.event_service import (
    service_create_event,
    service_get_events,
    service_get_event,
    service_update_event,
    service_delete_event,
    service_check_event_overlap,
    service_get_upcoming_events
)
from models.user import User

# Khởi tạo router với prefix mặc định
router = APIRouter()


@router.post("/events", response_model=EventResponse)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Tạo event mới trong calendar
    
    Args:
        event_data: Dữ liệu event cần tạo
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        EventResponse: Thông tin event đã tạo
        
    Raises:
        HTTPException 409: Nếu có xung đột thời gian với event khác
        HTTPException 400: Nếu dữ liệu không hợp lệ
    """
    return service_create_event(db, event_data, current_user.id)





@router.get("/events", response_model=EventListResponse)
def get_events(
    skip: int = Query(0, ge=0, description="Số lượng records bỏ qua"),
    limit: int = Query(100, ge=1, le=1000, description="Số lượng records lấy tối đa"),
    start: Optional[datetime] = Query(None, description="Lọc events từ thời gian này trở đi (ISO format)"),
    end: Optional[datetime] = Query(None, description="Lọc events đến thời gian này (ISO format)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách events của user hiện tại với filter theo thời gian
    
    Args:
        skip: Số lượng records bỏ qua (cho phân trang)
        limit: Số lượng records lấy tối đa (cho phân trang)
        start: Lọc events từ thời gian này trở đi (query parameter)
        end: Lọc events đến thời gian này (query parameter)
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        EventListResponse: Danh sách events kèm metadata phân trang
        
    Example:
        GET /calendar/events?start=2024-01-01T00:00:00&end=2024-01-31T23:59:59&skip=0&limit=10
    """
    return service_get_events(db, current_user.id, skip, limit, start, end)


@router.get("/events/upcoming", response_model=List[EventResponse])
def get_upcoming_events(
    limit: int = Query(10, ge=1, le=100, description="Số lượng events tối đa"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách events sắp tới
    
    Args:
        limit: Số lượng events tối đa
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        List[EventResponse]: Danh sách events sắp tới được sắp xếp theo thời gian
        
    Note:
        Endpoint này hữu ích cho dashboard để hiển thị events sắp tới
    """
    return service_get_upcoming_events(db, current_user.id, limit)


@router.get("/events/today", response_model=List[EventResponse])
def get_today_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách events hôm nay
    
    Args:
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        List[EventResponse]: Danh sách events hôm nay
        
    Note:
        Endpoint này lấy tất cả events trong ngày hiện tại
    """
    # Lấy thời gian bắt đầu và kết thúc ngày hôm nay
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Lấy events trong ngày với limit cao để lấy tất cả
    result = service_get_events(db, current_user.id, 0, 1000, start_of_day, end_of_day)
    return result.items


@router.get("/events/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int = Path(..., gt=0, description="ID của event cần lấy"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy thông tin chi tiết một event
    
    Args:
        event_id: ID của event cần lấy
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        EventResponse: Thông tin chi tiết event
        
    Raises:
        HTTPException 404: Nếu không tìm thấy event
        HTTPException 403: Nếu không có quyền truy cập event
    """
    return service_get_event(db, event_id, current_user.id)


@router.put("/events/{event_id}", response_model=EventResponse)
def update_event(
    event_update: EventUpdate,
    event_id: int = Path(..., gt=0, description="ID của event cần cập nhật"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cập nhật thông tin event
    
    Args:
        event_update: Dữ liệu cập nhật (chỉ cần truyền các trường muốn cập nhật)
        event_id: ID của event cần cập nhật
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        EventResponse: Thông tin event đã cập nhật
        
    Raises:
        HTTPException 404: Nếu không tìm thấy event
        HTTPException 403: Nếu không có quyền cập nhật event
        HTTPException 409: Nếu có xung đột thời gian với event khác
    """
    return service_update_event(db, event_id, event_update, current_user.id)


@router.delete("/events/{event_id}")
def delete_event(
    event_id: int = Path(..., gt=0, description="ID của event cần xóa"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Xóa event khỏi calendar
    
    Args:
        event_id: ID của event cần xóa
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        Dict: Thông báo kết quả xóa
        
    Raises:
        HTTPException 404: Nếu không tìm thấy event
        HTTPException 403: Nếu không có quyền xóa event
    """
    return service_delete_event(db, event_id, current_user.id)


@router.post("/events/check-overlap", response_model=List[EventResponse])
def check_event_overlap(
    overlap_check: EventOverlapCheck,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Kiểm tra xung đột thời gian với các events khác
    
    Args:
        overlap_check: Dữ liệu thời gian để kiểm tra xung đột
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        List[EventResponse]: Danh sách events bị xung đột thời gian
        
    Note:
        Endpoint này hữu ích khi frontend muốn kiểm tra xung đột trước khi tạo/cập nhật event
    """
    return service_check_event_overlap(db, current_user.id, overlap_check) 