from sqlalchemy import Column, Integer, String, DateTime, func, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from database.session import Base

class Template(Base):
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(64), nullable=False, index=True)
    variables = Column(JSON, default=list)  # Example: ["student_name", "deadline", "subject"]
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    owner = relationship("User", back_populates="templates")

