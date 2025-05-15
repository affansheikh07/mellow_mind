from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.schemas import UserCreate, UserLogin, ResetPassword, ForgotPassword, UserUpdate
from app.auth.services import AuthService
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup")
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    return AuthService.register_user(db, user_data)

@router.post("/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    return AuthService.authenticate_user(db, credentials.email, credentials.password)

@router.post("/reset-password")
async def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    return AuthService.reset_password(db, data.email, data.new_password, data.token)

@router.post("/forgot-password")
async def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):
    return AuthService.initiate_password_reset(db, data.email)

@router.post("/users/{user_id}")
def update_user(user_id: int, update_data: UserUpdate, db: Session = Depends(get_db)):
    return AuthService.update_user(db, user_id, update_data)