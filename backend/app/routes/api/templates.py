from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from dependencies.deps import get_db, get_current_user
from services.template_service import TemplateService
from schemas.template import (
    Template, 
    TemplateCreate, 
    TemplateUpdate, 
    TemplatePreviewRequest, 
    TemplatePreviewResponse
)
from models.user import User

router = APIRouter()


@router.post("", response_model=Template, summary="POST /templates - tạo mới")
def create_template(
    template: TemplateCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    service = TemplateService(db)
    return service.create_template(template, current_user.id)

@router.get("", response_model=List[Template], summary="GET /templates - list với filter category")
def list_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0, description="Number of templates to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of templates to return"),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    service = TemplateService(db)
    return service.get_templates(
        category=category, 
        user_id=current_user.id, 
        skip=skip, 
        limit=limit
    )

@router.put("/{template_id}", response_model=Template, summary="PUT /templates/{id} - update")
def update_template(
    template_id: int, 
    template_update: TemplateUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    service = TemplateService(db)
    return service.update_template(template_id, template_update, current_user.id)

@router.delete("/{template_id}", summary="DELETE /templates/{id}")
def delete_template(
    template_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    service = TemplateService(db)
    service.delete_template(template_id, current_user.id)
    return {"message": "Template deleted successfully"}


@router.post("/{template_id}/preview", response_model=TemplatePreviewResponse, summary="POST /templates/{id}/preview")
def preview_template(
    template_id: int, 
    preview_request: TemplatePreviewRequest,  
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        service = TemplateService(db)
        result = service.preview_template(template_id, preview_request, current_user.id)
        return result
    except Exception as e:
        print(f"Error in preview_template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to preview template: {str(e)}")
        