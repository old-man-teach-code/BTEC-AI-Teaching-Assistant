from pydantic import BaseModel, validator
from datetime import datetime
from typing import List, Dict, Any, Optional

class TemplateBase(BaseModel):
    """Base template schema"""
    name: str
    content: str
    category: str
    variables: List[str] = []  # Example: ["student_name", "deadline", "subject"]
    
    @validator('category')
    def validate_category(cls, v):
        """Validate template category"""
        allowed_categories = ['greeting', 'deadline', 'homework', 'assignment', 'general', 'reminder', 'feedback']
        if v not in allowed_categories:
            raise ValueError(f'Category must be one of: {", ".join(allowed_categories)}')
        return v
    
    @validator('variables')
    def validate_variables(cls, v):
        """Validate variables list"""
        if not isinstance(v, list):
            raise ValueError('Variables must be a list')
        return v

class TemplateCreate(TemplateBase):
    """Schema for creating a new template"""
    pass

class TemplateUpdate(BaseModel):
    """Schema for updating a template (all fields optional)"""
    name: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    variables: Optional[List[str]] = None
    
    @validator('category')
    def validate_category(cls, v):
        if v is not None:
            allowed_categories = ['greeting', 'deadline', 'homework']
            if v not in allowed_categories:
                raise ValueError(f'Category must be one of: {", ".join(allowed_categories)}')
        return v

class Template(TemplateBase):
    """Schema for template response"""
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TemplatePreviewRequest(BaseModel):
    """Schema for template preview request"""
    sample_data: Dict[str, Any]
    
class TemplatePreviewResponse(BaseModel):
    """Schema for template preview response"""
    template_id: int
    rendered_content: str
    missing_variables: List[str] = []
    used_variables: List[str] = []