from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, status
from fastapi.responses import JSONResponse
from jose import JWTError
from core.security import decode_access_token
from crud.user import get_user
from database.session import SessionLocal

class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        with open("request.log", "a") as log_file:
            log_file.write(f"Processing request for path: {request.url.path}\n")

        ignore_paths = [
            "/api/docs",
            "/docs",
            "/docs#"
            "/api/openapi.json",
            "/api/openapi.json",
            "/redoc",
            "/static",  # nếu bạn dùng static file
        ]
        # Bỏ qua cho path giống hoặc bắt đầu bằng ignore_paths
        if any(request.url.path.startswith(path) for path in ignore_paths):
            return await call_next(request)
        
        authorization: str = request.headers.get("Authorization")

        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"},
            )
        
        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        if payload is None or "sub" not in payload:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid token"},
            )
        db = SessionLocal()
        user = get_user(db, int(payload["sub"]))
        db.close()
        if user is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "User not found"},
            )
        request.state.user = user
        return await call_next(request)