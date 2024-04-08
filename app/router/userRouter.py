import json
from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.base.tokenBase import TokenData
from app.base.userbase import UserBase, UserInDB
from app.model.userModel import UserModel
from app.router.jwtBearer import JWTBearer
from app.service import userService
from app.db.db import get_db
from app.service import authService
from app.service.authService import JWTdecode, oauth2_scheme

router = APIRouter(prefix="/users", tags=["User"])


def cek_super(token: Annotated[str, Depends(oauth2_scheme)]):
    tokendata = json.loads(JWTdecode(token).get("sub"))
    print("data: ", tokendata.get("is_super"))
    # user = userService.getDetilUser(TokenData(**tokendata), db)
    if tokendata.get("is_super"):
        return True

    return False


@router.get(
    "/",
    summary="hanya super user yang dapat melakukan CRUD operation",
    dependencies=[Depends(JWTBearer())],
)
async def getAllUser(
    super: Annotated[bool, Depends(cek_super)],
    db: Annotated[Session, Depends(get_db)],
):
    users = userService.getAllUser(db)
    listUser = list()
    for u in users:
        listUser.append(
            UserBase(
                username=u.username,
                email=u.email,
                is_super=u.is_super,
                last_login=u.last_login,
            )
        )

    if super:
        return users
    else:
        return listUser


@router.post(
    "/tambah",
    status_code=status.HTTP_201_CREATED,
    response_model=List[UserBase],
    dependencies=[Depends(JWTBearer())],
)
async def tambahUser(
    user: UserInDB,
    super: Annotated[bool, Depends(cek_super)],
    db: Session = Depends(get_db),
):
    if not super:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="hanya superuser yang dapat melakukan CRUD operation",
        )
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

    passHash = authService.hashing(user.password)
    user.password = passHash
    model = UserModel(**user.model_dump())
    userBaru = userService.addUser(model, db)
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


@router.delete(
    "/hapus/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(JWTBearer())],
)
async def hapusUser(
    id: str,
    super: Annotated[bool, Depends(cek_super)],
    db: Session = Depends(get_db),
):
    if not super:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="hanya superuser yang dapat melakukan CRUD operation",
        )
    hapus = userService.getDetilUser(id, db)
    if hapus is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"tidak ada user dengan id: {id} untuk dihapus",
        )

    userService.deleteUser(id, db)


@router.patch(
    "/ubah/{id}",
    status_code=status.HTTP_200_OK,
    response_model=UserBase,
    dependencies=[Depends(JWTBearer())],
)
async def ubahUser(
    data: UserBase,
    id: str,
    super: Annotated[bool, Depends(cek_super)],
    db: Session = Depends(get_db),
):
    if not super:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="hanya superuser yang dapat melakukan CRUD operation",
        )
    ada = userService.getDetilUser(id, db)
    if ada is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"tidak ada user dengan id: {id} untuk diubah",
        )

    data_dump = data.model_dump(exclude_unset=True)
    model = UserModel(**data_dump)
    model.password = data_dump.get("hashed")
    perubahan = userService.patchUser(data_dump, id, db)
    return perubahan
