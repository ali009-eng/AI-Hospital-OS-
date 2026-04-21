"""
Authentication models
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data model"""
    username: Optional[str] = None
    role: Optional[str] = "user"


class UserLogin(BaseModel):
    """User login request model"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserCreate(BaseModel):
    """User creation model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=6)
    role: str = Field(default="user", pattern="^(user|admin|nurse|physician)$")


class User(BaseModel):
    """User model"""
    username: str
    email: Optional[str] = None
    role: str = "user"
    disabled: bool = False

