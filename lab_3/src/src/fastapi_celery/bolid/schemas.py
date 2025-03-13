from pydantic import BaseModel
from typing import List


class BolidSchema(BaseModel):
    name: str
    port: str
    pin_capacity: int
    baudrate: int
    parity: str
    stopbits: int
    bytesize: int
    class Config:
        from_attributes = True

class BolidCreateSchema(BaseModel):
    name: str
    port: str
    pin_capacity: int
    baudrate: int
    parity: str
    stopbits: int
    bytesize: int
