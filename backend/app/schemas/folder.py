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


class DocumentMove(BaseModel):
    """Schema cho việc di chuyển document vào folder"""
    folder_id: Optional[int] = Field(None, description="ID của folder đích (None = root level)")


# Update forward references
try:
    FolderTreeNode.model_rebuild()
except AttributeError:
    # For older Pydantic versions
    FolderTreeNode.update_forward_refs()
