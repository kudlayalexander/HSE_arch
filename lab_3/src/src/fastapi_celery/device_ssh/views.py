from celery import states
from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from ..database import get_db
from ..device_data.schemas import DeviceSchema
from ..device_data.service import get_device
from ..enums import ImageType, SshUser
from ..exceptions import (DeviceHasNoImageError, DeviceNotFoundError,
                          ImageNotFoundInDatabaseError)
from ..images.schemas import ImageSchema
from ..images.service import get_image
from .schemas import SshQueuedResponse, SshResult, SshTaskResponse
from .tasks import ssh_worker
from .tasks import task_ssh

router = APIRouter(prefix="/device_ssh", tags=["Device SSH"])


@router.post("", status_code=202, response_model=SshQueuedResponse)
def ssh_command(cmd: str, hostname: str, username: SshUser, db: Session = Depends(get_db)) -> SshQueuedResponse:
    try:
        device: DeviceSchema = get_device(db=db, hostname=hostname)

        if device.image_id is None:
            raise DeviceHasNoImageError(
                "You must upload image for device before using ssh command.")

        image: ImageSchema = get_image(db, device.image_id)

        task = task_ssh.delay(
            command=cmd,
            hostname=device.ip,
            username=username,
            device_type=device.type,
            image_type=image.type
        )

        response = SshQueuedResponse(id=task.id, location=f"/queue/{task.id}")
        return response
    except DeviceHasNoImageError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
    except ImageNotFoundInDatabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.get("/queue/{task_id}", response_model=SshTaskResponse)
async def get_status(task_id, response: Response):
    """URL used to receive updates on Celery tasks."""
    ssh_task = AsyncResult(task_id, app=ssh_worker)

    ssh_task_response = SshTaskResponse(
        id=task_id,
        status=ssh_task.state,
        meta=ssh_task.info,
        result=None
    )

    if ssh_task.state == states.SUCCESS:
        task_result = SshResult(**ssh_task.result)

        ssh_task_response.result = task_result

    return ssh_task_response
