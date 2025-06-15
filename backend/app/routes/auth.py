from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from services.auth_service import authenticate_user, login_for_access_token
from services.user_service import service_create_user
from schemas.user import UserCreate, UserRead
from schemas.user import Token
from api.deps import get_db

router = APIRouter()

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = login_for_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/create", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return service_create_user(db, user)
    except Exception as e:
        print(f"Error creating user: {e}")  # Log the error for debugging
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")