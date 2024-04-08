from uuid import UUID, uuid4
from sqlalchemy.orm import Session

from app.base.userbase import UserInDB
from app.model.userModel import UserModel


def getAllUser(db: Session):
    return db.query(UserModel).all()


def getDetilUser(id: UUID, db: Session):
    return db.query(UserModel).filter(UserModel.id == id).first()


def getUserData(id: UUID, db: Session):
    model = db.query(UserModel).filter(UserModel.id == id).first()
    return UserInDB(
        id=model.id,
        username=model.username,
        full_name=model.full_name,
        hashed=model.password,
        email=model.email,
        is_super=model.is_super,
        last_login=model.last_login,
    )


def getUserByUsername(username: str, db: Session):
    return db.query(UserModel).filter(UserModel.username == username).first()


def getUserByEmail(email: str, db: Session):
    return db.query(UserModel).filter(UserModel.email == email).first()


def addUser(user: UserModel, db: Session):
    user.id = uuid4().hex.replace("-", "")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def patchUser(user: dict, id: UUID, db: Session):
    dataBaru = db.query(UserModel).filter(UserModel.id == id)
    dataBaru.update(user, synchronize_session=False)
    db.commit()
    db.refresh(dataBaru.first())
    return dataBaru.first()


def deleteUser(id: UUID, db: Session):
    dataYGDihapus = db.query(UserModel).filter(UserModel.id == id)
    dataYGDihapus.delete(synchronize_session=False)
    db.commit()
