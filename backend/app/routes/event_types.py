from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from dependencies.deps import get_db, get_current_user
from schemas.event_type import EventTypeCreate, EventTypeUpdate, EventTypeResponse, EventTypeListResponse
from services.event_type_service import (
    service_get_event_types,
    service_get_event_type,
    service_create_event_type,
    service_update_event_type,
    service_delete_event_type,
    service_seed_default_event_types
)
from models.user import User

# Khởi tạo router
router = APIRouter(tags=["event_types"])


@router.get("/", response_model=EventTypeListResponse)
def get_event_types(
    skip: int = Query(0, ge=0, description="Số lượng records bỏ qua"),
    limit: int = Query(100, ge=1, le=1000, description="Số lượng records lấy tối đa"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách tất cả loại events
    
    Args:
        skip: Số lượng records bỏ qua
        limit: Số lượng records lấy tối đa
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        EventTypeListResponse: Danh sách loại events
    """
    return service_get_event_types(db, skip, limit)


@router.get("/{event_type_id}", response_model=EventTypeResponse)
def get_event_type(
    event_type_id: int = Path(..., gt=0, description="ID của loại event cần lấy"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy thông tin chi tiết một loại event
    
    Args:
        event_type_id: ID của loại event cần lấy
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        EventTypeResponse: Thông tin loại event
    """
    return service_get_event_type(db, event_type_id)


@router.post("/", response_model=EventTypeResponse, status_code=status.HTTP_201_CREATED)
def create_event_type(
    event_type_data: EventTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Tạo loại event mới
    
    Args:
        event_type_data: Dữ liệu loại event cần tạo
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        EventTypeResponse: Thông tin loại event đã tạo
    """
    return service_create_event_type(db, event_type_data)


@router.put("/{event_type_id}", response_model=EventTypeResponse)
def update_event_type(
    event_type_update: EventTypeUpdate,
    event_type_id: int = Path(..., gt=0, description="ID của loại event cần cập nhật"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cập nhật thông tin loại event
    
    Args:
        event_type_update: Dữ liệu cập nhật
        event_type_id: ID của loại event cần cập nhật
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        EventTypeResponse: Thông tin loại event đã cập nhật
    """
    return service_update_event_type(db, event_type_id, event_type_update)


@router.delete("/{event_type_id}")
def delete_event_type(
    event_type_id: int = Path(..., gt=0, description="ID của loại event cần xóa"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Xóa loại event
    
    Args:
        event_type_id: ID của loại event cần xóa
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        Dict: Thông báo kết quả xóa
    """
    return service_delete_event_type(db, event_type_id)


@router.post("/seed-defaults")
def seed_default_event_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Seed dữ liệu mặc định cho các loại event
    
    Args:
        db: Database session
        current_user: User hiện tại (từ token)
        
    Returns:
        Dict: Thông báo kết quả
    """
    return service_seed_default_event_types(db) 