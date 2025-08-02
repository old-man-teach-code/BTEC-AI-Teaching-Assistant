from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.template import Template
from schemas.template import TemplateCreate, TemplateUpdate
from typing import List, Optional

def create_template(db: Session, template: TemplateCreate, owner_id: int) -> Template:
    """Create a new template"""
    template_data = template.dict()
    db_template = Template(**template_data, owner_id=owner_id)
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

def get_template(db: Session, template_id: int) -> Optional[Template]:
    """Get template by ID"""
    return db.query(Template).filter(Template.id == template_id).first()

def get_template_with_ownership_check(db: Session, template_id: int, owner_id: int) -> Optional[Template]:
    """Get template by ID with ownership verification"""
    return db.query(Template).filter(
        and_(Template.id == template_id, Template.owner_id == owner_id)
    ).first()

def get_templates(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    user_id: Optional[int] = None
) -> List[Template]:
    """Get templates with optional filtering by category and user"""
    query = db.query(Template)
    
    if category:
        query = query.filter(Template.category == category)
    if user_id:
        query = query.filter(Template.owner_id == user_id)
        
    return query.offset(skip).limit(limit).all()

def get_templates_by_category(db: Session, category: str, owner_id: Optional[int] = None) -> List[Template]:
    """Get templates by category, optionally filtered by owner"""
    query = db.query(Template).filter(Template.category == category)
    if owner_id:
        query = query.filter(Template.owner_id == owner_id)
    return query.all()

def update_template(db: Session, template_id: int, template_update: TemplateUpdate, owner_id: int) -> Optional[Template]:
    """Update template with ownership check"""
    db_template = get_template_with_ownership_check(db, template_id, owner_id)
    if not db_template:
        return None
        
    update_data = template_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_template, key, value)
    
    db.commit()
    db.refresh(db_template)
    return db_template

def delete_template(db: Session, template_id: int, owner_id: int) -> bool:
    """Delete template with ownership check"""
    db_template = get_template_with_ownership_check(db, template_id, owner_id)
    if not db_template:
        return False
        
    db.delete(db_template)
    db.commit()
    return True

def get_user_templates_count(db: Session, user_id: int) -> int:
    """Get count of templates owned by user"""
    return db.query(Template).filter(Template.owner_id == user_id).count()

def search_templates(
    db: Session, 
    search_term: str, 
    user_id: Optional[int] = None,
    category: Optional[str] = None
) -> List[Template]:
    """Search templates by name or content"""
    query = db.query(Template).filter(
        Template.name.ilike(f"%{search_term}%") | 
        Template.content.ilike(f"%{search_term}%")
    )
    
    if user_id:
        query = query.filter(Template.owner_id == user_id)
    if category:
        query = query.filter(Template.category == category)
        
    return query.all()
