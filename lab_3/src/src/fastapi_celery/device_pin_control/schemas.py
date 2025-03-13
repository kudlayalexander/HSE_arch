from pydantic import BaseModel
from typing import Optional


class BolidPinSchema(BaseModel):
    id: str
    number: int
    bolid_name: str

    class Config:
        from_attributes = True


class BolidPinCreateSchema(BaseModel):
    number: int
    bolid_name: str


class BolidPinCreateRangeSchema(BaseModel):
    number_from: int
    number_to: int
    bolid_name: str
