from typing import Annotated, Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from starlette import status
from core.settings import settings

bearer_scheme = HTTPBearer(auto_error=False)

async def get_user_from_token(
        token: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
):
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        # Декодируем и проверяем токен с использованием секретного ключа и алгоритма
        payload = jwt.decode(token.credentials, settings.jwt_settings.secret_key,
                             algorithms=[settings.jwt_settings.algorithm])
        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in or Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
