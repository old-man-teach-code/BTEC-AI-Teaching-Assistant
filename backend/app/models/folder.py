from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from database.session import Base


class Folder(Base):
    """
    Model cho Folder
    
    Lưu trữ thông tin về các thư mục để tổ chức documents
    """
    __tablename__ = "folders"
    
    # ID của folder
    id = Column(Integer, primary_key=True, index=True)
    
    # Tên folder
    name = Column(String(255), nullable=False)
    
    # Mô tả folder (tùy chọn)
    description = Column(String(512), nullable=True)
    
    # ID của user sở hữu folder này
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # ID của folder cha (để tạo nested folders)
    parent_id = Column(Integer, ForeignKey("folders.id"), nullable=True, index=True)
    
    # Trash system fields
    # Đánh dấu folder đã bị xóa mềm
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    
    # Thời gian xóa mềm
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Thời gian tạo folder
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Thời gian cập nhật folder
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    # Relationship với User model
    owner = relationship("User", back_populates="folders")
    
    # Relationship với Document model
    documents = relationship("Document", back_populates="folder", cascade="all, delete-orphan")
    
    # Self-referential relationship cho nested folders
    # Parent folder
    parent = relationship("Folder", remote_side=[id], back_populates="children")
    
    # Child folders
    children = relationship("Folder", back_populates="parent", cascade="all, delete-orphan")
