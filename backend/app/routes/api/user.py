from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.user import UserCreate, UserRead, Token
from services.user_service import service_create_user, service_get_user
from services.auth_service import authenticate_user, login_for_access_token
from dependencies.deps import get_db, get_current_user
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.get("/me", response_model=UserRead)
def read_current_user(current_user = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = service_get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/me", response_model=UserRead)
def update_current_user(user: UserCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = service_get_user(db, current_user.id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user details
    db_user.name = user.name
    db_user.email = user.email
    # Note: Password update logic should be handled separately for security reasons
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user
