import datetime
import re
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, validator


class AuthBase(BaseModel):
    email: EmailStr = Field(..., description="email")
    password: str = Field(..., description="password", min_length=8)

    # @validator("email")
    # def valid_email(cls, v):
    #     regex = re.compile(r"(^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$)")
    #     if not re.fullmatch(regex, cls.email):
    #         raise ValueError("email tidak valid")
    #     return cls.email


class AuthOutput(BaseModel):
    email: EmailStr
    id: UUID
    created_at: datetime.datetime

    class Config:
        from_attributes = True
