from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class EventBase(BaseModel):
    """Schema cơ bản cho event, chứa các trường dùng chung"""
    title: str = Field(..., min_length=1, max_length=255, description="Tiêu đề event")
    description: Optional[str] = Field(None, description="Mô tả chi tiết event")
    start_time: datetime = Field(..., description="Thời gian bắt đầu event")
    end_time: datetime = Field(..., description="Thời gian kết thúc event")
    location: Optional[str] = Field(None, max_length=255, description="Địa điểm tổ chức event")
    reminder_minutes: int = Field(15, ge=0, le=1440, description="Số phút nhắc nhở trước event (0-1440)")
    is_all_day: bool = Field(False, description="Event cả ngày hay không")
    event_type: Optional[str] = Field(None, max_length=50, description="Loại event (tự do nhập)")

    @validator('end_time')
    def validate_end_time(cls, v, values):
        """Kiểm tra thời gian kết thúc phải sau thời gian bắt đầu"""
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('Thời gian kết thúc phải sau thời gian bắt đầu')
        return v


class EventCreate(EventBase):
    """Schema dùng khi tạo event mới"""
    pass


class EventUpdate(BaseModel):
    """Schema dùng khi cập nhật thông tin event"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Tiêu đề event")
    description: Optional[str] = Field(None, description="Mô tả chi tiết event")
    start_time: Optional[datetime] = Field(None, description="Thời gian bắt đầu event")
    end_time: Optional[datetime] = Field(None, description="Thời gian kết thúc event")
    location: Optional[str] = Field(None, max_length=255, description="Địa điểm tổ chức event")
    reminder_minutes: Optional[int] = Field(None, ge=0, le=1440, description="Số phút nhắc nhở trước event (0-1440)")
    is_all_day: Optional[bool] = Field(None, description="Event cả ngày hay không")
    event_type: Optional[str] = Field(None, max_length=50, description="Loại event (tự do nhập)")

    @validator('end_time')
    def validate_end_time(cls, v, values):
        """Kiểm tra thời gian kết thúc phải sau thời gian bắt đầu"""
        if v is not None and 'start_time' in values and values['start_time'] is not None:
            if v <= values['start_time']:
                raise ValueError('Thời gian kết thúc phải sau thời gian bắt đầu')
        return v


class EventInDB(EventBase):
    """Schema biểu diễn event trong DB, bao gồm tất cả trường"""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Cho phép chuyển đổi từ ORM model sang Pydantic model


class EventResponse(EventInDB):
    """Schema cho response khi trả về event cho client"""
    pass


class EventListResponse(BaseModel):
    """Schema trả về danh sách events kèm metadata"""
    total: int = Field(..., description="Tổng số events để phục vụ phân trang")
    items: List[EventResponse] = Field(..., description="Danh sách events")

    class Config:
        from_attributes = True


class EventOverlapCheck(BaseModel):
    """Schema để kiểm tra xung đột thời gian"""
    start_time: datetime = Field(..., description="Thời gian bắt đầu để kiểm tra")
    end_time: datetime = Field(..., description="Thời gian kết thúc để kiểm tra")
    event_type: Optional[str] = Field(None, max_length=50, description="Loại event để kiểm tra xung đột (chỉ kiểm tra với cùng loại)")
    exclude_event_id: Optional[int] = Field(None, description="ID event cần loại trừ khi kiểm tra (dùng khi update)")

    @validator('end_time')
    def validate_end_time(cls, v, values):
        """Kiểm tra thời gian kết thúc phải sau thời gian bắt đầu"""
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('Thời gian kết thúc phải sau thời gian bắt đầu')
        return v