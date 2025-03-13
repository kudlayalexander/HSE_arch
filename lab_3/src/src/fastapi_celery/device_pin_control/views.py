from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..exceptions import BolidNotFoundError
from . import service as bolid_pin_service
from .schemas import BolidPinSchema

router = APIRouter(prefix="/pin_control", tags=["Device Pin Control"])


@router.get('', response_model=List[BolidPinSchema])
async def get_pin_list(
        db: Session = Depends(get_db)
):
    bolids_list: List[BolidPinSchema] = bolid_pin_service.get_bolid_pins(
        db
    )

    return bolids_list


@router.get('/get_by_id', response_model=BolidPinSchema)
async def get_pin_by_id(
    id: str,
    db: Session = Depends(get_db)
):
    try:
        bolid_pin = bolid_pin_service.get_bolid_pin_by_id(
            db=db, bolid_pin_id=id)

        return bolid_pin
    except BolidNotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
