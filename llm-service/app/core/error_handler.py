import logging
import traceback
from typing import Union
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions với format chuẩn
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Exception",
            "detail": exc.detail,
            "code": f"HTTP_{exc.status_code}",
            "path": str(request.url.path)
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors với format dễ đọc
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(x) for x in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": "Request validation failed",
            "code": "VALIDATION_ERROR",
            "errors": errors
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle các exception không được catch
    """
    # Log full traceback
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Trong production, không expose internal error details
    error_detail = str(exc) if logger.level == logging.DEBUG else "Internal server error"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": error_detail,
            "code": "INTERNAL_ERROR",
            "path": str(request.url.path)
        }
    )


def add_exception_handlers(app):
    """
    Add all exception handlers to FastAPI app
    
    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers registered")