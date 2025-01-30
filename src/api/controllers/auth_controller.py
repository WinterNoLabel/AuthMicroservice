from fastapi import APIRouter, Depends
from api.services.auth_service import get_auth_service, AuthService
from api.dto.auth_dto import AuthRequestDTO, TokensCreateResponseDTO, AuthRefreshTokenDTO
from starlette import status


router = APIRouter(
    tags=["Авторизация"],
)


@router.post(
    "/auth",
    status_code=status.HTTP_200_OK,
    summary="Авторизация (Регистрация) пользователя",
    response_model=TokensCreateResponseDTO,
)
async def auth_me(
        data: AuthRequestDTO,
        service: AuthService = Depends(get_auth_service)
):
    return await service.get_or_create_user(data)

@router.post(
    '/refresh_token',
    summary="Обновление токена авторизации",
    status_code=status.HTTP_200_OK,
    response_model=TokensCreateResponseDTO
)
async def refresh_token_endpoint(
    data: AuthRefreshTokenDTO,
    service: AuthService = Depends(get_auth_service)
):
    return await service.refresh_token_service(data)

