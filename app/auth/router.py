from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.schemas import UserCreate, UserLogin, ResetPassword, ForgotPassword, UserUpdate
from app.auth.services import AuthService
from app.database import get_db
from fastapi import Form, File, UploadFile
from typing import Optional

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup")
async def signup(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    profile_image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    user_data = type("UserData", (object,), {
        "name": name,
        "email": email,
        "password": password,
        "profile_image": profile_image
    })()

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
async def update_user(
    user_id: int,
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    profile_image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    return AuthService.update_user(db, user_id, name, email, profile_image)