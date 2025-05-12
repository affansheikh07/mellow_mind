from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
import re
from fastapi import HTTPException, Depends
import secrets
from datetime import datetime, timedelta
from app.models.passwordReset import PasswordReset
from fastapi.responses import JSONResponse

class AuthService:

    @staticmethod
    def validate_password(password: str):
        if len(password) < 8:
            return {
                "message": "Password must be at least 8 characters long",
                "status_code": 400
            }
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return {
                "message": "Password must contain at least one special character",
                "status_code": 400
            }
        return None

    @staticmethod
    def register_user(db: Session, user_data):
        # Check if user exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            return {
                "message": "Email already registered",
                "status_code": 400
            }

        # Validate password
        password_validation = AuthService.validate_password(user_data.password)
        if password_validation:
            return password_validation

        # Create new user
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

        # Return custom response
        return JSONResponse(
            status_code=200,
            content={
                "status": 200,
                "data": {
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
                    "name": user.name,
                    "email": user.email,
                    "access_token": access_token, 
                    "token_type": "bearer",
                    
                }
            }
        )

    @staticmethod
    def reset_password(db: Session, email: str, new_password: str):
        reset_entry = db.query(PasswordReset).filter(PasswordReset.email == email).first()
        if not reset_entry:
            return {
                "message": "Password reset request not found",
                "status_code": 400
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
            return {
                "message": "User not found",
                "status_code": 404
            }

        # Generate token and expiration
        reset_token = secrets.token_urlsafe(32)
        expiration_time = datetime.utcnow() + timedelta(hours=1)

        new_reset = PasswordReset(
            email=email,
            token=reset_token,
            created_at=expiration_time
        )
        db.add(new_reset)
        db.commit()

        return {
            "message": "Success",
            "status_code": 200
        }