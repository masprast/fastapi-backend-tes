from sqlalchemy import UUID, Column, String
from db.db import Base


class TokenModel(Base):
    __tablename__ = "token"

    userId = Column(UUID, primary_key=True)
    access_token = Column(String(500))
    refresh_token = Column(String(500))
