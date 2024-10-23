from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import inject, Provide

from src.core.containers import Container
from src.models.user import User
from src.schemes.user import UserCreate, UserReadSchema, UserUpdateSchema
from src.services.user.abstract import AbstractUserService
from src.dependencies.auth import get_current_user

router = APIRouter(
    prefix='/users',
    tags=['users']
)


@router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=UserReadSchema)
@inject
async def signup(user_data: UserCreate,
                 user_service: AbstractUserService = Depends(Provide[Container.user_service])
                 ):
    return await user_service.user_signup(user_data)


@router.get('/details', response_model=UserReadSchema)
async def get_user_details(user: User = Depends(get_current_user)):
    return UserReadSchema(**user.model_dump())

@router.put('/update', response_model=UserReadSchema)
@inject
async def update_user(
        user_update_data: UserUpdateSchema,
        user: User = Depends(get_current_user),
        user_service: AbstractUserService = Depends(Provide[Container.user_service]),
):
    return await user_service.update_user(user, user_update_data)


@router.put('/change-password', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def change_password(
        user: User = Depends(get_current_user)
):
    pass