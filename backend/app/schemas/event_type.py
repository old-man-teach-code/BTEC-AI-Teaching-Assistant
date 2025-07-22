from pydantic import BaseModel, Field
from typing import Optional, List

class EventTypeBase(BaseModel):
    """Schema cơ bản cho event type, chứa các trường dùng chung"""
    name: str = Field(..., min_length=1, max_length=50, description="Tên loại event")
    color: str = Field(..., min_length=4, max_length=7, description="Mã màu hex (ví dụ: #1976d2)")
    description: Optional[str] = Field(None, description="Mô tả loại event")
    code: str = Field(..., min_length=1, max_length=20, description="Mã loại event (ví dụ: lecture)")


class EventTypeCreate(EventTypeBase):
    """Schema dùng khi tạo event type mới"""
    pass


class EventTypeUpdate(BaseModel):
    """Schema dùng khi cập nhật thông tin event type"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Tên loại event")
    color: Optional[str] = Field(None, min_length=4, max_length=7, description="Mã màu hex (ví dụ: #1976d2)")
    description: Optional[str] = Field(None, description="Mô tả loại event")


class EventTypeInDB(EventTypeBase):
    """Schema biểu diễn event type trong DB, bao gồm tất cả trường"""
    id: int

    class Config:
        from_attributes = True  # Cho phép chuyển đổi từ ORM model sang Pydantic model


class EventTypeResponse(EventTypeInDB):
    """Schema cho response khi trả về event type cho client"""
    pass


class EventTypeListResponse(BaseModel):
    """Schema trả về danh sách event types"""
    total: int = Field(..., description="Tổng số event types")
    items: List[EventTypeResponse] = Field(..., description="Danh sách event types")

    class Config:
        from_attributes = True 