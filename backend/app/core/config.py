import os

class Settings:
    DB_HOST: str = os.getenv("DB_HOST", "db")
    DB_USER: str = os.getenv("DB_USER", "testuser")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "testpass")
    DB_NAME: str = os.getenv("DB_NAME", "testdb")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

settings = Settings()