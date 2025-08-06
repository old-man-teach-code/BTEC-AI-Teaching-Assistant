from routes.api import user, files, documents, trash, folders, calendar, templates
from routes import auth, info, reminder, notifications
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies.deps import get_db
from core.jwt_middleware import JWTAuthMiddleware
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
protected_app = FastAPI(
    title="FastAPI + MySQL + Docker Compose",
    description="Basic template for FastAPI with MySQL and Docker Compose",
    version="1.0.0",
    doc_url="/api/docs",
)
# Sub-app cho routes cần JWT
protected_app.add_middleware(JWTAuthMiddleware)

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
protected_app.include_router(trash.router, prefix="/trash", tags=["trash"])
protected_app.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
protected_app.include_router(templates.router, prefix="/templates", tags=["templates"])



app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(info.router, prefix="/info", tags=["info"])
app.include_router(reminder.router, prefix="/reminder", tags=["reminder"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

# Public endpoint để lookup user theo Discord ID (không cần JWT)
@app.get("/users/by-discord/{discord_user_id}")
async def get_user_by_discord_id_public(discord_user_id: str, db: Session = Depends(get_db)):
    """Public endpoint để tìm user theo discord_user_id (không cần JWT)"""
    from crud.user import get_user_by_discord_id
    from schemas.user import UserRead
    
    db_user = get_user_by_discord_id(db, discord_user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found with this Discord ID")
    
    # Return basic user info without sensitive data
    return {
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "discord_user_id": db_user.discord_user_id,
        "created_at": db_user.created_at
    }

app.mount("/api", protected_app)

@app.get("/")
def read_root():
    return {"message": "FastAPI + MySQL + Docker Compose basic template"}
