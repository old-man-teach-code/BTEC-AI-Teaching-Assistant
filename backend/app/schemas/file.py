from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class FileResponse(BaseModel):
    """Schema cho thông tin file đã upload"""
    filename: str
    original_filename: str
    content_type: str
    size: int
    path: str
    full_path: Optional[str] = None
    
class FileListItem(BaseModel):
    """Schema cho item trong danh sách file"""
    filename: str
    path: str
    size: int
    extension: str
    
class FileListResponse(BaseModel):
    """Schema cho danh sách file"""
    files: List[Dict[str, Any]]
    total: int
    
class FileDeleteResponse(BaseModel):
    """Schema cho kết quả xóa file"""
    success: bool
    message: str 