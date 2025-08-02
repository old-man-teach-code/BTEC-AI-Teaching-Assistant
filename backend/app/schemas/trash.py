from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class TrashItemIdentifier(BaseModel):
    """Schema để xác định một item trong trash"""
    id: int = Field(..., gt=0, description="ID của item")
    type: str = Field(..., description="Loại item: 'document' hoặc 'folder'")
    
    class Config:
        schema_extra = {
            "example": {
                "id": 123,
                "type": "document"
            }
        }


class BulkHardDeleteRequest(BaseModel):
    """Schema cho request xóa cứng nhiều items từ trash"""
    items: List[TrashItemIdentifier] = Field(
        ..., 
        min_items=1, 
        max_items=100,
        description="Danh sách items cần xóa cứng (tối đa 100 items)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {"id": 123, "type": "document"},
                    {"id": 456, "type": "folder"},
                    {"id": 789, "type": "document"}
                ]
            }
        }


class DeletedItemInfo(BaseModel):
    """Schema thông tin item đã được xóa"""
    id: int
    type: str
    name: str
    deleted_at: datetime
    
    class Config:
        from_attributes = True


class FailedItemInfo(BaseModel):
    """Schema thông tin item không thể xóa"""
    id: int
    type: str
    reason: str
    
    class Config:
        schema_extra = {
            "example": {
                "id": 123,
                "type": "document",
                "reason": "Item không tồn tại trong trash"
            }
        }


class BulkHardDeleteResponse(BaseModel):
    """Schema cho response xóa cứng nhiều items"""
    message: str
    total_requested: int = Field(..., description="Tổng số items được yêu cầu xóa")
    successfully_deleted: int = Field(..., description="Số items đã xóa thành công")
    failed_to_delete: int = Field(..., description="Số items không thể xóa")
    deleted_items: List[DeletedItemInfo] = Field(default=[], description="Danh sách items đã xóa thành công")
    failed_items: List[FailedItemInfo] = Field(default=[], description="Danh sách items không thể xóa")
    operation_completed_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "message": "Đã xóa vĩnh viễn 2/3 items từ trash",
                "total_requested": 3,
                "successfully_deleted": 2,
                "failed_to_delete": 1,
                "deleted_items": [
                    {
                        "id": 123,
                        "type": "document",
                        "name": "example.pdf",
                        "deleted_at": "2023-12-01T10:30:00Z"
                    }
                ],
                "failed_items": [
                    {
                        "id": 456,
                        "type": "folder",
                        "reason": "Folder không tồn tại trong trash"
                    }
                ],
                "operation_completed_at": "2023-12-01T10:35:00Z"
            }
        }
