from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator, ValidationInfo


class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    password1: str
    password2: str

    @field_validator('password1', 'password2')
    def password_length(cls, value: str):
        """Ensure password is at least 8 characters long."""
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return value

    @field_validator('password2')
    def passwords_match(cls, value, info: ValidationInfo):
        """Ensure both passwords match."""
        password1 = info.data["password1"]  # Use the new approach to get value
        if password1 is None or value != password1:
            raise ValueError('Passwords do not match')
        return value

class UserUpdateSchema(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None

class UserReadSchema(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    created_at: datetime
    updated_at: datetime


class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password1: str
    new_password2: str

    @field_validator('new_password1', 'new_password2')
    def password_length(cls, value: str):
        """Ensure password is at least 8 characters long."""
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return value

    @field_validator('new_password2')
    def passwords_match(cls, value, info: ValidationInfo):
        """Ensure both passwords match."""
        password1 = info.data["new_password1"]  # Use the new approach to get value
        if password1 is None or value != password1:
            raise ValueError('Passwords do not match')
        return value
