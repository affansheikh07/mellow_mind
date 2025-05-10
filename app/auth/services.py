from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
from fastapi import HTTPException, Depends
import secrets
from datetime import datetime, timedelta
from app.models.passwordReset import PasswordReset

class AuthService:

    @staticmethod
    def register_user(db: Session, user_data):
        # Check if user exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

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
        
        return {"name": user_data.name,"email":user_data.email,"message": "User created successfully"}

    @staticmethod
    def get_user_by_email(db: Session, email: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        access_token = create_access_token(data={"sub": email})
        return {"name": user.name,"email":user.email,"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    def reset_password(db: Session, email: str, new_password: str):
        reset_entry = db.query(PasswordReset).filter(PasswordReset.email == email).first()
        if not reset_entry:
            raise HTTPException(status_code=400, detail="Password reset request not found")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.hashed_password = get_password_hash(new_password)
        db.commit()

        db.delete(reset_entry)
        db.commit()

        return {"message": "Password updated successfully"}

    @staticmethod
    def initiate_password_reset(db: Session, email: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Generate token and expiration
        reset_token = secrets.token_urlsafe(32)
        expiration_time = datetime.utcnow() + timedelta(hours=1)

        # Save token (assume `passwordReset` is a SQLAlchemy model)
        new_reset = PasswordReset(
            email=email,
            token=reset_token,
            created_at=expiration_time
        )
        db.add(new_reset)
        db.commit()

        # Normally, you'd send the email here
        return {"message": "Password reset link sent to your email"}
