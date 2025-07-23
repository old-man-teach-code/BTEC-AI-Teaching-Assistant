from fastapi import APIRouter
from .api import templates

api_router = APIRouter()

# Include template routes with proper prefix and tags
api_router.include_router(
    templates.router, 
    prefix="/templates", 
    tags=["templates"]
)
