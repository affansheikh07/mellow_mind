from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.schemas import UserCreate, UserLogin, ResetPassword, ForgotPassword
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
async def reset_password(data: ResetPassword):
    return AuthService.reset_password(data.email, data.new_password)

@router.post("/forgot-password")
async def forgot_password(data: ForgotPassword):
    return AuthService.initiate_password_reset(data.email)