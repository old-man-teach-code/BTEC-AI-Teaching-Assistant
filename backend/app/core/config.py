import os

class Settings:
    DB_HOST: str = os.getenv("DB_HOST", "db")
    DB_USER: str = os.getenv("DB_USER", "testuser")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "testpass")
    DB_NAME: str = os.getenv("DB_NAME", "testdb")

settings = Settings()