from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from crud import template as template_crud
from schemas.template import TemplateCreate, TemplateUpdate, TemplatePreviewRequest, TemplatePreviewResponse
import re

class TemplateService:
    """Service for managing templates and rendering"""
    
    def __init__(self, db: Session):
        self.db = db

    def create_template(self, template: TemplateCreate, user_id: int):
        """Create a new template"""
        return template_crud.create_template(self.db, template, user_id)

    def get_templates(self, category: str = None, user_id: int = None, skip: int = 0, limit: int = 100):
        """Get templates with optional filtering"""
        return template_crud.get_templates(
            self.db, 
            skip=skip, 
            limit=limit, 
            category=category, 
            user_id=user_id
        )

    def get_template(self, template_id: int, user_id: int = None):
        """Get single template with optional ownership check"""
        if user_id:
            return template_crud.get_template_with_ownership_check(self.db, template_id, user_id)
        return template_crud.get_template(self.db, template_id)

    def update_template(self, template_id: int, template_update: TemplateUpdate, user_id: int):
        """Update template with ownership verification"""
        result = template_crud.update_template(self.db, template_id, template_update, user_id)
        if not result:
            raise HTTPException(status_code=404, detail="Template not found or not authorized")
        return result

    def delete_template(self, template_id: int, user_id: int):
        """Delete template with ownership verification"""
        success = template_crud.delete_template(self.db, template_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Template not found or not authorized")
        return True
        
    def preview_template(self, template_id: int, preview_request: TemplatePreviewRequest, user_id: int = None) -> TemplatePreviewResponse:
        """Preview template with sample data"""
        template = self.get_template(template_id, user_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
            
        # Extract variables from template content
        template_variables = self._extract_variables_from_content(template.content)
        
        # Check for missing variables
        provided_variables = set(preview_request.sample_data.keys())
        missing_variables = [var for var in template_variables if var not in provided_variables]
        used_variables = [var for var in template_variables if var in provided_variables]
        
        # Render template
        rendered_content = self.render_template(template.content, preview_request.sample_data)
        
        return TemplatePreviewResponse(
            template_id=template_id,
            rendered_content=rendered_content,
            missing_variables=missing_variables,
            used_variables=used_variables
        )

    def render_template(self, template_content: str, data: Dict[str, Any]) -> str:
        result = template_content
        
        def get_nested_value(obj: Dict[str, Any], path: str) -> Any:
            """Get value from nested dictionary using dot notation like user.name"""
            parts = path.split('.')
            current = obj
            
            try:
                for part in parts:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        return None
                return current
            except (KeyError, TypeError):
                return None
            

        variables = re.findall(r'{{([\w.]+)}}', template_content)
        
        for var in variables:
            value = get_nested_value(data, var)
            placeholder = '{{' + var + '}}'
            
            if value is not None:
                # Replace with actual value
                result = result.replace(placeholder, str(value))
            # If value is None, leave placeholder as is (or you could replace with empty string)
        
        return result
    
    def _extract_variables_from_content(self, content: str) -> List[str]:
        """Extract all variable names from template content"""
        return re.findall(r'{{([\w.]+)}}', content)
    
    def search_templates(self, search_term: str, user_id: int = None, category: str = None):
        """Search templates by name or content"""
        return template_crud.search_templates(self.db, search_term, user_id, category)
    
    def get_template_categories(self, user_id: int = None) -> List[str]:
        """Get list of available template categories"""
        categories = ['greeting', 'deadline', 'homework']
        return categories
    
    def validate_template_variables(self, content: str, declared_variables: List[str]) -> Dict[str, Any]:
        """Validate that declared variables match those used in content"""
        content_variables = set(self._extract_variables_from_content(content))
        declared_set = set(declared_variables)
        
        return {
            'content_variables': list(content_variables),
            'declared_variables': declared_variables,
            'missing_declarations': list(content_variables - declared_set),
            'unused_declarations': list(declared_set - content_variables),
            'is_valid': content_variables == declared_set
        }
