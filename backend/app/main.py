from routes.api import user, templates
from routes.api import files, documents, trash, folders, calendar
from fastapi import FastAPI
from routes import auth, info
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

app.mount("/api", protected_app)

@app.get("/")
def read_root():
    return {"message": "FastAPI + MySQL + Docker Compose basic template"}
