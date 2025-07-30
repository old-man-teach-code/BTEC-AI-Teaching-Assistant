from pydantic import BaseModel
from typing import Optional, List

class FileResponse(BaseModel):
    """Schema cho thông tin file đã upload"""
    filename: str
    original_filename: str
    content_type: str
    size: int
    path: str
    
class FileListItem(BaseModel):
    """Schema cho item trong danh sách file"""
    filename: str
    path: str
    size: int
    extension: str
    
class FileListResponse(BaseModel):
    """Schema cho danh sách file"""
    files: List[FileListItem]
    total: int
    
class FileDeleteResponse(BaseModel):
    """Schema cho response xóa file"""
    success: bool
    message: str 