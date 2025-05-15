from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
import re
from fastapi import HTTPException, Depends
import secrets
from datetime import datetime, timedelta
from app.models.passwordReset import PasswordReset
from fastapi.responses import JSONResponse
from app.auth.schemas import UserUpdate
import random
from datetime import datetime, timedelta
from app.utils.email_utils import send_email

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

        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        access_token = create_access_token(data={"sub": new_user.email})

        return JSONResponse(
            status_code=200,
            content={
                "status": 201,
                "data": {
                    "id": new_user.id,
                    "name": new_user.name,
                    "email": new_user.email,
                    "access_token": access_token,
                    "token_type": "bearer"
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
        return JSONResponse(
            status_code=200,
            content={
                "status": 200,
                "data": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
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

        token_age = datetime.utcnow() - reset_entry.created_at
        if token_age > timedelta(minutes=15):
            db.delete(reset_entry)
            db.commit()
            return {
                "message": "Token has expired",
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
    def update_user(db: Session, user_id: int, update_data: UserUpdate):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return JSONResponse(status_code=200, content={"status": 404,"message": "User not found"})

        if update_data.email and update_data.email != user.email:
            email_user = db.query(User).filter(User.email == update_data.email, User.id != user_id).first()
            if email_user:
                return JSONResponse(status_code=200, content={"status": 404,"message": "Email already in use"})
            user.email = update_data.email

        if update_data.name:
            user.name = update_data.name

        db.commit()
        db.refresh(user)

        return JSONResponse(
            status_code=200,
            content={
                "status": 200,
                "message": "User updated successfully",
                "data": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email
                }
            }
        )
