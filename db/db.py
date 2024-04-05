from sqlalchemy.orm import sessionmaker

from db.initdb import InitDB

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=InitDB.engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
