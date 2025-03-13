from pydantic import BaseModel, Field
from typing import Union, Optional, Dict

from ..enums import StandUser, DeviceType

from ..device_data.schemas import DeviceSchema
from datetime import datetime


class ReservationSchema(BaseModel):
    id: str
    reserved_by: StandUser
    time_start: Optional[datetime]
    time_end: Optional[datetime]

    class Config:
        from_attributes = True


class ReservationRequest(BaseModel):
    reserved_by: StandUser
    requested_types: Dict[DeviceType, int]
    time_end: Optional[datetime]
