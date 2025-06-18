import os
from pathlib import Path

# Lấy đường dẫn gốc của dự án
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings:
    # Database settings
    DB_HOST: str = os.getenv("DB_HOST", "db")
    DB_USER: str = os.getenv("DB_USER", "testuser")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "testpass")
    DB_NAME: str = os.getenv("DB_NAME", "testdb")
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    
    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_DEFAULT_TTL: int = int(os.getenv("REDIS_DEFAULT_TTL", 3600))  # 1 hour default
    
    # File storage settings
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads")))
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB mặc định
    ALLOWED_EXTENSIONS: list = os.getenv("ALLOWED_EXTENSIONS", ".pdf,.docx,.pptx").split(",")

settings = Settings()