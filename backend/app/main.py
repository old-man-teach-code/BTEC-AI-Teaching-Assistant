from fastapi import FastAPI
from routes import user, auth
from core.jwt_middleware import JWTAuthMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
protected_app = FastAPI()
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

app.include_router(auth.router, prefix="/auth", tags=["auth"])
protected_app.include_router(user.router, prefix="/users", tags=["users"])

app.mount("", protected_app)

@app.get("/")
def read_root():
    return {"message": "FastAPI + MySQL + Docker Compose basic template"}