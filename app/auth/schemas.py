from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ResetPassword(BaseModel):
    email: str
    token: str
    new_password: str

class ForgotPassword(BaseModel):
    email: EmailStr

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, example="New Name")
    email: Optional[EmailStr] = Field(None, example="newemail@example.com")

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str