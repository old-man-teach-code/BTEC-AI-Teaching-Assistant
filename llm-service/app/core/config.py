import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

# Lấy đường dẫn gốc của dự án
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    """
    Cấu hình chung cho AI Service
    Sử dụng Pydantic Settings để quản lý biến môi trường
    """
    
    # MySQL Configuration (kết nối đến backend database)
    mysql_host: str = Field(default="backend-db", env="MYSQL_HOST")
    mysql_user: str = Field(default="testuser", env="MYSQL_USER")
    mysql_password: str = Field(default="testpass", env="MYSQL_PASSWORD")
    mysql_database: str = Field(default="testdb", env="MYSQL_DATABASE")
    mysql_port: int = Field(default=3306, env="MYSQL_PORT")
    
    # ChromaDB Configuration
    chroma_persist_directory: Path = Field(
        default=BASE_DIR / "data" / "chroma_db",
        env="CHROMA_PERSIST_DIRECTORY"
    )
    chroma_collection_name: str = Field(
        default="ta_edu_knowledge",
        env="CHROMA_COLLECTION_NAME"
    )
    
    # Model Configuration
    model_path: Path = Field(
        default=BASE_DIR / "data" / "models" / "Arcee-VyLinh-Q4_K_M.gguf",
        env="MODEL_PATH"
    )
    embedding_model: str = Field(
        default="dangvantuan/vietnamese-embedding",
        env="EMBEDDING_MODEL"
    )
    model_cache_dir: Path = Field(
        default=BASE_DIR / "data" / "models",
        env="MODEL_CACHE_DIR"
    )
    
    # LLM Configuration
    llm_temperature: float = Field(default=0.7, env="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=2048, env="LLM_MAX_TOKENS")
    llm_context_size: int = Field(default=4096, env="LLM_CONTEXT_SIZE")
    llm_n_gpu_layers: int = Field(default=0, env="LLM_N_GPU_LAYERS")
    
    # Service Configuration
    service_name: str = Field(default="ai-service", env="SERVICE_NAME")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    cors_origins: List[str] = Field(
        default=["http://localhost:8000", "http://localhost:3000"],
        env="CORS_ORIGINS"
    )
    
    # File processing limits
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: List[str] = [".pdf", ".docx", ".pptx", ".txt"]
    
    # RAG Configuration
    chunk_size: int = 512  # Kích thước mỗi chunk khi chia nhỏ document
    chunk_overlap: int = 50  # Độ overlap giữa các chunks
    top_k_results: int = 5  # Số lượng kết quả tìm kiếm tối đa
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def mysql_url(self) -> str:
        """Tạo MySQL connection URL"""
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )
    
    def create_directories(self):
        """Tạo các thư mục cần thiết nếu chưa tồn tại"""
        self.chroma_persist_directory.mkdir(parents=True, exist_ok=True)
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)

# Khởi tạo settings instance
settings = Settings()
settings.create_directories()