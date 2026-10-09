from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


def _check_password_byte_length(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password must be at most 72 UTF-8 bytes.")
    return password


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    location: str | None = Field(default=None, max_length=120)

    _validate_password = field_validator("password")(_check_password_byte_length)


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    _validate_password = field_validator("password")(_check_password_byte_length)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    location: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=20)


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    location: str | None = None
    phone: str | None = None
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
