from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .schemas import BolidSchema
from . import service as bolid_service
from ..exceptions import BolidNotFoundError

router = APIRouter(prefix="/bolid")


@router.get('', response_model=List[BolidSchema])
async def get_bolids_list(
        db: Session = Depends(get_db)
):
    bolids_list: List[BolidSchema] = bolid_service.get_bolids(
        db
    )

    return bolids_list


@router.get('/get_by_name', response_model=BolidSchema)
async def get_bolid_by_name(
    name: str,
    db: Session = Depends(get_db)
):
    try:
        reservation = bolid_service.get_bolid_by_name(
            db=db, bolid_name=name)

        return reservation
    except BolidNotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
