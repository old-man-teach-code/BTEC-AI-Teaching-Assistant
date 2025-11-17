from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FolderBase(BaseModel):
    """Base schema cho Folder"""
    name: str = Field(..., min_length=1, max_length=255, description="Tên folder")
    description: Optional[str] = Field(None, max_length=512, description="Mô tả folder")
    parent_id: Optional[int] = Field(None, description="ID của folder cha")


class FolderCreate(FolderBase):
    """Schema cho việc tạo folder mới"""
    pass


class FolderUpdate(BaseModel):
    """Schema cho việc cập nhật folder"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Tên folder mới")
    description: Optional[str] = Field(None, max_length=512, description="Mô tả folder mới")
    parent_id: Optional[int] = Field(None, description="ID folder cha mới")


class FolderMove(BaseModel):
    """Schema cho việc di chuyển folder"""
    new_parent_id: Optional[int] = Field(None, description="ID của folder cha mới (None = root level)")


class FolderInDB(FolderBase):
    """Schema biểu diễn folder trong DB"""
    id: int
    owner_id: int
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FolderResponse(FolderInDB):
    """Schema cho response khi trả về folder cho client"""
    document_count: Optional[int] = Field(None, description="Số lượng documents trong folder")
    subfolder_count: Optional[int] = Field(None, description="Số lượng subfolders")


class FolderTreeNode(BaseModel):
    """Schema cho folder tree node"""
    id: int
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    document_count: int = 0
    subfolder_count: int = 0
    children: List['FolderTreeNode'] = []
    created_at: datetime

    class Config:
        from_attributes = True


class FolderListResponse(BaseModel):
    """Schema trả về danh sách folders kèm metadata"""
    total: int
    items: List[FolderResponse]

    class Config:
        from_attributes = True


class FolderTreeResponse(BaseModel):
    """Schema trả về folder tree structure"""
    total: int
    tree: List[FolderTreeNode]

    class Config:
        from_attributes = True


class FolderTrashResponse(BaseModel):
    """Schema cho response danh sách folders trong trash"""
    total: int
    items: List[FolderResponse]

    class Config:
        from_attributes = True


class DocumentMove(BaseModel):
    """Schema cho việc di chuyển document vào folder"""
    folder_id: Optional[int] = Field(None, description="ID của folder đích (None = root level)")


class FolderContentItem(BaseModel):
    """Schema cho một item trong folder (có thể là folder hoặc document)"""
    id: int
    name: str
    type: str = Field(..., description="Loại item: 'folder' hoặc 'document'")
    size: Optional[int] = Field(None, description="Kích thước file (bytes) - chỉ có cho documents")
    size_formatted: Optional[str] = Field(None, description="Kích thước file đã format (KB, MB)")
    file_type: Optional[str] = Field(None, description="Loại file - chỉ có cho documents")
    extension: Optional[str] = Field(None, description="Extension của file")
    document_count: Optional[int] = Field(None, description="Số documents trong folder - chỉ có cho folders")
    subfolder_count: Optional[int] = Field(None, description="Số subfolders - chỉ có cho folders")
    total_size: Optional[int] = Field(None, description="Tổng kích thước của folder - chỉ có cho folders")
    total_size_formatted: Optional[str] = Field(None, description="Tổng kích thước folder đã format")
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class FolderContentResponse(BaseModel):
    """Schema trả về nội dung folder với sorting và filtering"""
    total: int = Field(..., description="Tổng số items (không phân trang)")
    items: List[FolderContentItem] = Field(..., description="Danh sách items trong folder")
    folder_info: Optional[FolderResponse] = Field(None, description="Thông tin folder hiện tại (None nếu là root)")
    
    class Config:
        from_attributes = True


# Update forward references
try:
    FolderTreeNode.model_rebuild()
except AttributeError:
    # For older Pydantic versions
    FolderTreeNode.update_forward_refs()
