from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, func
from sqlalchemy.orm import relationship
from database.session import Base
import enum

class NotificationType(enum.Enum):
    """Enum cho loại thông báo"""
    EVENT = "event"        # Thông báo sự kiện
    RESPOND = "respond"    # Thông báo cần phản hồi
    GENERAL = "general"    # Thông báo chung

class NotificationEventStatus(enum.Enum):
    """Enum cho trạng thái thông báo sự kiện"""
    UNREAD = "unread"  # Chưa đọc
    READ = "read"      # Đã đọc

class NotificationRespondStatus(enum.Enum):
    """Enum cho trạng thái thông báo phản hồi"""
    PENDING_RESPONSE = "pending_response"  # Chưa phản hồi
    RESPONDED = "responded"                # Đã phản hồi

class NotificationGeneralStatus(enum.Enum):
    """Enum cho trạng thái thông báo chung"""
    PENDING = "pending"  # Chưa gửi
    SENT = "sent"        # Đã gửi

class Notification(Base):
    """
    Model cho Notification system với 3 loại thông báo
    
    - EVENT: Thông báo sự kiện (có event_id)
    - RESPOND: Thông báo cần phản hồi (event_id = null) 
    - GENERAL: Thông báo chung có lập lịch (có scheduled_at)
    """
    __tablename__ = "notifications"

    # ID của notification - Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Loại thông báo - Bắt buộc
    notification_type = Column(Enum(NotificationType), nullable=False, index=True)

    # Tiêu đề của notification - Bắt buộc
    title = Column(String(255), nullable=False, index=True)

    # Nội dung thông báo - Bắt buộc
    message = Column(Text, nullable=False)

    # Trạng thái cho EVENT notifications (nullable)
    event_status = Column(Enum(NotificationEventStatus), nullable=True, index=True)

    # Trạng thái cho RESPOND notifications (nullable)
    respond_status = Column(Enum(NotificationRespondStatus), nullable=True, index=True)

    # Trạng thái cho GENERAL notifications (nullable)
    general_status = Column(Enum(NotificationGeneralStatus), nullable=True, index=True)

    # ID của user nhận notification - Foreign key tới bảng users
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # ID của event liên quan (chỉ cho EVENT type) - Foreign key tới bảng events
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True, default=None, index=True)

    # Thời gian lập lịch gửi (chỉ cho GENERAL type) - Nullable
    scheduled_at = Column(DateTime(timezone=True), nullable=True, default=None)

    # Thời gian tạo notification - Tự động set khi tạo
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationship với User model
    user = relationship("User", back_populates="notifications")

    # Relationship với Event model
    event = relationship("Event", back_populates="notifications")