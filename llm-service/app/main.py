from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys

# Import cấu hình và routes
from core.config import settings
from core.llm_config import initialize_llm
from core.embedding_config import initialize_embeddings
from core.error_handler import add_exception_handlers
from database.vector_store import initialize_vector_store
from database.mysql_client import mysql_client
from routes import extraction, template

# Cấu hình logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Quản lý vòng đời của ứng dụng
    Khởi tạo các services cần thiết khi start và cleanup khi shutdown
    """
    logger.info(f"Khởi động {settings.service_name}...")
    
    try:
        # Khởi tạo MySQL Client
        logger.info("Đang kết nối đến Backend Database...")
        mysql_client.initialize()
        
        # Khởi tạo LLM
        logger.info("Đang khởi tạo Large Language Model...")
        initialize_llm()
        
        # Khởi tạo Embeddings
        logger.info("Đang khởi tạo Embedding Model...")
        initialize_embeddings()
        
        # Khởi tạo Vector Store
        logger.info("Đang khởi tạo Vector Store (ChromaDB)...")
        initialize_vector_store()
        
        logger.info("Khởi tạo hoàn tất! AI Service sẵn sàng.")
        
    except Exception as e:
        logger.error(f"Lỗi khi khởi tạo services: {str(e)}")
        raise
    
    yield  # Ứng dụng chạy
    
    # Cleanup khi shutdown
    logger.info("Đang dọn dẹp resources...")
    # Thêm cleanup logic nếu cần


# Khởi tạo FastAPI app
app = FastAPI(
    title="AI Teaching Assistant Service",
    description="Service xử lý AI cho hệ thống Trợ lý Giảng viên",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add exception handlers
add_exception_handlers(app)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount các routes
app.include_router(
    extraction.router,
    prefix="/api/extraction",
    tags=["Knowledge Extraction"]
)
app.include_router(
    template.router,
    prefix="/api/template",
    tags=["Template Processing"]
)

# Health check endpoint
@app.get("/", tags=["Health Check"])
async def root():
    """
    Health check endpoint
    Kiểm tra service đang hoạt động
    """
    return {
        "service": settings.service_name,
        "status": "running",
        "version": "1.0.0",
        "description": "AI Teaching Assistant Service"
    }

@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Detailed health check
    Kiểm tra chi tiết các components
    """
    health_status = {
        "service": "healthy",
        "components": {
            "llm": "checking...",
            "embeddings": "checking...",
            "vector_store": "checking...",
            "mysql": "checking..."
        }
    }
    
    try:
        # Kiểm tra LLM
        from core.llm_config import llm_manager
        if llm_manager.llm is not None:
            health_status["components"]["llm"] = "healthy"
        else:
            health_status["components"]["llm"] = "not initialized"
            
        # Kiểm tra Embeddings
        from core.embedding_config import embedding_manager
        if embedding_manager.embed_model is not None:
            health_status["components"]["embeddings"] = "healthy"
        else:
            health_status["components"]["embeddings"] = "not initialized"
            
        # Kiểm tra Vector Store
        from database.vector_store import vector_store_manager
        if vector_store_manager.vector_store is not None:
            health_status["components"]["vector_store"] = "healthy"
        else:
            health_status["components"]["vector_store"] = "not initialized"
            
        # Kiểm tra MySQL connection
        from database.mysql_client import test_connection
        if test_connection():
            health_status["components"]["mysql"] = "healthy"
        else:
            health_status["components"]["mysql"] = "connection failed"
            
    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra health: {str(e)}")
        health_status["service"] = "unhealthy"
        health_status["error"] = str(e)
    
    # Xác định overall status
    if all(status == "healthy" for status in health_status["components"].values()):
        health_status["service"] = "healthy"
    else:
        health_status["service"] = "degraded"
    
    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level=settings.log_level.lower()
    )