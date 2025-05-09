from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class PasswordReset(Base):
    __tablename__ = 'password_resets'

    email = Column(String(255), primary_key=True, index=True)
    token = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<PasswordReset(email={self.email}, token={self.token}, created_at={self.created_at})>"

    # Optional: Define methods for easier interaction with the model
    def as_dict(self):
        return {
            "email": self.email,
            "token": self.token,
            "created_at": self.created_at
        }
