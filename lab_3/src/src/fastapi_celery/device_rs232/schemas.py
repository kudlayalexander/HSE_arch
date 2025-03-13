from pydantic import BaseModel, Field
from typing import Union, Optional

from pathlib import Path

#########################
# --- Queue Request --- #
#########################


class Rs232Request(BaseModel):
    hostname: str
    baudrate: Optional[int] = Field(gt=0, examples=[115200])
    timeout: float = Field(ge=0, examples=[0, 10])


class Rs232ReadRequest(Rs232Request):
    pass


class Rs232WriteRequest(Rs232Request):
    text: str


class Rs232WriteAndReadRequest(Rs232Request):
    text: str


##########################
# --- Queue Response --- #
##########################


class Rs232QueuedResponse(BaseModel):
    id: str
    location: Union[Path, str]

#########################
# --- Worker Result --- #
#########################


class Rs232Result(BaseModel):
    execution_time_s: Optional[float]


class Rs232ReadResult(Rs232Result):
    output: str


class Rs232WriteResult(Rs232Result):
    pass


class Rs232WriteAndReadResult(Rs232Result):
    output: str

###############################
# --- Task State Response --- #
###############################


class Rs232TaskResponse(BaseModel):
    id: str
    status: str
    meta: Optional[dict]
    result: Union[Rs232ReadResult, Rs232WriteResult,
                  Rs232WriteAndReadResult, None]
