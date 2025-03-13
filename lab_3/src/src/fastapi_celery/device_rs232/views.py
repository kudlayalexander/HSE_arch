from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from ..database import get_db
from typing import Annotated
from ..device_data.schemas import DeviceSchema
from ..device_data.service import get_device
from celery import states
from .schemas import (Rs232QueuedResponse, Rs232ReadRequest, Rs232ReadResult,
                      Rs232TaskResponse, Rs232WriteAndReadRequest,
                      Rs232WriteAndReadResult, Rs232WriteRequest,
                      Rs232WriteResult)
from .tasks import (rs232_worker, rs232_read_task, rs232_write_and_read_task,
                    rs232_write_task)

router = APIRouter(prefix="/device_rs232", tags=["Device RS232"])


@router.post("/read", status_code=202, response_model=Rs232QueuedResponse)
def read(request: Annotated[Rs232ReadRequest, "Rs232 Read Request"], db: Session = Depends(get_db)) -> Rs232QueuedResponse:
    device: DeviceSchema = get_device(db=db, hostname=request.hostname)

    task = rs232_read_task.delay(
        port=device.rs232_port,
        timeout=request.timeout,
        baudrate=request.baudrate
    )

    response = Rs232QueuedResponse(id=task.id, location=f"/queue/{task.id}")
    return response


@router.post("/write", status_code=202, response_model=Rs232QueuedResponse)
def write(request: Rs232WriteRequest, db: Session = Depends(get_db)) -> Rs232QueuedResponse:
    device: DeviceSchema = get_device(db=db, hostname=request.hostname)

    task = rs232_write_task.delay(
        port=device.rs232_port,
        text=request.text,
        baudrate=request.baudrate,
        timeout=request.timeout
    )

    response = Rs232QueuedResponse(id=task.id, location=f"/queue/{task.id}")
    return response


@router.post("/write-and-read", status_code=202, response_model=Rs232QueuedResponse)
def write_and_read(request: Rs232WriteAndReadRequest, db: Session = Depends(get_db)) -> Rs232QueuedResponse:
    device: DeviceSchema = get_device(db=db, hostname=request.hostname)

    task = rs232_write_and_read_task.delay(
        port=device.rs232_port,
        text=request.text,
        baudrate=request.baudrate,
        timeout=request.timeout
    )

    response = Rs232QueuedResponse(id=task.id, location=f"/queue/{task.id}")
    return response


@router.get("/queue/{task_id}", response_model=Rs232TaskResponse)
async def get_status(task_id, response: Response) -> Rs232TaskResponse:
    """URL used to receive updates on Celery tasks."""
    rs232_task = AsyncResult(task_id, app=rs232_worker)

    rs232_task_response = Rs232TaskResponse(
        id=task_id,
        status=rs232_task.state,
        meta=rs232_task.info,
        result=None
    )

    task_name = rs232_task.name

    if rs232_task.state == states.SUCCESS:
        if task_name == "rs232_read":
            task_result = Rs232ReadResult(**rs232_task.result)
        elif task_name == "rs232_write":
            task_result = Rs232WriteResult(**rs232_task.result)
        elif task_name == "rs232_write_and_read":
            task_result = Rs232WriteAndReadResult(**rs232_task.result)
        else:
            response.status_code = 500
            raise HTTPException(
                status_code=500, detail="Unknown task name (do you need /device_rs232 route??)")

        rs232_task_response.result = task_result

    return rs232_task_response
