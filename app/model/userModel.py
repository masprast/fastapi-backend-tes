from sqlalchemy import TIMESTAMP, UUID, Boolean, Column, DateTime, String, func
from app.db.db import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, index=True, nullable=False)
    username = Column(String, nullable=True, index=True, unique=True)
    full_name = Column(String, nullable=True)
    password = Column(String, nullable=True)
    email = Column(String, nullable=True, index=True)
    is_super = Column(Boolean, nullable=True, server_default="FALSE")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
