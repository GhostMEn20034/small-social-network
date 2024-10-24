from fastapi import FastAPI
from .containers import Container
from src.routes.user import router as user_router
from src.routes.auth import router as auth_router
from src.routes.post import router as post_router
from src.routes.comment import router as comment_router


def create_app() -> FastAPI:
    api_v1_prefix = "/api/v1"

    container = Container()
    modules_to_wire = [
        'src.routes.auth',
        'src.routes.user',
        'src.routes.post',
        'src.routes.comment',
    ]
    container.wire(modules=modules_to_wire)

    app = FastAPI()
    app.container = container

    app.include_router(auth_router, prefix=api_v1_prefix)
    app.include_router(user_router, prefix=api_v1_prefix)
    app.include_router(post_router, prefix=api_v1_prefix)
    app.include_router(comment_router, prefix=api_v1_prefix)

    return app