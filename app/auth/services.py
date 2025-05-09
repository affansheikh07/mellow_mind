from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
from fastapi import HTTPException
import secrets
from datetime import datetime, timedelta
from app.models import passwordReset

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
        return {"message": "User created successfully"}

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
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    def reset_password(email: str, new_password: str):
        if email not in fake_users_db:
            raise HTTPException(status_code=404, detail="User not found")
        fake_users_db[email]["hashed_password"] = get_password_hash(new_password)
        return {"message": "Password updated successfully"}

    @staticmethod
    def initiate_password_reset(email: str):
        # Check if the email exists in the user table
        def initiate_password_reset(email: str, db: Session = Depends(get_db)):
        user = get_user_by_email(email)  # You need a function to query the user table
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Generate a secure token (You can use JWT or any other method)
        reset_token = secrets.token_urlsafe(32)  # Generates a random token
        
        # Set expiration time (e.g., 1 hour from now)
        expiration_time = datetime.utcnow() + timedelta(hours=1)

        # Store the token in the password_resets table
        db = get_db()  # Your DB connection
        db.execute("""
            INSERT INTO password_resets (email, token, created_at)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE token=%s, created_at=%s
        """, (email, reset_token, expiration_time, reset_token, expiration_time))
        db.commit()

        # In a real application, send the email with the reset link (skip here for simplicity)
        return {"message": "Password reset link sent to your email"}