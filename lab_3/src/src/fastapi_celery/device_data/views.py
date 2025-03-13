from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..device_data import service
from ..enums import (DeviceReservationStatus, DeviceConnectionStatus, DeviceTestStage,
                     DeviceType, DeviceTypeGroup)
from .schemas import DeviceSchema
from ..exceptions import DeviceNotFoundError

router = APIRouter(prefix="/device_data", tags=["Device Data"])


@router.get('', response_model=List[DeviceSchema])
async def device_list(
    types: List[DeviceType] = Query(
        None, description="List of device types to filter by"),
    connection_status: Optional[DeviceConnectionStatus] = Query(
        None, description="Filter by connection status"),
    test_stage: Optional[DeviceTestStage] = Query(
        None, description="Filter by test stage"),
    type_group: Optional[DeviceTypeGroup] = Query(
        None, description="Filter by type group"),

        db: Session = Depends(get_db)):

    devices: List[DeviceSchema] = service.get_devices(
        db,
        device_types=types,
        connection_status=connection_status,
        test_stage=test_stage,
        type_group=type_group
    )

    return devices


@router.get('/{device_hostname}', response_model=DeviceSchema)
async def get_device_single(hostname: str, db: Session = Depends(get_db)):
    try:
        device: DeviceSchema = service.get_device(db, hostname)
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))

    return device