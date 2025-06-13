from sqlalchemy.orm import Session
from crud.user import get_user, create_user, get_user_by_email
from schemas.user import UserCreate
from core.security import verify_password, create_access_token

def service_create_user(db: Session, user: UserCreate):
    # Logic nghiệp vụ có thể mở rộng ở đây
    return create_user(db, user)

def service_get_user(db: Session, user_id: int):
    # Logic nghiệp vụ có thể mở rộng ở đây
    return get_user(db, user_id)