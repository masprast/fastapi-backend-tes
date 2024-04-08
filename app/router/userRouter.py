import json
from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.base.tokenBase import TokenData
from app.base.userbase import UserBase, UserInDB
from app.model.userModel import UserModel
from app.service import userService
from app.db.db import get_db
from app.service import authService
from app.service.authService import JWTdecode, oauth2_scheme

router = APIRouter(prefix="/users", tags=["User"])


async def cek_super(token: str, db=Session):
    tokendata = json.loads(JWTdecode(token).sub)
    user = await userService.getDetilUser(TokenData(**tokendata), db)
    if user.is_super:
        return True

    return False


@router.get("/", summary="hanya super user yang dapat melakukan CRUD operation")
async def getAllUser(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
):
    tokendata = TokenData(**json.loads(authService.JWTdecode(token).sub))
    users = userService.getAllUser(db)
    listUser = List[UserBase]
    for u in users:
        listUser.append(
            UserBase(
                username=u.username,
                email=u.email,
                is_super=u.is_super,
                last_login=u.last_login,
            )
        )

    if tokendata.is_super:
        return users
    else:
        return listUser


@router.post(
    "/tambah", status_code=status.HTTP_201_CREATED, response_model=List[UserBase]
)
async def tambahUser(
    user: UserInDB,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    ada = userService.getUserByEmail(user.email, db)
    if ada:
        pesan = ""
        if ada.username == user.username and ada.email == user.email:
            pesan = f"username {user.username} dan email {user.email}"
        elif ada.username == user.username:
            pesan = f"username {user.username}"
        else:
            pesan = f"email {user.email}"

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{pesan} sudah ada",
        )

    data_dump = user.model_dump()
    model = UserModel(data_dump)
    model.password = data_dump.get("hashed")
    userBaru = await userService.addUser(model, db)
    return [userBaru]


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=UserBase)
async def detilUser(id: str, db: Session = Depends(get_db)):
    detil = userService.getDetilUser(UUID(id), db)
    if detil is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"tidak ada data",
        )
    return detil


@router.delete("/hapus/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def hapusUser(
    id: str,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    hapus = userService.getDetilUser(id, db)
    if hapus.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"tidak ada user dengan id: {id} untuk dihapus",
        )

    await userService.deleteUser(id, db)


@router.patch("/ubah/{id}", status_code=status.HTTP_200_OK, response_model=UserBase)
async def ubahUser(
    data: UserBase,
    id: str,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    ada = userService.getDetilUser(id, db)
    if ada.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"tidak ada user dengan id: {id} untuk diubah",
        )

    data_dump = data.model_dump(exclude_unset=True)
    model = UserModel(data_dump)
    print(model)
    model.password = data_dump.get("hashed")
    perubahan = await userService.patchUser(data_dump, id, db)
    return perubahan
