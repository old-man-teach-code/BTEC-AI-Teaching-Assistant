from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from models.notification import NotificationStatus, NotificationCategory


class NotificationBase(BaseModel):
    """Schema cơ bản cho notification, chứa các trường dùng chung"""
    title: str = Field(..., min_length=1, max_length=255, description="Tiêu đề notification")
    category: NotificationCategory = Field(..., description="Danh mục notification")
    message: str = Field(..., min_length=1, description="Nội dung thông báo")
    event_id: Optional[int] = Field(None, description="ID event liên quan (nếu có)")


class NotificationCreate(NotificationBase):
    """Schema dùng khi tạo notification mới"""
    user_id: int = Field(..., description="ID user nhận notification")


class NotificationUpdate(BaseModel):
    """Schema dùng khi cập nhật notification"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Tiêu đề notification")
    category: Optional[NotificationCategory] = Field(None, description="Danh mục notification")
    message: Optional[str] = Field(None, min_length=1, description="Nội dung thông báo")
    status: Optional[NotificationStatus] = Field(None, description="Trạng thái notification")


class NotificationStatusUpdate(BaseModel):
    """Schema chỉ dùng để cập nhật trạng thái notification"""
    status: NotificationStatus = Field(..., description="Trạng thái mới của notification")


class NotificationInDB(NotificationBase):
    """Schema biểu diễn notification trong DB, bao gồm tất cả trường"""
    id: int
    user_id: int
    status: NotificationStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationResponse(NotificationInDB):
    """Schema cho response khi trả về notification cho client"""
    # Có thể thêm thông tin user hoặc event nếu cần
    pass


class NotificationListResponse(BaseModel):
    """Schema trả về danh sách notifications kèm metadata"""
    total: int = Field(..., description="Tổng số notifications để phục vụ phân trang")
    unread_count: int = Field(..., description="Số notifications chưa đọc")
    items: List[NotificationResponse] = Field(..., description="Danh sách notifications")

    class Config:
        from_attributes = True


class NotificationMarkAsReadRequest(BaseModel):
    """Schema để đánh dấu nhiều notifications là đã đọc"""
    notification_ids: List[int] = Field(..., description="Danh sách ID notifications cần đánh dấu")


class NotificationStatsResponse(BaseModel):
    """Schema trả về thống kê notifications của user"""
    total: int = Field(..., description="Tổng số notifications")
    unread: int = Field(..., description="Số notifications chưa đọc")
    read: int = Field(..., description="Số notifications đã đọc")
    pending_response: int = Field(..., description="Số notifications chưa phản hồi")
    responded: int = Field(..., description="Số notifications đã phản hồi")
    by_category: dict = Field(..., description="Thống kê theo danh mục")

    class Config:
        from_attributes = True
