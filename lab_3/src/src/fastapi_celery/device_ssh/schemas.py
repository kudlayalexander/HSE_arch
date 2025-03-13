from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, Field

#########################
# --- Queue Request --- #
#########################


class SshRequest(BaseModel):
    cmd: str
    hostname: str
    is_prod: bool
    username: str
    password: str
    port: Optional[int]
    retries: int = Field(default=3)
    retry_timeout: int = Field(default=5)
    cmd_timeout: int = Field(default=5)

##########################
# --- Queue Response --- #
##########################


class SshQueuedResponse(BaseModel):
    id: str
    location: Union[Path, str]

#########################
# --- Worker Result --- #
#########################


class SshResult(BaseModel):
    stdout: Optional[str]
    stderr: Optional[str]
    retcode: Optional[int]
    execution_time_s: Optional[float]

###############################
# --- Task State Response --- #
###############################


class SshTaskResponse(BaseModel):
    id: str
    status: str
    meta: Optional[dict]
    result: Optional[SshResult]
