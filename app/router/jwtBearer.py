from fastapi import HTTPException, Request, status
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from app.service.authService import JWTdecode


class JWTBearer(HTTPBearer):
    def __init__(self, *, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credential = await super(JWTBearer, self).__call__(request)
        if credential:
            if not credential.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="access FORBIDDEN"
                )
            if not self.verifyJWT(credential.credentials):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="access FORBIDDEN"
                )
            return credential.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="access FORBIDDEN"
            )

    def verifyJWT(self, jwtToken: str):
        isValid = False
        try:
            payload = JWTdecode(jwtToken)
        except:
            payload = None

        if payload:
            isValid = True
        return isValid
