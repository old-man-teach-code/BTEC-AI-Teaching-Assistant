from sqlalchemy import Column, Integer, String, Text, DateTime, func
from database.session import Base

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    threadId = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    dName = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)