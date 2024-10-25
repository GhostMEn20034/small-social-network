import os
from celery import Celery
from celery.utils.log import get_task_logger

from src.core.containers import Container

celery = Celery(__name__)
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL")
celery.conf.result_backend = os.getenv("CELERY_BROKER_URL")

# Initialize Dependency Container
container = Container()
container.wire(
    ['src.tasks.comments'],
)


celery.autodiscover_tasks(["src.tasks"])

logger = get_task_logger(__name__)