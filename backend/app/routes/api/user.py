from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from schemas.user import UserCreate, UserRead, Token, UserUpdate
from services.user_service import service_create_user, service_get_user, service_get_users
from services.auth_service import authenticate_user, login_for_access_token
from dependencies.deps import get_db, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from typing import List

router = APIRouter()

@router.get("/", response_model=List[UserRead])
def get_all_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lấy danh sách tất cả users (có phân trang)"""
    users = service_get_users(db, skip=skip, limit=limit)
    return users

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
def update_current_user(user: UserUpdate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = service_get_user(db, current_user.id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user details - chỉ cập nhật field nào có giá trị
    if user.name is not None:
        db_user.name = user.name
    if user.email is not None:
        db_user.email = user.email
    if user.discord_user_id is not None:
        db_user.discord_user_id = user.discord_user_id
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.patch("/me/profile", response_model=UserRead)
def update_user_profile_after_login(
    user_update: UserUpdate, 
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """API để cập nhật thông tin user sau khi đăng nhập (name, email, discord_user_id)"""
    db_user = service_get_user(db, current_user.id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Cập nhật từng field nếu có giá trị
    updated = False
    if user_update.name is not None and user_update.name.strip():
        db_user.name = user_update.name.strip()
        updated = True
    
    if user_update.email is not None and user_update.email.strip():
        # Kiểm tra email đã tồn tại chưa (trừ email hiện tại)
        from crud.user import get_user_by_email
        existing_user = get_user_by_email(db, user_update.email.strip())
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already exists")
        db_user.email = user_update.email.strip()
        updated = True
    
    if user_update.discord_user_id is not None:
        # Cho phép set rỗng để xóa discord_user_id
        discord_id = user_update.discord_user_id.strip() if user_update.discord_user_id else None
        db_user.discord_user_id = discord_id if discord_id else None
        updated = True
    
    if not updated:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.put("/{user_id}/discord", response_model=UserRead)
def update_user_discord_id(user_id: int, discord_user_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Endpoint để cập nhật discord_user_id cho user (admin only hoặc self-update)"""
    db_user = service_get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Chỉ cho phép user tự cập nhật hoặc admin (có thể thêm logic admin check sau)
    if current_user.id != user_id:
        # Có thể thêm check admin role ở đây
        pass
    
    db_user.discord_user_id = discord_user_id
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user
