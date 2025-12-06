"""
User-related Pydantic schemas for request/response validation.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base schema for user data."""
    
    email: EmailStr = Field(..., description="User's email address")
    full_name: str = Field(..., min_length=1, max_length=255, description="User's full name")


class UserCreate(UserBase):
    """Schema for user registration."""
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User's password (min 8 characters)"
    )
    phone_number: Optional[str] = Field(None, max_length=20, description="User's phone number")
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)
    daily_rate: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    monthly_salary: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    pay_cycle_day: Optional[int] = Field(None, ge=1, le=31)
    risk_tolerance: Optional[int] = Field(None, ge=1, le=10)
    financial_goals: Optional[str] = Field(None, max_length=5000)
    employer_id: Optional[str] = Field(None, max_length=100)
    employee_id: Optional[str] = Field(None, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login."""
    
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class UserResponse(BaseModel):
    """Schema for user response (excludes sensitive data)."""
    
    id: int
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    employer_id: Optional[str] = None
    employee_id: Optional[str] = None
    daily_rate: Decimal
    monthly_salary: Decimal
    pay_cycle_day: int
    is_active: bool
    is_verified: bool
    risk_tolerance: int
    financial_goals: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """Schema for detailed user profile with financial info."""
    
    id: int
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    employer_id: Optional[str] = None
    daily_rate: Decimal
    monthly_salary: Decimal
    pay_cycle_day: int
    risk_tolerance: int
    available_wage_advance: Decimal
    total_buckets: int = 0
    total_bucket_balance: Decimal = Decimal("0.00")
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication tokens."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""
    
    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""
    
    refresh_token: str = Field(..., description="Refresh token")


class PasswordChange(BaseModel):
    """Schema for password change request."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password"
    )
    
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

