from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
import re
from fastapi import HTTPException, Depends
import secrets
from datetime import datetime, timedelta, time
from app.models.passwordReset import PasswordReset
from fastapi.responses import JSONResponse
from app.auth.schemas import UserUpdate
import random
from app.utils.email_utils import send_email
import os
from uuid import uuid4
from fastapi import UploadFile
from typing import Optional
from app.models.accessToken import AccessToken
from app.core.config import settings
from app.firebase_init import *
from firebase_admin import auth
import jwt
from fastapi import status


class AuthService:

    @staticmethod
    def validate_password(password: str):
        if len(password) < 8:
            return {
                "message": "Password must be at least 8 characters long",
                "status_code": 401
            }
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return {
                "message": "Password must contain at least one special character",
                "status_code": 401
            }
        return None

    @staticmethod
    def register_user(db: Session, user_data):
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            return {
                "message": "Email already registered",
                "status_code": 401
            }

        password_validation = AuthService.validate_password(user_data.password)
        if password_validation:
            return password_validation

        image_filename = None
        if hasattr(user_data, "profile_image") and user_data.profile_image:
            image = user_data.profile_image
            extension = os.path.splitext(image.filename)[1]
            image_filename = f"{uuid4().hex}{extension}"
            image_path = f"uploads/{image_filename}"
            with open(image_path, "wb") as f:
                f.write(image.file.read())

        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_password,
            profile_image=image_filename
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        access_token = create_access_token(data={"sub": new_user.email})

        token_entry = AccessToken(
            user_id=new_user.id,
            token=access_token
        )
        db.add(token_entry)
        db.commit()

        return JSONResponse(
            status_code=200,
            content={
                "status": 201,
                "data": {
                    "id": new_user.id,
                    "name": new_user.name,
                    "email": new_user.email,
                    "access_token": access_token,
                    "token_type": "bearer",
                    "profile_image": image_filename
                }
            }
        )


    @staticmethod
    def get_user_by_email(db: Session, email: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return {
                "message": "User not found",
                "status_code": 404
            }
        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            return {
                "message": "Incorrect email or password",
                "status_code": 401
            }

        access_token = create_access_token(data={"sub": email})

        token_entry = AccessToken(
            user_id=user.id,
            token=access_token
        )
        db.add(token_entry)
        db.commit()

        if user.profile_image:
            if user.profile_image.startswith("http://") or user.profile_image.startswith("https://"):
                profile_image_url = user.profile_image
            else:
                profile_image_url = f"https://mellowmind-production-457f.up.railway.app/uploads/{user.profile_image}"
        else:
            profile_image_url = None

        return JSONResponse(
            status_code=200,
            content={
                "status": 200,
                "data": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "profile_image": profile_image_url,
                    "access_token": access_token,
                    "token_type": "bearer",
                }
            }
        )


    @staticmethod
    def reset_password(db: Session, email: str, new_password: str, token: str):
        reset_entry = db.query(PasswordReset).filter(
            PasswordReset.email == email,
            PasswordReset.token == token
        ).first()

        if not reset_entry:
            return {
                "message": "Invalid or expired password reset token",
                "status_code": 401
            }

        user = db.query(User).filter(User.email == email).first()
        if not user:
            return {
                "message": "User not found",
                "status_code": 404
            }

        user.hashed_password = get_password_hash(new_password)
        db.commit()

        db.delete(reset_entry)
        db.commit()

        return {
            "message": "Password updated successfully",
            "status_code": 200
        }


    @staticmethod
    def initiate_password_reset(db: Session, email: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return JSONResponse(
                status_code=200,
                content={"status": 404, "message": "User not found"}
            )

        reset_code = str(random.randint(100000, 999999))
        expiration_time = datetime.utcnow() + timedelta(minutes=10)

        existing_reset = db.query(PasswordReset).filter(PasswordReset.email == email).first()

        if existing_reset:
            existing_reset.token = reset_code
            existing_reset.created_at = expiration_time
        else:
            existing_reset = PasswordReset(
                email=email,
                token=reset_code,
                created_at=expiration_time
            )
            db.add(existing_reset)

        db.commit()

        subject = "Your Password Reset Code"
        body = f"Your password reset code is: {reset_code}"
        send_email(to=email, subject=subject, body=body)

        return JSONResponse(
            status_code=200,
            content={"status": 200, "message": "Reset code sent to your email"}
        )


    @staticmethod
    def update_user(db: Session, user_id: int, name: Optional[str], email: Optional[str], profile_image: UploadFile = None):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return JSONResponse(status_code=200, content={"status": 404, "message": "User not found"})

        if email and email.strip() != "" and email != user.email:
            email_user = db.query(User).filter(User.email == email, User.id != user_id).first()
            if email_user:
                return JSONResponse(status_code=200, content={"status": 404, "message": "Email already in use"})
            user.email = email.strip()

        if name and name.strip() != "":
            user.name = name.strip()

        if profile_image and profile_image.filename:
            upload_dir = "uploads"
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            ext = os.path.splitext(profile_image.filename)[1]
            filename = f"{uuid4().hex}{ext}"
            file_path = os.path.join(upload_dir, filename)

            with open(file_path, "wb") as f:
                f.write(profile_image.file.read())

            user.profile_image = filename

        db.commit()
        db.refresh(user)

        if user.profile_image:
            if user.profile_image.startswith("http://") or user.profile_image.startswith("https://"):
                profile_image_url = user.profile_image
            else:
                profile_image_url = f"https://mellowmind-production-457f.up.railway.app/uploads/{user.profile_image}"
        else:
            profile_image_url = None

        return JSONResponse(
            status_code=200,
            content={
                "status": 200,
                "message": "User updated successfully",
                "data": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "profile_image": profile_image_url
                }
            }
        )


    @staticmethod
    def create_user_from_social_login(
        db: Session, 
        name: str, 
        email: str, 
        profile_image_url: str = None, 
        auth_provider: str = None
    ):
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            user = User(name=name, email=email, auth_provider=auth_provider, hashed_password=get_password_hash("123456799"))
            if profile_image_url:
                user.profile_image = profile_image_url
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            updated = False
            if user.auth_provider != auth_provider:
                user.auth_provider = auth_provider
                updated = True
            if not user.profile_image and profile_image_url:
                user.profile_image = profile_image_url
                updated = True
            if updated:
                db.commit()
                db.refresh(user)

        return user

    @staticmethod
    def generate_login_token(db: Session, user: User, auth_provider: str):
        payload = {
            "sub": user.email,
            "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "user_id": user.id,
            "auth_provider": auth_provider
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        token_entry = AccessToken(user_id=user.id, token=token)
        db.add(token_entry)
        db.commit()

        return {
            "status": 200,
            "data": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "profile_image": user.profile_image,
                "access_token": token,
                "token_type": "bearer",
                "auth_provider": auth_provider
            }
        }


    @staticmethod
    def change_password(db: Session, user: User, old_password: str, new_password: str):
        if not verify_password(old_password, user.hashed_password):
            return JSONResponse(
                status_code=200,
                content={"status": 400, "message": "Old password is incorrect"}
            )

        user.hashed_password = get_password_hash(new_password)
        db.commit()

        return JSONResponse(
            status_code=200,
            content={"status": 200, "message": "Password updated successfully"}
        )



