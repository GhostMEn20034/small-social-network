from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import inject, Provide

from src.dependencies.auth import get_current_user
from src.models.user import User
from src.schemes.post.create import PostCreateSchema
from src.schemes.post.list import PostListItemSchema, PostListItemWithAuthorSchema
from src.schemes.post.details import PostDetails
from src.schemes.post.update import UpdatePostSchema
from src.services.post.abstraction import AbstractPostService
from src.core.containers import Container

router = APIRouter(
    prefix='/posts',
    tags=['posts']
)

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=PostListItemSchema)
@inject
async def create_post(
        create_post_schema: PostCreateSchema,
        user: User = Depends(get_current_user),
        post_service: AbstractPostService = Depends(Provide[Container.post_service])
):
    return await post_service.create_post(user, create_post_schema)


@router.get('/me', response_model=list[PostListItemSchema])
@inject
async def your_posts(
        user: User = Depends(get_current_user),
        post_service: AbstractPostService = Depends(Provide[Container.post_service]),
):
    return await post_service.get_user_posts(user)


@router.get('/', response_model=list[PostListItemWithAuthorSchema])
@inject
async def get_all_posts(post_service: AbstractPostService = Depends(Provide[Container.post_service])):
    return await post_service.get_all_posts_with_authors()


@router.get('/{post_id}', response_model=PostDetails)
@inject
async def get_specific_post(
        post_id: int,
        post_service: AbstractPostService = Depends(Provide[Container.post_service])
):
    return await post_service.get_post_with_related_data(post_id)

@router.put('/{post_id}', response_model=PostListItemSchema)
@inject
async def update_post(
    post_id: int,
    update_post_scheme: UpdatePostSchema,
    user: User = Depends(get_current_user),
    post_service: AbstractPostService = Depends(Provide[Container.post_service]),
):
    return await post_service.update_post(user, post_id, update_post_scheme)

@router.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_post(
    post_id: int,
    user: User = Depends(get_current_user),
    post_service: AbstractPostService = Depends(Provide[Container.post_service]),
):
    await post_service.delete_post(user, post_id)