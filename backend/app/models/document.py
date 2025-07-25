from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from database.session import Base
import enum

class DocumentStatus(str, enum.Enum):
    """Enum cho trạng thái của document"""
    UPLOADED = "uploaded"    # Trạng thái khi mới upload
    PROCESSING = "processing"  # Trạng thái đang xử lý
    READY = "ready"          # Trạng thái đã xử lý xong, sẵn sàng sử dụng
    DELETED = "deleted"      # Trạng thái đã bị xóa mềm

class Document(Base):
    """
    Model cho Document
    
    Lưu trữ thông tin về các tài liệu được tải lên hệ thống
    """
    __tablename__ = "documents"
    
    # ID của document
    id = Column(Integer, primary_key=True, index=True)
    
    # Tên file hệ thống (đã được generate unique)
    filename = Column(String(255), nullable=False)
    
    # Tên gốc của file được upload
    original_name = Column(String(255), nullable=False)
    
    # Đường dẫn tới file trên hệ thống
    file_path = Column(String(512), nullable=False)
    
    # Kích thước file (bytes)
    file_size = Column(Integer, nullable=False)
    
    # Loại file (MIME type)
    file_type = Column(String(100), nullable=False)
    
    # ID của user sở hữu document này
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Trạng thái của document
    status = Column(String(20), default=DocumentStatus.UPLOADED.value, nullable=False)
    
    # Thời gian tạo document
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Thời gian cập nhật document
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Trash system fields
    # Đánh dấu document đã bị xóa mềm
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)

    # Thời gian xóa mềm (để tính toán auto-cleanup)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Folder system field với proper foreign key
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True, index=True)

    # Relationship với User model - back_populates sẽ map với thuộc tính tương ứng ở User model
    owner = relationship("User", back_populates="documents")

    # Relationship với Folder model
    folder = relationship("Folder", back_populates="documents")