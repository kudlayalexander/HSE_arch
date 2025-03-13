from typing import List, Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Form
from sqlalchemy.orm import Session

from ..database import get_db
from ..exceptions import (DeviceNotFoundError, EmptyFileExtensionError,
                          ImageFileNotFoundError, InvalidFileExtensionError,
                          UnspecifiedDeviceHostnameError, ImageNotFoundInDatabaseError)
from ..enums import ImageType
from .schemas import ImageSchema, ImageUploadSchema
from . import service as image_service

router = APIRouter(prefix="/image", tags=["Image"])


@router.get('', response_model=List[ImageSchema])
async def image_list(
        db: Session = Depends(get_db)
):

    images: List[ImageSchema] = image_service.get_images(
        db
    )

    return images


@router.get('/get_by_id', response_model=ImageSchema)
async def get_image_single(id: str, db: Session = Depends(get_db)):
    try:
        image: ImageSchema = image_service.get_image(db, id)

        return image
    except ImageNotFoundInDatabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.get('/get_by_device', response_model=ImageSchema)
async def get_image_by_device_hostname(device_hostname: str, db: Session = Depends(get_db)):
    try:
        image: ImageSchema = image_service.get_by_device_hostname(
            db, device_hostname)

        return image
    except ImageNotFoundInDatabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.post("/upload", response_model=ImageSchema)
async def upload_single_file(
    image_type: Annotated[ImageType, Form()],
    image_version: Annotated[str, Form()],
    device_hostname: Annotated[str, Form()],
    commit: Annotated[str, Form()],
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload image
    """
    try:
        created_image: ImageSchema = await image_service.save_image(db,
                                                                    file=file,
                                                                    image_type=image_type,
                                                                    image_version=image_version,
                                                                    device_hostname=device_hostname,
                                                                    commit=commit
                                                                    )

        return created_image
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
    except UnspecifiedDeviceHostnameError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
    except ImageFileNotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
    except InvalidFileExtensionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
    except EmptyFileExtensionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=[str(exc), str(type(exc))])


@router.delete('/remove_by_id', response_model=ImageSchema)
async def remove_image_by_id(
    image_id: str,
    db: Session = Depends(get_db)
):
    try:
        removed_image_schema: ImageSchema = image_service.delete_image(
            db, image_id)
        return removed_image_schema
    except ImageFileNotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
    except ImageNotFoundInDatabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.delete('/remove_by_hostname', response_model=ImageSchema)
async def remove_image_by_hostname(
    hostname: str,
    db: Session = Depends(get_db)
):
    try:
        removed_image_schema: ImageSchema = image_service.delete_image_by_hostname(
            db, hostname)
        return removed_image_schema
    except ImageFileNotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
    except ImageNotFoundInDatabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
