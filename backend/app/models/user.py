from sqlalchemy import Column, Integer, String
from database.session import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), index=True)
    email = Column(String(120), unique=True, index=True)
    hashed_password = Column(String(256))