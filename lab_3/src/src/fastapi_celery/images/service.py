import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import List

from fastapi import UploadFile
from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from ..config import server_settings
from ..device_data.model import Device
from ..enums import ImageType
from ..exceptions import (DeviceNotFoundError, EmptyFileExtensionError,
                          ImageFileNotFoundError, ImageNotFoundInDatabaseError,
                          InvalidFileExtensionError,
                          UnspecifiedDeviceHostnameError)
from .convert_model_schema import convert_from_model_to_schema
from .model import Image
from .schemas import ImageSchema

logger = logging.getLogger()


def get_images(
    db: Session,
) -> List[ImageSchema]:

    images: List[Image] = db.query(Image).all()

    images_schemas = [convert_from_model_to_schema(
        image_db) for image_db in images]

    return images_schemas


def get_image(db: Session, id: str) -> ImageSchema:
    image_db: Image = db.query(Image).filter(
        Image.id == id).first()

    if image_db is None:
        raise ImageNotFoundInDatabaseError(f"Image with ID {id} not found")

    image_schema = convert_from_model_to_schema(image_db)

    return image_schema


def create_image(db: Session, image: ImageSchema) -> ImageSchema:
    image_db = Image(
        id=image.id,
        commit=image.commit,
        version=image.version,
        type=image.type,
        filename=image.filename
    )

    db.add(image_db)
    db.commit()
    db.refresh(image_db)

    image_schema = convert_from_model_to_schema(image_db)
    return image_schema


def delete_image(db: Session, id: str) -> ImageSchema:
    image_db: Image = db.query(Image).filter(
        Image.id == id).first()

    if image_db is None:
        raise ImageNotFoundInDatabaseError(
            f"Image with ID '{id}' was not found in database")

    db.delete(image_db)
    db.commit()

    file_path = os.path.join(
        server_settings.IMAGE_SETTINGS.FOLDER_PATH, image_db.filename)

    if not os.path.exists(file_path):
        raise ImageFileNotFoundError(
            f"Path to image with ID '{id}' was not found. Path: '{file_path}'")

    os.remove(file_path)

    image_schema = convert_from_model_to_schema(image_db)

    return image_schema


def delete_image_by_hostname(db: Session, hostname: str) -> ImageSchema:

    try:
        image_db: Image = db.query(Image).join(Device, Device.image_id == Image.id).filter(
            Device.hostname == hostname
        ).one()
    except NoResultFound as exc:
        raise ImageNotFoundInDatabaseError(
            f"Image was not found by hostname '{hostname}'. Either no device with hostname or no attached image to this device.")

    db.delete(image_db)
    db.commit()

    file_path = os.path.join(
        server_settings.IMAGE_SETTINGS.FOLDER_PATH, image_db.filename)

    if not os.path.exists(file_path):
        raise ImageFileNotFoundError(
            f"Path to image with ID '{image_db.id}' was not found. Path: '{file_path}'")

    os.remove(file_path)

    image_schema = convert_from_model_to_schema(image_db)

    return image_schema


def get_by_device_hostname(db: Session, device_hostname: str) -> ImageSchema:
    try:
        image_db: Image = db.query(Image).join(Device, Device.image_id == Image.id).filter(
            Device.hostname == device_hostname
        ).one()
    except NoResultFound as exc:
        raise ImageNotFoundInDatabaseError(
            f"Image was not found by hostname '{device_hostname}'. Either no device with hostname or no attached image to this device.")

    image_schema = convert_from_model_to_schema(image_db)

    return image_schema


async def save_file(upload_folder: str, file: UploadFile, image_type: ImageType, image_version: str, device_hostname: str, commit: str = None) -> tuple[str, Path]:
    file_extension = os.path.splitext(file.filename)[1]

    if not file_extension:
        raise EmptyFileExtensionError("Extension of file is empty.")

    if file_extension not in server_settings.IMAGE_SETTINGS.VALID_EXTS:
        raise InvalidFileExtensionError(
            f"Extension '{file_extension}' is not in the list of available extensions: {str(server_settings.IMAGE_SETTINGS.VALID_EXTS)}")

    filename = f"{device_hostname}-{image_type}-{image_version}-{commit}{file_extension}"
    filepath: Path = os.path.join(upload_folder, filename)

    with open(filepath, "wb") as target_file:
        shutil.copyfileobj(file.file, target_file)

    return filename, filepath


async def save_image(db: Session, file: UploadFile, image_type: ImageType, image_version: str, device_hostname: str, commit: str = None) -> ImageSchema:
    """
    Saves the uploaded image file to the specified folder and creates a database entry.
    """
    upload_folder = "/images"
    Path(upload_folder).mkdir(parents=True,
                              exist_ok=True)

    try:
        filename, filepath = await save_file(upload_folder, file, image_type, image_version, device_hostname, commit)

        image_schema = ImageSchema(
            id=str(uuid.uuid4()),
            type=image_type,
            version=image_version,
            commit=commit,
            filename=filename
        )
        # add image to db
        created_image_schema = create_image(db, image_schema)

        if not device_hostname:
            raise UnspecifiedDeviceHostnameError(
                "Device hostname must be specified.")

        # find device for image
        device = db.query(Device).filter(
            Device.hostname == device_hostname).first()

        if device is None:
            os.remove(filepath)
            raise DeviceNotFoundError(
                f"Device with hostname {device_hostname} not found")

        created_image_db = db.query(Image).filter(
            Image.id == created_image_schema.id).first()

        if device.image:
            delete_image(db, device.image.id)

        device.image = created_image_db
        db.commit()

        return created_image_schema
    except Exception as exc:
        try:
            os.remove(filepath)
        finally:
            raise exc
    finally:
        await file.close()
