from routes.api import user, files, documents, trash, folders, calendar, templates, notifications, stats, folder_contents, messages
from routes import auth, info, reminder
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies.deps import get_db
from core.jwt_middleware import JWTAuthMiddleware
from core.rate_limit import RateLimitMiddleware
from fastapi.middleware.cors import CORSMiddleware
from database.session import Base, engine
import os
import glob
import importlib
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()
protected_app = FastAPI(
    title="FastAPI + MySQL + Docker Compose",
    description="Basic template for FastAPI with MySQL and Docker Compose",
    version="1.0.0",
    doc_url="/api/docs",
)

@app.on_event("startup")
async def startup_event():
    """Tự động tạo bảng database khi ứng dụng khởi động"""
    try:
        # Import tất cả models để SQLAlchemy biết về chúng
        models_dir = os.path.join(os.path.dirname(__file__), 'models')
        for file in glob.glob(os.path.join(models_dir, '*.py')):
            name = os.path.splitext(os.path.basename(file))[0]
            if name != '__init__':
                importlib.import_module(f'models.{name}')

        # Tạo tất cả bảng
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully (or already exist)")
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        # Không raise exception để không crash app
        
# Sub-app cho routes cần JWT
protected_app.add_middleware(JWTAuthMiddleware)

# Add rate limiting middleware để prevent spam requests
app.add_middleware(RateLimitMiddleware, requests_per_second=20)
protected_app.add_middleware(RateLimitMiddleware, requests_per_second=20)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Thay đổi nếu cần thiết
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
protected_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Thay đổi nếu cần thiết
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount các router
protected_app.include_router(user.router, prefix="/users", tags=["users"])
protected_app.include_router(files.router, prefix="/files", tags=["files"])
protected_app.include_router(documents.router, prefix="/documents", tags=["documents"])
protected_app.include_router(folders.router, prefix="/documents/folders", tags=["folders"])
protected_app.include_router(folder_contents.router, prefix="/folders", tags=["folder-contents"])
protected_app.include_router(trash.router, prefix="/trash", tags=["trash"])
protected_app.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
protected_app.include_router(templates.router, prefix="/templates", tags=["templates"])
protected_app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
protected_app.include_router(stats.router, prefix="/stats", tags=["stats"])
protected_app.include_router(messages.router, prefix="/messages", tags=["messages"])

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(info.router, prefix="/info", tags=["info"])
app.include_router(reminder.router, prefix="/reminder", tags=["reminder"])

app.mount("/api", protected_app)

@app.get("/")
def read_root():
    return {"message": "FastAPI + MySQL + Docker Compose basic template"}
