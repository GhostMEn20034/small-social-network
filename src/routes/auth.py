from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from dependency_injector.wiring import inject, Provide

from src.schemes.auth.token_data import RefreshTokenRequest
from src.services.auth.abstract import AbstractAuthService
from src.core.containers import Container

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

@router.post('/token')
@inject
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        auth_service: AbstractAuthService = Depends(Provide[Container.auth_service])
):
    return await auth_service.provide_tokens(form_data)

@router.post('/token/refresh', response_model=str)
@inject
async def update_access_token(
        refresh_token_req: RefreshTokenRequest,
        auth_service: AbstractAuthService = Depends(Provide[Container.auth_service]),
):

    return await auth_service.refresh_access_token(refresh_token_req.refresh_token)
