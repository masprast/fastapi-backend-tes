from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import os
from datetime import datetime, timedelta, timezone
import smtplib
import ssl
from uuid import UUID
from dotenv import load_dotenv
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.base.tokenBase import Token, TokenData, TokenPayload
from app.base.userbase import UserBase, UserInDB
from app.model.userModel import UserModel
from app.service import tokenService, userService

load_dotenv("secret.env")

ACCESS_TOKEN_EXP_MIN = 30
REFRESH_TOKEN_EXP_DAY = 7
ALGORITHM = "HS256"
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_REFRESH_SECRET = os.environ["JWT_REFRESH_SECRET"]

enkriptor = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", scheme_name="JWT")


def hashing(password: str):
    return enkriptor.hash(password)


def verifying(password: str, hashed: str):
    return enkriptor.verify(password, hashed)


def authenticateUser(email: str, password: str, sesion):
    adaUser = userService.getUserByEmail(email, sesion)
    print(adaUser)
    if adaUser:
        isVerified = verifying(password, adaUser.password)

    if not adaUser or not isVerified:
        return False

    return adaUser


def authHeder(token: str):
    authorized = JWTdecode(token)
    if authorized is None:
        return {}
    return authorized


def signJWT(payload: TokenPayload):
    token = jwt.encode(payload, JWT_SECRET, ALGORITHM)
    return token


def JWTdecode(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, [ALGORITHM])
        return TokenPayload(**payload).model_dump()
    except JWTError:
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED, detail="token tidak valid"
        # )
        return {}


def createAccessToken(data: dict, exp: timedelta | None = None):
    if exp:
        exp = datetime.now(timezone.utc) + exp
    else:
        exp = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXP_MIN)

    # to_encode.update({"exp": datetime(exp).strftime("%Y-%m-%d %H:%M:%S")})
    sekarang = datetime.fromisoformat(str(exp)).timestamp()
    to_encode = TokenPayload(sub=json.dumps(data), exp=int(sekarang)).model_dump()
    token = signJWT(to_encode)
    return token


def createRefreshToken(data: dict, exp: timedelta | None = None):
    if exp:
        exp = datetime.now(timezone.utc) + exp
    else:
        exp = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXP_DAY)

    sekarang = datetime.fromisoformat(str(exp)).timestamp()
    to_encode = TokenPayload(
        sub=json.dumps(data.copy()), exp=int(sekarang)
    ).model_dump()
    token = signJWT(to_encode)
    return token


def verifyToken(token: str):
    try:
        payload = JWTdecode(token)
        if payload:
            if datetime.fromtimestamp(payload.get("exp")) < datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="token expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="credential tidak valid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def getCurrentUser(token: str, sesion):
    try:
        payload = JWTdecode(token)
        data = {**json.loads(payload.get("sub"))}

        if data is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="credential tidak valid",
                headers={"WWW-Authenticate": "Bearer"},
            )
        tokenData = TokenData(
            id=data.get("id"),
            email=data.get("email"),
            is_super=data.get("is_super"),
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="credential tidak valid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    currentUser = userService.getDetilUser(tokenData.id, sesion)
    if currentUser is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="credential tidak valid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserInDB(
        username=currentUser.username,
        full_name=currentUser.full_name,
        email=currentUser.email,
        is_super=currentUser.is_super,
        last_login=currentUser.last_login,
        password=currentUser.password,
    )


def userAktif(user: UserBase):
    return user


def getUserData(id: UUID, sesion):
    return userService.getUserData(id, sesion)


def updateToken(id: UUID, token: Token, tipe: str, sesion):
    try:
        secret = JWT_SECRET if tipe == "access_token" else JWT_REFRESH_SECRET
        tokenStr = token.model_dump(exclude_unset=True).get(
            "accessToken" if secret == JWT_SECRET else "refreshToken"
        )
        # tokenTerinstall = jwt.decode(tokenStr, secret, [ALGORITHM])
        # tgl_token = tokenTerinstall.get("exp")
        tokenService.updateToken(id, tokenStr, sesion)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


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
        context = ssl.create_default_context()
        mailserver = smtplib.SMTP("smtp.gmail.com", 587)
        mailserver.starttls(context=context)
        mailserver.login(from_email, pass_email)
        mailserver.sendmail(from_email, email, pesan.as_string())
        return {"pesan": "email verifikasi berhasil dikirim"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"""tidak dapat mengirim email ke {email} | error: {e}""",
        )
    finally:
        mailserver.quit()
