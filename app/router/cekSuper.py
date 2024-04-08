# import json
# from sqlalchemy.orm import Session

# from app.base.tokenBase import TokenData
# from app.service import userService
# from app.service.authService import JWTdecode


# class CekSuper:
#     def __init__(self, token: str, db: Session):
#         tokendata = json.loads(JWTdecode(token).sub)
#         user = userService.getDetilUser(TokenData(**tokendata), db)
#         if user.is_super:
#             is_super = True
#         is_super = False
#         super().__init__(is_super)
