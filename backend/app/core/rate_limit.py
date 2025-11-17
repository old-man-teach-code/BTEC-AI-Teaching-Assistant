"""
Rate limiting middleware để prevent API spam
"""
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
import time
from collections import defaultdict
from threading import Lock

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_second=10):
        super().__init__(app)
        self.requests_per_second = requests_per_second
        self.requests = defaultdict(list)
        self.lock = Lock()
        
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP hoặc user ID from token)
        client_id = request.client.host if request.client else "unknown"
        
        # Bỏ qua rate limit cho một số paths
        ignore_paths = ["/api/docs", "/docs", "/openapi.json", "/health"]
        if any(request.url.path.startswith(path) for path in ignore_paths):
            return await call_next(request)
        
        current_time = time.time()
        
        with self.lock:
            # Clean old requests (older than 1 second)
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if current_time - req_time < 1.0
            ]
            
            # Check rate limit
            if len(self.requests[client_id]) >= self.requests_per_second:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many requests. Please slow down.",
                        "retry_after": 1
                    }
                )
            
            # Add current request
            self.requests[client_id].append(current_time)
        
        response = await call_next(request)
        return response
