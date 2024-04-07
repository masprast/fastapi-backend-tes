from uuid import UUID
from model.tokenModel import TokenModel
from sqlalchemy.orm import Session


async def addToken(token: TokenModel, db: Session):
    db.add(token)
    db.commit()
    db.refresh(token)


async def getToken(id: UUID, db: Session):
    return db.query(TokenModel).filter(TokenModel.userId == id).first()


async def updateToken(id: UUID, token: str, db: Session):
    tokenLama = db.query(TokenModel).filter(TokenModel.userId == id)
    tokenLama.update(token, synchronize_session=False)
    db.commit()
    db.refresh(tokenLama.first())
