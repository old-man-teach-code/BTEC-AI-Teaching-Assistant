from database.session import SessionLocal
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from core.security import decode_access_token
from crud.user import get_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Retrieves the current authenticated user based on the provided JWT token.

    Args:
        token: The JWT token provided in the Authorization header (handled by Depends(oauth2_scheme)).
        db: The database session dependency.

    Returns:
        The authenticated user object if the token is valid and the user exists.

    Raises:
        HTTPException: If the token is invalid, expired, or the user does not exist (status_code 401).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise credentials_exception
    user = get_user(db, int(payload["sub"]))
    if user is None:
        raise credentials_exception
    return user