from typing import List, Annotated
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status

from src.core.containers import Container
from src.dependencies.auth import get_current_user
from src.models.user import User
from src.schemes.comment.create import CreateCommentSchema
from src.schemes.comment.update import CommentUpdateSchema
from src.schemes.comment.read import CommentReadSchema, CommentWithRepliesSchema, DailyCommentAnalyticItem
from src.schemes.common import DateRange
from src.services.comment.abstract import AbstractCommentService

router = APIRouter(
    prefix='/comments',
    tags=['comments']
)

@router.get('/', response_model=List[CommentReadSchema],
            summary="Retrieve all top level comments for a specific post",
            )
@inject
async def get_all_top_level_comments(
        post_id: int,
        comment_service: AbstractCommentService = Depends(Provide[Container.comment_service]),
):
    """
    Retrieve all top level comments for a specific post
    """
    return await comment_service.get_top_level_comments(post_id)

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=CommentReadSchema)
@inject
async def create_comment(
    comment_data: CreateCommentSchema,
    user: User = Depends(get_current_user),
    comment_service: AbstractCommentService = Depends(Provide[Container.comment_service]),
):
    return await comment_service.create_comment(user, comment_data)

@router.get('/{comment_id}', response_model=CommentWithRepliesSchema)
@inject
async def get_specific_comment(
    comment_id: int,
    comment_service: AbstractCommentService = Depends(Provide[Container.comment_service])
):
    return await comment_service.get_comment_details(comment_id)

@router.put('/{comment_id}', response_model=CommentReadSchema)
@inject
async def edit_comment(
    comment_id: int,
    update_data: CommentUpdateSchema,
    user: User = Depends(get_current_user),
    comment_service: AbstractCommentService = Depends(Provide[Container.comment_service])
):
    return await comment_service.update_comment(comment_id, user, update_data)

@router.put('/{comment_id}/like', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def like_comment(
    comment_id: int,
    user: User = Depends(get_current_user),
    comment_service: AbstractCommentService = Depends(Provide[Container.comment_service])
):
    await comment_service.like_comment(comment_id, user)

@router.put('/{comment_id}/block', response_model=CommentReadSchema)
@inject
async def block_comment(
    comment_id: int,
    user: User = Depends(get_current_user),
    comment_service: AbstractCommentService = Depends(Provide[Container.comment_service]),
):
    return await comment_service.block_comment(comment_id, user)

@router.delete('/{comment_id}', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_comment(
        comment_id: int,
        user: User = Depends(get_current_user),
        comment_service: AbstractCommentService = Depends(Provide[Container.comment_service]),
):
    return await comment_service.delete_comment(comment_id, user)

@router.get('/analytics/daily-breakdown', response_model=List[DailyCommentAnalyticItem],
            summary="Returns the number of published, blocked comments on the user's posts grouped by day")
@inject
async def get_daily_comment_breakdown(
    date_range: Annotated[DateRange, Depends()],
    user: User = Depends(get_current_user),
    comment_service: AbstractCommentService = Depends(Provide[Container.comment_service]),
):
    return await comment_service.daily_comment_analytic(date_range, user)
