from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from base.userbase import UserBase
from model.usermodel import UserModel
from db.db import get_db

router = APIRouter(prefix='/users',tags=['User'])

@router.get('/',response_model=List[UserBase])
async def getAllUser(db:Session = Depends(get_db)):
    users = db.query(UserModel).all()
    print(users)
    return users

