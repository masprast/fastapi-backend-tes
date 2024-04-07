from uuid import UUID, uuid4
from sqlalchemy.orm import Session

from model.userModel import UserModel


async def getAllUser(db: Session):
    return db.query(UserModel).all()


async def getDetilUser(id: UUID, db: Session):
    return db.query(UserModel).filter(UserModel.id == id).first()


async def getUserByUsername(username: str, db: Session):
    return db.query(UserModel).filter(UserModel.username == username).first()


async def getUserByEmail(email: str, db: Session):
    return db.query(UserModel).filter(UserModel.email == email).first()


async def addUser(user: UserModel, db: Session):
    user.id = str(uuid4().hex)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def patchUser(user: dict, id: int, db: Session):
    dataBaru = db.query(UserModel).filter(UserModel.id == id)
    dataBaru.update(user, synchronize_session=False)
    db.commit()
    db.refresh(dataBaru.first())
    return dataBaru.first()


async def deleteUser(id: int, db: Session):
    dataYGDihapus = db.query(UserModel).filter(UserModel.id == id)
    dataYGDihapus.delete(synchronize_session=False)
    db.commit()
