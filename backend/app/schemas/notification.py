from pydantic import BaseModel, Field, validator
from datetime import datetime, timezone
from typing import Optional
from models.notification import (
    NotificationType,
    NotificationEventStatus,
    NotificationRespondStatus,
    NotificationGeneralStatus
)


class NotificationBase(BaseModel):
    """
    Base schema cho Notification
    
    Validation rules theo notification_type:
    - RESPOND: event_id=null, scheduled_at=null
    - EVENT: event_id=required, scheduled_at=null  
    - GENERAL: event_id=null, scheduled_at=required (future time)
    """
    notification_type: NotificationType = Field(..., description="Loại thông báo: respond/event/general")
    title: str = Field(..., min_length=1, max_length=255, description="Tiêu đề thông báo")
    message: str = Field(..., min_length=1, description="Nội dung thông báo")
    user_id: int = Field(..., gt=0, description="ID người nhận")
    event_id: Optional[int] = Field(None, gt=0, description="ID sự kiện (chỉ cho EVENT type, null cho RESPOND/GENERAL)")
    scheduled_at: Optional[datetime] = Field(None, description="Thời gian lập lịch (chỉ cho GENERAL type, null cho EVENT/RESPOND)")

    @validator('event_id')
    def validate_event_id(cls, v, values):
        """Validate event_id theo notification_type"""
        notification_type = values.get('notification_type')
        
        if notification_type == NotificationType.EVENT:
            if v is None:
                raise ValueError('event_id is required for EVENT notifications')
        else:  # RESPOND hoặc GENERAL
            if v is not None:
                raise ValueError('event_id must be null for RESPOND and GENERAL notifications')
        return v

    @validator('scheduled_at')
    def validate_scheduled_at(cls, v, values):
        """Validate scheduled_at theo notification_type"""
        notification_type = values.get('notification_type')
        
        if notification_type == NotificationType.GENERAL:
            if v is None:
                raise ValueError('scheduled_at is required for GENERAL notifications')
            # Kiểm tra thời gian không được trong quá khứ
            # Convert cả hai datetime về UTC để so sánh
            if v.tzinfo is not None:
                # v có timezone, convert datetime.now() sang UTC
                current_time = datetime.now(timezone.utc)
            else:
                # v không có timezone, dùng datetime.now() local
                current_time = datetime.now()
            
            if v <= current_time:
                raise ValueError('scheduled_at must be in the future for GENERAL notifications')
        else:  # EVENT hoặc RESPOND
            if v is not None:
                raise ValueError('scheduled_at must be null for EVENT and RESPOND notifications')
        return v


class NotificationCreate(NotificationBase):
    """Schema tạo notification mới"""
    pass


class NotificationUpdate(BaseModel):
    """Schema cập nhật notification"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    message: Optional[str] = Field(None, min_length=1)
    scheduled_at: Optional[datetime] = None
    event_status: Optional[NotificationEventStatus] = None
    respond_status: Optional[NotificationRespondStatus] = None
    general_status: Optional[NotificationGeneralStatus] = None


class NotificationStatusUpdate(BaseModel):
    """Schema cập nhật trạng thái thông báo"""
    event_status: Optional[NotificationEventStatus] = None
    respond_status: Optional[NotificationRespondStatus] = None
    general_status: Optional[NotificationGeneralStatus] = None


class NotificationRespondStatusUpdate(BaseModel):
    """Schema cập nhật trạng thái RESPOND theo message"""
    message: str = Field(..., min_length=1, description="Nội dung thông báo cần cập nhật")
    respond_status: NotificationRespondStatus = Field(..., description="Trạng thái phản hồi mới")


class NotificationGeneralStatusUpdate(BaseModel):
    """Schema cập nhật trạng thái GENERAL theo message"""
    message: str = Field(..., min_length=1, description="Nội dung thông báo cần cập nhật")
    general_status: NotificationGeneralStatus = Field(..., description="Trạng thái general mới")


class NotificationFilterByStatus(BaseModel):
    """Schema lọc thông báo theo loại và trạng thái"""
    notification_type: NotificationType = Field(..., description="Loại thông báo")
    event_status: Optional[NotificationEventStatus] = Field(None, description="Trạng thái EVENT (chỉ cho EVENT type)")
    respond_status: Optional[NotificationRespondStatus] = Field(None, description="Trạng thái RESPOND (chỉ cho RESPOND type)")
    general_status: Optional[NotificationGeneralStatus] = Field(None, description="Trạng thái GENERAL (chỉ cho GENERAL type)")
    
    @validator('event_status')
    def validate_event_status(cls, v, values):
        """Validate event_status chỉ dùng cho EVENT type"""
        notification_type = values.get('notification_type')
        if notification_type == NotificationType.EVENT:
            if v is None:
                raise ValueError('event_status is required for EVENT notifications')
        else:
            if v is not None:
                raise ValueError('event_status can only be used with EVENT notifications')
        return v
    
    @validator('respond_status')
    def validate_respond_status(cls, v, values):
        """Validate respond_status chỉ dùng cho RESPOND type"""
        notification_type = values.get('notification_type')
        if notification_type == NotificationType.RESPOND:
            if v is None:
                raise ValueError('respond_status is required for RESPOND notifications')
        else:
            if v is not None:
                raise ValueError('respond_status can only be used with RESPOND notifications')
        return v
    
    @validator('general_status')
    def validate_general_status(cls, v, values):
        """Validate general_status chỉ dùng cho GENERAL type"""
        notification_type = values.get('notification_type')
        if notification_type == NotificationType.GENERAL:
            if v is None:
                raise ValueError('general_status is required for GENERAL notifications')
        else:
            if v is not None:
                raise ValueError('general_status can only be used with GENERAL notifications')
        return v


class NotificationResponse(NotificationBase):
    """Schema response cho notification"""
    id: int
    event_status: Optional[NotificationEventStatus] = None
    respond_status: Optional[NotificationRespondStatus] = None
    general_status: Optional[NotificationGeneralStatus] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema response cho danh sách notifications"""
    total: int
    notifications: list[NotificationResponse]


class NotificationStatsResponse(BaseModel):
    """Schema response cho thống kê notifications"""
    total: int
    by_type: dict

    class Config:
        from_attributes = True
