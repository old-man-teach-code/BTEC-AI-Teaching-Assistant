from sqlalchemy.orm import Session
from typing import List, Optional
from crud.message import (
    get_message,
    get_messages_by_thread,
    get_messages,
    create_message,
    update_message,
    delete_message,
    count_messages_by_thread,
    search_message_by_content_and_dname
)
from schemas.message import MessageCreate, MessageUpdate, MessageRead, MessageSearch
from models.message import Message

class MessageService:
    """Service layer cho Message operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_new_message(self, message_data: MessageCreate) -> MessageRead:
        """Tạo message mới"""
        db_message = create_message(self.db, message_data)
        return MessageRead.from_orm(db_message)
    
    def get_message_by_id(self, message_id: int) -> Optional[MessageRead]:
        """Lấy message theo ID"""
        db_message = get_message(self.db, message_id)
        if db_message:
            return MessageRead.from_orm(db_message)
        return None
    
    def get_thread_messages(self, thread_id: str, skip: int = 0, limit: int = 100) -> List[MessageRead]:
        """Lấy danh sách messages của một thread"""
        db_messages = get_messages_by_thread(self.db, thread_id, skip, limit)
        return [MessageRead.from_orm(message) for message in db_messages]
    
    def get_all_messages(self, skip: int = 0, limit: int = 100) -> List[MessageRead]:
        """Lấy danh sách tất cả messages"""
        db_messages = get_messages(self.db, skip, limit)
        return [MessageRead.from_orm(message) for message in db_messages]
    
    def update_message_by_id(self, message_id: int, message_update: MessageUpdate) -> Optional[MessageRead]:
        """Cập nhật message"""
        db_message = update_message(self.db, message_id, message_update)
        if db_message:
            return MessageRead.from_orm(db_message)
        return None
    
    def delete_message_by_id(self, message_id: int) -> bool:
        """Xóa message"""
        return delete_message(self.db, message_id)
    
    def get_thread_message_count(self, thread_id: str) -> int:
        """Đếm số lượng messages trong thread"""
        return count_messages_by_thread(self.db, thread_id)
    
    def search_message_by_content_and_dname(self, content: str, dName: str) -> Optional[MessageRead]:
        """Tìm kiếm message theo content và dName"""
        db_message = search_message_by_content_and_dname(self.db, content, dName)
        if db_message:
            return MessageRead.from_orm(db_message)
        return None