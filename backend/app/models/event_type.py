from sqlalchemy import Column, Integer, String, Text
from database.session import Base
import enum

class EventTypeEnum(str, enum.Enum):
    """
    Enum cho các loại event chuẩn
    """
    LECTURE = "lecture"      # Bài giảng
    ASSIGNMENT = "assignment"  # Bài tập
    EXAM = "exam"            # Thi
    MEETING = "meeting"      # Họp
    DEADLINE = "deadline"    # Deadline
    EVENT = "event"          # Sự kiện khác
    OTHER = "other"          # Khác

class EventType(Base):
    """
    Model cho các loại event và màu sắc tương ứng
    
    Mỗi loại event sẽ có màu riêng để hiển thị trên giao diện calendar
    """
    __tablename__ = "event_types"
    
    # ID của event type - Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Tên loại event - Bắt buộc
    name = Column(String(50), nullable=False, index=True, unique=True)
    
    # Mã màu hex - Bắt buộc (ví dụ: #1976d2)
    color = Column(String(7), nullable=False)
    
    # Mô tả loại event - Có thể null
    description = Column(Text, nullable=True)
    
    # Mã loại event (dùng để mapping với enum)
    code = Column(String(20), nullable=False, index=True, unique=True)
    
    @classmethod
    def get_default_types(cls):
        """
        Trả về danh sách các loại event mặc định
        """
        return [
            {
                "name": "Bài giảng",
                "color": "#1976d2",  # Xanh dương
                "description": "Các buổi giảng dạy",
                "code": EventTypeEnum.LECTURE
            },
            {
                "name": "Bài tập",
                "color": "#ff9800",  # Cam
                "description": "Thời hạn nộp bài tập",
                "code": EventTypeEnum.ASSIGNMENT
            },
            {
                "name": "Thi",
                "color": "#f44336",  # Đỏ
                "description": "Kỳ thi, kiểm tra",
                "code": EventTypeEnum.EXAM
            },
            {
                "name": "Họp",
                "color": "#9c27b0",  # Tím
                "description": "Cuộc họp",
                "code": EventTypeEnum.MEETING
            },
            {
                "name": "Deadline",
                "color": "#d32f2f",  # Đỏ đậm
                "description": "Các thời hạn quan trọng",
                "code": EventTypeEnum.DEADLINE
            },
            {
                "name": "Sự kiện",
                "color": "#4caf50",  # Xanh lá
                "description": "Sự kiện khác",
                "code": EventTypeEnum.EVENT
            },
            {
                "name": "Khác",
                "color": "#607d8b",  # Xám xanh
                "description": "Loại sự kiện khác",
                "code": EventTypeEnum.OTHER
            }
        ] 