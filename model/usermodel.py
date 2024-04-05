from sqlalchemy import TIMESTAMP, Boolean, Column, Integer,String, func, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserModel(Base):
    __tablename__ = 'users'

    id = Column(Integer,primary_key=True,index=True,nullable=False,autoincrement=True)
    username = Column(String,nullable=False,index=True,unique=True)
    password = Column(String,nullable=False)
    email = Column(String,nullable=True,index=True)
    is_super = Column(Boolean,nullable=False,server_default='FALSE')
    created_at = Column(TIMESTAMP(timezone=True),server_default=func.now())
    last_login = Column(TIMESTAMP(timezone=True),nullable=True)