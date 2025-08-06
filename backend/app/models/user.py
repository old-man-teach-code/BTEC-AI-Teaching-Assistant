from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from database.session import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), index=True)
    email = Column(String(120), unique=True, index=True)
    hashed_password = Column(String(256))
    discord_user_id = Column(String(64), nullable=True) 

    # Thêm trường created_at (thời gian tạo tài khoản)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Thêm relationship với Document model
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")

    # Thêm relationship với Event model
    events = relationship("Event", back_populates="owner", cascade="all, delete-orphan")

    # Thêm relationship với Folder model
    folders = relationship("Folder", back_populates="owner", cascade="all, delete-orphan")

    templates = relationship("Template", back_populates="owner", cascade="all, delete-orphan")

    # Thêm relationship với Notification model
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
