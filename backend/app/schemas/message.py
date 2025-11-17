from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageBase(BaseModel):
    threadId: str
    content: str
    dName: Optional[str] = None

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    threadId: Optional[str] = None
    content: Optional[str] = None
    dName: Optional[str] = None

class MessageSearch(BaseModel):
    content: str
    dName: str

class MessageRead(MessageBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True