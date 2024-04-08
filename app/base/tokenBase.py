from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class Token(BaseModel):
    accessToken: str
    refreshToken: str


class TokenModelBase(BaseModel):
    userId: UUID
    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    # id: Optional[UUID] = None
    id: UUID
    username: str
    is_super: bool


class TokenPayload(BaseModel):
    sub: str
    exp: int
