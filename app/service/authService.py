import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError
from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import ValidationError

from app.base.tokenBase import TokenPayload

load_dotenv("secret.env")

ACCESS_TOKEN_EXP_MIN = 30
REFRESH_TOKEN_EXP_DAY = 7
ALGORITHM = "HS256"
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_REFRESH_SECRET = os.environ["JWT_REFRESH_SECRET"]

enkriptor = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hashing(password: str):
    return enkriptor.hash(password)


def verifying(password: str, hashed: str):
    return enkriptor.verify(password, hashed)


def createAccessToken(data: dict, exp: timedelta | None = None):
    to_encode = data.copy()
    # print(to_encode)
    if exp:
        exp = datetime.now(timezone.utc) + exp
    else:
        exp = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXP_MIN)

    # to_encode.update({"exp": datetime(exp).strftime("%Y-%m-%d %H:%M:%S")})
    to_encode.update({"exp": exp})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)


def createRefreshToken(data: dict, exp: timedelta | None = None):
    to_encode = data.copy()
    if exp:
        exp = datetime.now(timezone.utc) + exp
    else:
        exp = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXP_DAY)

    to_encode.update({"exp": exp})
    return jwt.encode(data, JWT_REFRESH_SECRET, algorithm=ALGORITHM)


def verifyToken(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        # data = payload.get("sub")
        data = TokenPayload(**payload)
        print("data: ", data)
        if datetime.fromtimestamp(data.exp) > datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="credential tidak valid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return data


# def emailValidator(email: str):
#     try:
#         validation = validate_email(email, check_deliverability=False)
#         return validation.email
#     except EmailNotValidError as e:
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail=f"email '{email}' tidak valid. {str(e)}",
#         )
