from datetime import datetime
from pydantic import BaseModel

class UserBase(BaseModel):
    username:str
    password:str
    email:str|None=None
    is_super:bool
    last_login:datetime|None=None