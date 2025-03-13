from pydantic import BaseModel
from typing import Optional
from ..enums import ImageType
import uuid


class ImageSchema(BaseModel):
    id: str
    type: ImageType
    version: Optional[str]
    commit: Optional[str]
    filename: str

    class Config:
        from_attributes = True


class ImageUploadSchema(BaseModel):
    type: ImageType
    version: Optional[str]
    commit: Optional[str]
    device_hostname: str
