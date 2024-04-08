from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.db.initdb import InitDB
from app.router import authRouter, uploadRouter, userRouter

load_dotenv("local.env")

app = FastAPI()
app.include_router(authRouter.router)
app.include_router(userRouter.router)
app.include_router(uploadRouter.router)

InitDB()
# db_dependency = Annotated(Session,Depends(get_db))
app.mount("/files", StaticFiles(directory="files"), "files")


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
