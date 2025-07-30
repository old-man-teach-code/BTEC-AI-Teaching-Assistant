from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ProcessingStatus(str, Enum):
    """Enum cho trạng thái xử lý"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class DocumentType(str, Enum):
    """Enum cho loại document"""
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    TXT = "txt"
    UNKNOWN = "unknown"


# =================== Knowledge Extraction Schemas ===================

class DocumentUploadRequest(BaseModel):
    """Schema cho request upload document để extract knowledge"""
    user_id: int = Field(..., description="ID của user sở hữu document")
    document_id: int = Field(..., description="ID của document từ backend")
    file_path: str = Field(..., description="Đường dẫn file trên server")
    metadata: Optional[Dict[str, Any]] = Field(
        default={},
        description="Metadata bổ sung (course, subject, etc.)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "document_id": 123,
                "file_path": "/app/uploads/1_1234567890.pdf",
                "metadata": {
                    "course": "SE07102",
                    "subject": "Toán cao cấp",
                    "type": "syllabus"
                }
            }
        }


class ExtractionResult(BaseModel):
    """Schema cho kết quả extraction"""
    document_id: int
    status: ProcessingStatus
    chunks_extracted: int = Field(0, description="Số chunks đã extract")
    error_message: Optional[str] = None
    processing_time: Optional[float] = Field(None, description="Thời gian xử lý (seconds)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": 123,
                "status": "completed",
                "chunks_extracted": 45,
                "error_message": None,
                "processing_time": 3.2
            }
        }


class BatchExtractionRequest(BaseModel):
    """Schema cho batch extraction nhiều documents"""
    user_id: int
    document_ids: List[int] = Field(..., min_items=1, max_items=50)
    
    @validator('document_ids')
    def validate_unique_ids(cls, v):
        if len(v) != len(set(v)):
            raise ValueError('Document IDs phải unique')
        return v


class BatchExtractionResponse(BaseModel):
    """Response cho batch extraction"""
    total: int
    successful: int
    failed: int
    results: List[ExtractionResult]


# =================== Template Processing Schemas ===================

class TemplateVariable(BaseModel):
    """Schema cho một biến trong template"""
    name: str = Field(..., description="Tên biến (vd: deadline, subject)")
    description: Optional[str] = Field(None, description="Mô tả về biến")
    required: bool = Field(True, description="Biến bắt buộc hay không")
    default_value: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "deadline",
                "description": "Thời hạn nộp bài",
                "required": True,
                "default_value": None
            }
        }


class TemplateFillRequest(BaseModel):
    """Schema cho request điền template"""
    user_id: int = Field(..., description="ID của user")
    template_id: int = Field(..., description="ID của template từ backend")
    question: str = Field(..., description="Câu hỏi từ sinh viên")
    context: Optional[Dict[str, Any]] = Field(
        default={},
        description="Context bổ sung (course, student_name, etc.)"
    )
    use_rag: bool = Field(
        default=True,
        description="Có sử dụng RAG để tìm thông tin không"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "template_id": 456,
                "question": "Deadline ASM môn toán lớp SE07102 là khi nào?",
                "context": {
                    "course": "SE07102",
                    "student_name": "Nguyễn Văn A"
                },
                "use_rag": True
            }
        }


class FilledTemplate(BaseModel):
    """Schema cho template đã được điền"""
    template_id: int
    original_template: str = Field(..., description="Template gốc")
    filled_content: str = Field(..., description="Nội dung đã điền")
    variables_filled: Dict[str, str] = Field(
        ...,
        description="Các biến đã được điền và giá trị"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Độ tin cậy của việc điền template"
    )
    sources: List[str] = Field(
        default=[],
        description="Nguồn thông tin được sử dụng"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "template_id": 456,
                "original_template": "Deadline nộp bài là {{deadline}} cho môn {{subject}}",
                "filled_content": "Deadline nộp bài là 23:59 ngày 31/07/2025 cho môn Toán cao cấp",
                "variables_filled": {
                    "deadline": "23:59 ngày 31/07/2025",
                    "subject": "Toán cao cấp"
                },
                "confidence_score": 0.95,
                "sources": ["syllabus_toan_se07102.pdf", "calendar_july_2025.docx"]
            }
        }


class TemplateAnalysisRequest(BaseModel):
    """Schema để phân tích template và tìm variables"""
    template_content: str = Field(..., description="Nội dung template cần phân tích")
    
    class Config:
        json_schema_extra = {
            "example": {
                "template_content": "Chào {{student_name}}, deadline môn {{subject}} là {{deadline}}"
            }
        }


class TemplateAnalysisResponse(BaseModel):
    """Response cho template analysis"""
    variables: List[str] = Field(..., description="Danh sách variables tìm thấy")
    variable_details: List[TemplateVariable]
    template_valid: bool = Field(..., description="Template có hợp lệ không")
    suggestions: List[str] = Field(default=[], description="Gợi ý cải thiện template")


# =================== Search/Query Schemas ===================

class SearchRequest(BaseModel):
    """Schema cho search trong knowledge base"""
    user_id: int
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)
    search_scope: str = Field(
        default="user",
        description="Phạm vi search: 'user' hoặc 'global'"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default={},
        description="Filters cho metadata (course, type, etc.)"
    )
    
    @validator('search_scope')
    def validate_scope(cls, v):
        if v not in ['user', 'global']:
            raise ValueError('search_scope phải là "user" hoặc "global"')
        return v


class SearchResult(BaseModel):
    """Schema cho một kết quả search"""
    text: str = Field(..., description="Nội dung tìm thấy")
    score: float = Field(..., ge=0.0, le=1.0, description="Điểm similarity")
    metadata: Dict[str, Any] = Field(default={})
    source: Optional[str] = Field(None, description="Nguồn document")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Deadline nộp Assignment 1 môn Toán cao cấp là 23:59 ngày 31/07/2025",
                "score": 0.89,
                "metadata": {
                    "document_id": 123,
                    "page": 5,
                    "course": "SE07102"
                },
                "source": "syllabus_toan_se07102.pdf"
            }
        }


class SearchResponse(BaseModel):
    """Response cho search request"""
    query: str
    total_results: int
    results: List[SearchResult]
    search_time: float = Field(..., description="Thời gian search (seconds)")


# =================== Knowledge Management Schemas ===================

class KnowledgeStats(BaseModel):
    """Schema cho statistics về knowledge base"""
    user_id: int
    total_documents: int
    total_chunks: int
    last_updated: Optional[datetime] = None
    storage_used_mb: float = Field(0.0, description="Dung lượng sử dụng (MB)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "total_documents": 25,
                "total_chunks": 450,
                "last_updated": "2025-01-15T10:30:00",
                "storage_used_mb": 12.5
            }
        }


class DeleteKnowledgeRequest(BaseModel):
    """Schema để xóa knowledge"""
    user_id: int
    document_ids: Optional[List[int]] = Field(
        None,
        description="Danh sách document IDs cần xóa. Nếu None = xóa tất cả"
    )
    confirm: bool = Field(
        False,
        description="Xác nhận xóa (bắt buộc = True để xóa)"
    )


# =================== Health/Status Schemas ===================

class ServiceHealth(BaseModel):
    """Schema cho health check response"""
    service: str
    status: str
    components: Dict[str, str]
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"


class ComponentStatus(BaseModel):
    """Schema cho status của một component"""
    name: str
    status: str
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# =================== Error Response Schema ===================

class ErrorResponse(BaseModel):
    """Schema chuẩn cho error responses"""
    error: str = Field(..., description="Mô tả lỗi")
    detail: Optional[str] = Field(None, description="Chi tiết lỗi")
    code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Document not found",
                "detail": "Document với ID 999 không tồn tại",
                "code": "DOC_NOT_FOUND",
                "timestamp": "2025-01-15T10:30:00"
            }
        }