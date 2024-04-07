from datetime import datetime, timezone
import os
import smtplib
from typing import Annotated
from uuid import UUID
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from base.authBase import AuthBase, AuthOutput
from base.tokenBase import Token, TokenData, TokenModelBase
from base.userbase import UserBase
from db.db import get_db
from model.tokenModel import TokenModel
from model.userModel import UserModel
from service import tokenService, userService
from service.authService import (
    createAccessToken,
    createRefreshToken,
    hashing,
    verifyToken,
    verifying,
)

load_dotenv("private.env")

router = APIRouter(prefix="/auth", tags=["Auth"])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", scheme_name="JWT")


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=AuthOutput
)
async def registerUser(user: AuthBase, session: Annotated[Session, Depends(get_db)]):
    adaUser = await userService.getUserByEmail(user.email, session)
    if adaUser:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="user sudah ada"
        )

    userBaru = AuthBase(password=hashing(user.password), email=user.email)
    buatUser = await userService.addUser(UserModel(**userBaru.model_dump()), session)
    # return {
    #     "pesan": f"user {buatUser.username} dengan email {buatUser.email} berhasil registrasi"
    # }
    token = TokenData(email=buatUser.email, id=buatUser.id, is_super=buatUser.is_super)
    print(token.model_dump())
    access_token = createAccessToken(**token.model_dump())
    kirimEmail(access_token)
    return AuthOutput(
        id=buatUser.id,
        email=buatUser.email,
        created_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    )


@router.post("/login", response_model=Token)
async def loginUser(
    user: Annotated[AuthBase, Depends()], session: Annotated[Session, Depends(get_db)]
):
    # email = emailValidator(user.email)
    adauser = await userService.getUserByEmail(user.email, session)
    if adauser is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"tidak ada user dengan email {user.email}",
        )

    if not verifying(user.password, adauser.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="tidak memenuhi credential",
        )

    data = TokenData(
        id=adauser.id, email=adauser.email, is_super=adauser.is_super
    ).model_dump()
    data.update({"id": str(data.get("id"))})
    access_token = createAccessToken(data)
    refresh_token = createRefreshToken(data)
    tokenModel = TokenModelBase(
        userId=adauser.id, access_token=access_token, refresh_token=refresh_token
    )
    getteduser = await getUser(access_token, session)
    # await tokenService.addToken(
    #     TokenModel(**tokenModel.model_dump(exclude_unset=True)), session
    # )
    # return {"access_token": access_token, "refresh_token": refresh_token}
    return Token(accessToken=access_token, refreshToken=refresh_token).model_dump()


async def getUser(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session,
):
    verified = verifyToken(token).sub
    print("verified: ", verified)
    user = await userService.getUserByEmail(verified.get("email"), session)
    print("user: ", user)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="tidak ada user",
        )

    return UserBase(
        username=user.username,
        email=user.email,
        is_super=user.is_super,
        last_login=user.last_login,
    )


def kirimEmail(token: str, email: str):
    from_email = os.environ["EMAIL"]
    pass_email = os.environ["PASS"]

    alamat_email_verification = (
        f"""{os.environ['PENGIRIM']}/konfirmasi-email/{token}/"""
    )
    body_email = f"""
    <html>
    <body>
        <h1>Assalamualaikum,</h1>
        <br/>
        <p>Email ini dikirim ke {email} untuk verifikasi</p>
        <p>Berikut adalah link untuk verifikasi email anda:</p>
        <a href="{alamat_email_verification}">{alamat_email_verification}</a>
    </body>
    </html>
    """

    pesan = MIMEMultipart()
    pesan["From"] = from_email
    pesan["To"] = email
    pesan["Subject"] = "email verificaton"
    pesan.attach(MIMEText(body_email, "html"))

    try:
        mailserver = smtplib.SMTP("smtp.gmail.com", 587)
        mailserver.starttls()
        mailserver.login(from_email, pass_email)
        mailserver.sendmail(from_email, email, pesan.as_string())
        mailserver.quit()
        return {"pesan": "email verifikasi berhasil dikirim"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="tidak dapat mengirim email ke {email}",
        )
