import os
from typing import Annotated
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi_sqlalchemy import DBSessionMiddleware
from sqlalchemy.orm import Session
from base.userbase import UserBase

from db.initdb import InitDB
from router import authRouter, userRouter

load_dotenv("local.env")

app = FastAPI()
app.include_router(authRouter.router)
app.include_router(userRouter.router)

InitDB()
# db_dependency = Annotated(Session,Depends(get_db))


@app.get("/")
async def root():
    return {"message": "Assalamualaikum"}


# @app.post('/add_user')
# async def tambah_user(user:UserBase,db:db_dependency):
#     db_user = usermodel.UserModel(username=user.username,password=user.password,email=user.email)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
# @app.get('/users',response_model=list[User])
# async def getUsers():
#     return {"users":users}

# @app.get('/users/{id}',response_model=User)
# async def getUserDetail(id:int) -> User:
#     user=list(filter(lambda u:u.id==id,users))
#     if len(user) > 0:
#         return {"user":user[id]}
#     else:
#         raise HTTPException(status_code=404,detail=f'tidak ada data untuk pengguna dengan id: {id}')
