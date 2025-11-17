from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from models.message import Message
from schemas.message import MessageCreate, MessageUpdate

def get_message(db: Session, message_id: int) -> Optional[Message]:
    """Lấy message theo ID"""
    return db.query(Message).filter(Message.id == message_id).first()

def get_messages_by_thread(db: Session, thread_id: str, skip: int = 0, limit: int = 100) -> List[Message]:
    """Lấy danh sách messages theo threadId với phân trang"""
    return db.query(Message).filter(Message.threadId == thread_id).order_by(desc(Message.created_at)).offset(skip).limit(limit).all()

def get_messages(db: Session, skip: int = 0, limit: int = 100) -> List[Message]:
    """Lấy danh sách tất cả messages với phân trang"""
    return db.query(Message).order_by(desc(Message.created_at)).offset(skip).limit(limit).all()

def create_message(db: Session, message: MessageCreate) -> Message:
    """Tạo message mới"""
    db_message = Message(
        threadId=message.threadId,
        content=message.content,
        dName=message.dName
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def update_message(db: Session, message_id: int, message_update: MessageUpdate) -> Optional[Message]:
    """Cập nhật message"""
    db_message = db.query(Message).filter(Message.id == message_id).first()
    if db_message:
        update_data = message_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_message, field, value)
        db.commit()
        db.refresh(db_message)
    return db_message

def delete_message(db: Session, message_id: int) -> bool:
    """Xóa message"""
    db_message = db.query(Message).filter(Message.id == message_id).first()
    if db_message:
        db.delete(db_message)
        db.commit()
        return True
    return False

def count_messages_by_thread(db: Session, thread_id: str) -> int:
    """Đếm số lượng messages trong một thread"""
    return db.query(Message).filter(Message.threadId == thread_id).count()

def search_message_by_content_and_dname(db: Session, content: str, dName: str) -> Optional[Message]:
    """Tìm kiếm message theo content và dName"""
    return db.query(Message).filter(
        Message.content == content,
        Message.dName == dName
    ).first()