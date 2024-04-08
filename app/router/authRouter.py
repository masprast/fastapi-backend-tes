from datetime import datetime, timezone
from typing import Annotated
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.base.authBase import AuthBase, AuthOutput
from app.base.tokenBase import Token, TokenData
from app.base.userbase import UserBase, UserInDB
from app.db.db import get_db
from app.model.userModel import UserModel
from app.router.jwtBearer import JWTBearer
from app.service import tokenService, userService
from app.service import authService
from app.service.authService import (
    createAccessToken,
    createRefreshToken,
    hashing,
    kirimEmail,
    oauth2_scheme,
)

load_dotenv("private.env")

router = APIRouter(prefix="/auth", tags=["Auth"])


def getUser(
    token: Annotated[str, Depends(oauth2_scheme)],
    sesion: Annotated[Session, Depends(get_db)],
):
    print("token", token)
    user = authService.getCurrentUser(token, sesion)
    currentUser = authService.userAktif(user)
    return currentUser


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=AuthOutput
)
async def registerUser(user: AuthBase, session: Annotated[Session, Depends(get_db)]):
    adaUser = userService.getUserByEmail(user.email, session)
    if adaUser:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="user sudah ada"
        )

    userBaru = AuthBase(password=hashing(user.password), email=user.email)
    buatUser = userService.addUser(UserModel(**userBaru.model_dump()), session)
    # return {
    #     "pesan": f"user {buatUser.username} dengan email {buatUser.email} berhasil registrasi"
    # }
    token = TokenData(
        email=buatUser.email, id=buatUser.id, is_super=buatUser.is_super
    ).model_dump()
    token.update({"id": str(token.get("id"))})
    access_token = createAccessToken(token)

    # kirimEmail(access_token, buatUser.email)

    return AuthOutput(
        id=token.get("id"),
        email=buatUser.email,
        accessToken=access_token,
        created_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    )


# @router.post("/login", response_model=Token)
# async def loginUser(
#     user: Annotated[AuthBase, Depends()], session: Annotated[Session, Depends(get_db)]
# ):
#     adauser = userService.getUserByEmail(user.email, session)
#     if adauser is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"tidak ada user dengan email {user.email}",
#         )

#     if not verifying(user.password, adauser.password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="tidak memenuhi credential",
#         )


#     dataUser = TokenData(
#         id=adauser.id, email=adauser.email, is_super=adauser.is_super
#     ).model_dump()
#     dataUser.update({"id": str(dataUser.get("id"))})
#     access_token = createAccessToken(dataUser)
#     refresh_token = createRefreshToken(dataUser)
#     # print(
#     #     "jwt: ",
#     #     jwt.decode(access_token, authService.JWT_SECRET, [authService.ALGORITHM]),
#     # )
#     # userId = authService.getCurrentUserID(access_token)
#     # gettedUser=userService.getDetilUser(userId)
#     # gettedUser.last_login = datetime.now()  # .strftime("%Y-%m-%d %H:%M:%S")
#     updatedUserLastLogin = userService.patchUser(
#         {"last_login": datetime.now()}, dataUser.get("id"), session
#     )
#     tokenModel = TokenModelBase(
#         userId=updatedUserLastLogin.id,
#         access_token=access_token,
#         refresh_token=refresh_token,
#     )
#     # tokenModel.update({"userId": str(tokenModel.get("userId"))})
#     adatoken = tokenService.getToken(tokenModel.userId, session)
#     # verifiedToken=authService.verifyToken(adatoken.access_token)
#     if not adatoken:
#         tokenService.addToken(
#             TokenModel(**tokenModel.model_dump(exclude_unset=True)), session
#         )
#     # return {"access_token": access_token, "refresh_token": refresh_token}
#     return Token(accessToken=access_token, refreshToken=refresh_token).model_dump()
@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_db)],
):
    cekUser = authService.authenticateUser(
        form_data.username, form_data.password, session
    )
    if not cekUser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="invalid credential"
        )
    dataToken = TokenData(
        id=cekUser.id, email=cekUser.email, is_super=cekUser.is_super
    ).model_dump()
    dataToken.update({"id": str(dataToken.get("id"))})
    accessToken = createAccessToken(dataToken)
    refreshToken = createRefreshToken(dataToken)
    return Token(accessToken=accessToken, refreshToken=refreshToken).model_dump()


@router.get("/me", response_model=UserInDB, dependencies=[Depends(JWTBearer())])
async def aboutMe(me: Annotated[UserBase, Depends(getUser)]):
    return me
