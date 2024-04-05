import os
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy_utils import database_exists,create_database

from model.usermodel import UserModel,Base

load_dotenv('local.env')

class InitDB():
    query = ''
    engine = create_engine(os.environ['POSTGRES_URI'])
    engine.connect()

    def buat_db(self):
        if not database_exists(self.__class__.engine.url):
            create_database(self.__class__.engine.url)
            print(f'''database {os.environ['POSTGRES_DB']}: generated''')
        else:
            print(f'''database {os.environ['POSTGRES_DB']}: sudah ada''')
        Base.metadata.create_all(self.__class__.engine)


    def buat_superuser(self):
        query = insert(UserModel).values(username='super',password='user',is_super=True)\
            .on_conflict_do_nothing(index_elements=[UserModel.username]).returning(UserModel)
        with self.__class__.engine.connect() as conn:
            ada = conn.execute(query)
            if len(ada.fetchall()) > 0:
                conn.commit()
                print('generate akun superuser')
            else:
                print('akun superuser sudah ada')

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