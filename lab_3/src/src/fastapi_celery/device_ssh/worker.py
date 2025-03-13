from celery import Celery
from ..config import env_settings

ssh_worker = Celery('ssh_worker',
                    broker_connection_retry_on_startup=True,
                    broker=env_settings.CELERY_BROKER_URL,
                    backend=env_settings.CELERY_RESULT_BACKEND,
                    include=['src.fastapi_celery.device_ssh.tasks']
                    )
ssh_worker.config_from_object('src.fastapi_celery.celeryconfig')

ssh_worker.conf.update(
    result_expires=3600,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC'
)
