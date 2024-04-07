from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.base.userbase import UserBase, UserInDB
from app.model.userModel import UserModel
from app.service import userService
from app.db.db import get_db

router = APIRouter(prefix="/users", tags=["User"])


@router.get("/", response_model=List[UserBase])
async def getAllUser(db: Session = Depends(get_db)):
    users = await userService.getAllUser(db)
    return users


@router.post(
    "/tambah", status_code=status.HTTP_201_CREATED, response_model=List[UserBase]
)
async def tambahUser(
    user: UserInDB,
    # token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    ada = await userService.getUserByEmail(user.email, db)
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
async def detilUser(id: UUID, db: Session = Depends(get_db)):
    detil = await userService.getDetilUser(id, db)
    if detil is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"tidak ada data",
        )
    return detil


@router.delete("/hapus/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def hapusUser(
    id: int,
    # token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    hapus = db.query(UserModel).filter(UserModel.id == id)
    if hapus.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"tidak ada user dengan id: {id} untuk dihapus",
        )

    await userService.deleteUser(id, db)


@router.patch("/ubah/{id}", status_code=status.HTTP_200_OK, response_model=UserBase)
async def ubahUser(
    data: UserBase,
    id: int,
    # token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    ada = db.query(UserModel).filter(UserModel.id == id)
    if ada.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"tidak ada user dengan id: {id} untuk diubah",
        )

    data_dump = data.model_dump(exclude_unset=True)
    model = UserModel(data_dump)
    model.password = data_dump.get("hashed")
    perubahan = await userService.patchUser(model, id, db)
    return perubahan
