from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, func
from sqlalchemy.orm import relationship
from database.session import Base

class Event(Base):
    """
    Model cho Event trong calendar system

    Lưu trữ thông tin về các sự kiện/lịch hẹn của giảng viên
    """
    __tablename__ = "events"

    # ID của event - Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Tiêu đề của event - Bắt buộc
    title = Column(String(255), nullable=False, index=True)

    # Mô tả chi tiết của event - Có thể null
    description = Column(Text, nullable=True)

    # Thời gian bắt đầu event - Bắt buộc
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)

    # Thời gian kết thúc event - Bắt buộc
    end_time = Column(DateTime(timezone=True), nullable=False, index=True)

    # Địa điểm tổ chức event - Có thể null
    location = Column(String(255), nullable=True)

    # ID của user sở hữu event này - Foreign key tới bảng users
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Loại event - String tự do, frontend sẽ xử lý màu sắc
    event_type = Column(String(50), nullable=True, index=True, default="other")

    # Số phút nhắc nhở trước khi event diễn ra - Mặc định 15 phút
    reminder_minutes = Column(Integer, default=15, nullable=False)

    # Cờ đánh dấu event cả ngày hay không - Mặc định False
    is_all_day = Column(Boolean, default=False, nullable=False)

    # Thời gian tạo event - Tự động set khi tạo
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Thời gian cập nhật event - Tự động update khi sửa
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Relationship với User model - back_populates sẽ map với thuộc tính tương ứng ở User model
    owner = relationship("User", back_populates="events")

    # Đánh dấu đã gửi nhắc nhở chưa
    reminded = Column(Boolean, default=False, nullable=False)