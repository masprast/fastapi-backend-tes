from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str | None = None
    full_name: str | None = None
    email: EmailStr | None = None
    is_super: bool | None = None
    last_login: datetime | None = None

    class Config:
        from_attributes = True


class UserInDB(UserBase):
    password: str
