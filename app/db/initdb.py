import os
from uuid import uuid4
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy_utils import database_exists, create_database

from app.model.userModel import UserModel
from app.db.db import engine, Base
from app.service.authService import hashing

load_dotenv("local.env")


class InitDB:
    def buat_db(self):
        if not database_exists(engine.url):
            create_database(engine.url)
            print(f"""database {os.environ['POSTGRES_DB']}: generated""")
        else:
            print(f"""database {os.environ['POSTGRES_DB']}: sudah ada""")

        Base.metadata.create_all(engine)

    def buat_superuser(self):
        query = (
            insert(UserModel)
            .values(
                id=str(uuid4().hex),
                username="super",
                password=hashing("user"),
                is_super=True,
            )
            .on_conflict_do_nothing(index_elements=[UserModel.username])
            .returning(UserModel)
        )
        with engine.connect() as conn:
            ada = conn.execute(query)
            if len(ada.fetchall()) > 0:
                conn.commit()
                print("generate akun superuser")
            else:
                print("akun superuser sudah ada")

    def __init__(self) -> None:
        self.__class__.buat_db(self)
        self.__class__.buat_superuser(self)


# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=InitDB.engine)
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
