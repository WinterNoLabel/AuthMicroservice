import jwt
from datetime import timedelta, datetime, timezone
from typing import Tuple, Optional

from fastapi import Depends, HTTPException
from starlette import status

from api.dependency.encrypted_decrypted_phone import encrypt
from api.dto.auth_dto import AuthRequestDTO, AuthRefreshTokenDTO, TokensCreateResponseDTO
from api.repositories.auth_repository import AuthRepository, get_auth_repository
from core.settings import settings
from models import User


class AuthService:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def get_or_create_user(self, data: AuthRequestDTO):
        encrypted_phone = await encrypt(data.phone_number)
        encrypted_password = await encrypt(data.password)
        user = await self.auth_repository.get_user_by_phone_number(encrypted_phone, encrypted_password, data.username)

        if not user:

            user = User(
                username=data.username,
                phone_number=encrypted_phone,
                password=encrypted_password
            )

            await self.auth_repository.create_user(user)

        access_token, refresh_token = await self.__create_tokens({"id": user.id, "username": data.username})

        return TokensCreateResponseDTO(access_token=access_token, refresh_token=refresh_token)


    async def __create_tokens(self, data: dict) -> Tuple[str, str]:
        # Время жизни токенов
        access_expires_delta = timedelta(hours=1)  # Время жизни access_token
        refresh_expires_delta = timedelta(days=7)  # Время жизни refresh_token

        # Создаем access_token
        access_payload = data.copy()
        access_payload.update({"exp": datetime.utcnow() + access_expires_delta})
        access_token = jwt.encode(access_payload, settings.jwt_settings.secret_key,
                                  algorithm=settings.jwt_settings.algorithm)

        # Создаем refresh_token
        refresh_payload = data.copy()
        refresh_payload.update({"exp": datetime.utcnow() + refresh_expires_delta})
        refresh_token = jwt.encode(refresh_payload, settings.jwt_settings.secret_key,
                                   algorithm=settings.jwt_settings.algorithm)

        return access_token, refresh_token

    async def __decode_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.jwt_settings.secret_key, algorithms=[settings.jwt_settings.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    async def refresh_token_service(self, data: AuthRefreshTokenDTO):
        # Декодируем токен
        decode_refresh_token = await self.__decode_token(data.refresh_token)

        # Проверяем, что токен был успешно декодирован
        if decode_refresh_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный или просроченный токен обновления.",
            )

        # Проверка на истечение времени токена
        current_timestamp = datetime.now(tz=timezone.utc).timestamp()
        if decode_refresh_token['exp'] < current_timestamp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен обновления истек."
            )

        # Проверка, что пользователь из токена существует и данные совпадают
        user_from_token = await self.auth_repository.check_user_from_token(
            id=decode_refresh_token.get('id'), username=decode_refresh_token.get('username'))

        if user_from_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден или данные токена не совпадают."
            )

        user_data = {"id": user_from_token.id, "username": user_from_token.username}
        new_access_token, new_refresh_token = await self.__create_tokens(user_data)

        return TokensCreateResponseDTO(access_token=new_access_token, refresh_token=new_refresh_token)

def get_auth_service(auth_repository: AuthRepository = Depends(get_auth_repository)) -> AuthService:
    return AuthService(auth_repository)
