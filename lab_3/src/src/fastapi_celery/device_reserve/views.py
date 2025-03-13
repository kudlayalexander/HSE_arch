from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..device_reserve import service as device_reserve_service
from .schemas import ReservationSchema, ReservationRequest
from ..exceptions import ReservationNotFoundError, DeviceNotFoundError, NotEnoughAvailableDevicesError, NotEnoughDevicesError

router = APIRouter(prefix="/device_reserve", tags=["Device Reserve"])


@router.get('', response_model=List[ReservationSchema])
async def get_reservations_list(
        db: Session = Depends(get_db)
):
    reservations_list: List[ReservationSchema] = device_reserve_service.get_reservations(
        db
    )

    return reservations_list


@router.get('/get_by_id', response_model=ReservationSchema)
async def get_reservation_by_id(
    id: str,
    db: Session = Depends(get_db)
):
    try:
        reservation = device_reserve_service.get_reservation_by_id(
            db=db, reservation_id=id)

        return reservation
    except ReservationNotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.get('/get_by_hostname', response_model=ReservationSchema)
async def get_reservation_by_id(
    hostname: str,
    db: Session = Depends(get_db)
):
    try:
        reservation_schema = device_reserve_service.get_reservation_by_device(
            db=db,
            hostname=hostname
        )

        return reservation_schema
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.post('/create', response_model=ReservationSchema)
async def create_reservation(
    reservation_request: ReservationRequest,
    db: Session = Depends(get_db)
):
    try:
        reservation_schema = device_reserve_service.create_reservation(
            db=db,
            reservation_request=reservation_request
        )

        return reservation_schema
    except NotEnoughAvailableDevicesError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
    except NotEnoughDevicesError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.delete('/delete_by_id', response_model=ReservationSchema)
async def delete_by_id(
    id: str,
    db: Session = Depends(get_db)
):
    try:
        reservation_schema = device_reserve_service.delete_reservation_by_id(
            db, id)

        return reservation_schema
    except ReservationNotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.delete('/delete_on_device', response_model=ReservationSchema)
async def delete_on_device(
    hostname: str,
    db: Session = Depends(get_db)
):
    try:
        reservation_schema = device_reserve_service.delete_reservation_by_device(
            db=db,
            hostname=hostname
        )

        return reservation_schema
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
