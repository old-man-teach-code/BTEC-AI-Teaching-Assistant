from sqlalchemy.orm import Session
from crud.user import get_user_by_email
from core.security import verify_password, create_access_token

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def login_for_access_token(user):
    return create_access_token(data={"sub": str(user.id)})