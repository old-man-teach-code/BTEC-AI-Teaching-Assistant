from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DocumentBase(BaseModel):
    """Schema cơ bản cho document, chứa các trường dùng chung"""
    original_name: str  # Tên gốc của file


class DocumentCreate(DocumentBase):
    """Schema dùng khi tạo document mới (không cần các trường tự sinh)"""
    # Các trường đặc trưng khi tạo document sẽ được thêm vào đây (nếu có)
    pass


class DocumentUpdate(BaseModel):
    """Schema dùng khi cập nhật thông tin document"""
    original_name: Optional[str] = None  # Cho phép cập nhật tên gốc (nếu cần)
    status: Optional[str] = None  # Cho phép cập nhật trạng thái
    folder_id: Optional[int] = None  # Cho phép di chuyển document vào folder khác


class DocumentInDB(DocumentBase):
    """Schema biểu diễn document trong DB, bao gồm tất cả trường"""
    id: int
    filename: str
    file_path: str
    file_size: int
    file_type: str
    owner_id: int
    status: str
    folder_id: Optional[int] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Cho phép chuyển đổi từ ORM model sang Pydantic model


class DocumentResponse(DocumentInDB):
    """Schema cho response khi trả về document cho client"""
    folder_name: Optional[str] = None  # Tên folder chứa document (nếu có)


class DocumentListResponse(BaseModel):
    """Schema trả về danh sách documents kèm metadata"""
    total: int  # Tổng số documents (để phục vụ phân trang)
    items: List[DocumentResponse]  # Danh sách documents

    class Config:
        from_attributes = True


class DocumentRestoreRequest(BaseModel):
    """Schema cho request khôi phục document từ trash"""
    folder_id: Optional[int] = None  # Folder đích khi khôi phục (None = root level)


class DocumentTrashResponse(BaseModel):
    """Schema cho response danh sách documents trong trash"""
    total: int
    items: List[DocumentResponse]

    class Config:
        from_attributes = True