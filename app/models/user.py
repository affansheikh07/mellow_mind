from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    profile_image = Column(String, nullable=True)
    hashed_password = Column(String(255), nullable=True)
    auth_provider = Column(String, default="local")

    tokens = relationship("AccessToken", back_populates="user", cascade="all, delete-orphan")

from app.models.accessToken import AccessToken