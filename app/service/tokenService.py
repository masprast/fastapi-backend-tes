from uuid import UUID
from sqlalchemy.orm import Session
from jose import jwt

from app.base.tokenBase import TokenPayload
from app.model.tokenModel import TokenModel


def addToken(token: TokenModel, db: Session):
    db.add(token)
    db.commit()
    db.refresh(token)


def getToken(id: UUID, db: Session):
    return db.query(TokenModel).filter(TokenModel.userId == id).first()


def updateToken(id: UUID, token: dict, db: Session):
    tokenLama = db.query(TokenModel).filter(TokenModel.userId == id)
    tokenLama.update(token, synchronize_session=False)
    db.commit()
    db.refresh(tokenLama.first())
    return tokenLama.first()


def getTGL(token: TokenPayload, tipe: str):
    tgl = jwt.decode(token.model_dump().get(tipe))
