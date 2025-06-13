from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.user import UserCreate, UserRead, Token
from services.user_service import service_create_user, service_get_user
from services.auth_service import authenticate_user, login_for_access_token
from api.deps import get_db, get_current_user
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return service_create_user(db, user)
    except Exception as e:
        print(f"Error creating user: {e}")  # Log the error for debugging
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/me", response_model=UserRead)
def read_current_user(current_user = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = service_get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user