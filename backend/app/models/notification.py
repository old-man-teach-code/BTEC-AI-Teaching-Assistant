from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, func
from sqlalchemy.orm import relationship
from database.session import Base
import enum

class NotificationStatus(enum.Enum):
    """Enum cho trạng thái của notification"""
    UNREAD = "unread"  # Chưa đọc
    READ = "read"      # Đã đọc
    PENDING_RESPONSE = "pending_response"  # Chưa phản hồi
    RESPONDED = "responded"  # Đã phản hồi

class NotificationCategory(enum.Enum):
    """Enum cho danh mục notification"""
    EVENT_REMINDER = "event_reminder"  # Nhắc nhở sự kiện
    EVENT_UPDATE = "event_update"      # Cập nhật sự kiện  
    SYSTEM = "system"                  # Thông báo hệ thống
    GENERAL = "general"                # Thông báo chung

class Notification(Base):
    """
    Model cho Notification system
    
    Lưu trữ thông tin các thông báo gửi đến user liên quan đến events
    """
    __tablename__ = "notifications"

    # ID của notification - Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Tiêu đề của notification - Bắt buộc
    title = Column(String(255), nullable=False, index=True)

    # Danh mục của notification - Bắt buộc
    category = Column(Enum(NotificationCategory), nullable=False, index=True)

    # Nội dung thông báo - Bắt buộc
    message = Column(Text, nullable=False)

    # Trạng thái của notification - Mặc định là chưa đọc
    status = Column(Enum(NotificationStatus), default=NotificationStatus.UNREAD, nullable=False, index=True)

    # ID của user nhận notification - Foreign key tới bảng users
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # ID của event liên quan (nếu có) - Foreign key tới bảng events
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True, index=True)

    # Thời gian tạo notification - Tự động set khi tạo
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Thời gian cập nhật notification - Tự động update khi sửa
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Thời gian đọc notification (nếu đã đọc)
    read_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship với User model
    user = relationship("User", back_populates="notifications")

    # Relationship với Event model
    event = relationship("Event", back_populates="notifications")