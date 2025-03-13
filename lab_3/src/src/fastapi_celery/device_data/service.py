from typing import List

from sqlalchemy import and_, update
from sqlalchemy.orm import Session

from ..device_pin_control.model import BolidPin
from ..enums import (DeviceConnectionStatus, DeviceReservationStatus,
                     DeviceTestStage, DeviceType)
from ..exceptions import DeviceNotFoundError, BolidPinNotFoundError
from .model import Device
from .schemas import DeviceCreateSchema, DeviceSchema, DeviceUpdateSchema


def get_devices(
    db: Session,
    device_types: list,
    connection_status: str,
    test_stage: str,
    type_group: str,
) -> List[DeviceSchema]:
    filters = []

    if device_types is not None:
        filters.append(Device.type.in_(device_types))

    if connection_status is not None:
        filters.append(Device.connection_status == connection_status)

    if test_stage is not None:
        filters.append(Device.test_stage == test_stage)

    if type_group is not None:
        filters.append(Device.device_group == type_group)

    if filters:
        devices: List[Device] = db.query(Device).filter(and_(*filters)).all()
    else:
        devices: List[Device] = db.query(Device).all()

    devices_schemas: List[DeviceSchema] = [
        DeviceSchema.model_validate(device_db) for device_db in devices]
    return devices_schemas


def get_device(db: Session, hostname: str) -> DeviceSchema:
    device_db: Device = db.query(Device).filter(
        Device.hostname == hostname).first()

    if device_db is None:
        raise DeviceNotFoundError(f"Device with hostname {hostname} not found")

    device_schema: DeviceSchema = DeviceSchema.model_validate(device_db)
    return device_schema


def get_available_devices_by_types(db: Session, device_types: List[DeviceType]) -> List[DeviceSchema]:
    available_devices: List[Device] = db.query(Device).filter(
        and_(Device.type in device_types, Device.reservation_id is None)).all()

    devices_schemas: List[DeviceSchema] = [
        DeviceSchema.model_validate(device_db) for device_db in available_devices]

    return devices_schemas


def create_device(db: Session, device: DeviceCreateSchema) -> DeviceSchema:
    output_boot_pin: BolidPin = db.query(BolidPin).filter(
        and_(
            BolidPin.bolid_name == device.output_boot.bolid_name,
            BolidPin.number == device.output_boot.number
        )
    ).first()

    if output_boot_pin is None:
        raise BolidPinNotFoundError(f"Output boot pin not found with name: {device.output_boot.bolid_name} and number: {device.output_boot.number}")
    
    output_power_pin: BolidPin = db.query(BolidPin).filter(
        and_(
            BolidPin.bolid_name == device.output_power.bolid_name,
            BolidPin.number == device.output_power.number
        )
    ).first()

    if output_power_pin is None:
        raise BolidPinNotFoundError(f"Output power pin not found with name: {device.output_power.bolid_name} and number: {device.output_power.number}")
    
    db_device = Device(
        hostname=device.hostname,
        type=device.type,
        mac=device.mac,
        ip=device.ip,
        https_port=device.https_port,
        ws_port=device.ws_port,
        rs232_port=device.rs232_port,
        output_boot_id=output_boot_pin.id,
        output_power_id=output_power_pin.id,
        connection_status=DeviceConnectionStatus.UNAVAILABLE,
        test_stage=DeviceTestStage.NONE,
        device_group=device.type_group,
        reservation_status=DeviceReservationStatus.AVAILABLE
    )

    db_device.output_power=output_power_pin
    db_device.output_boot=output_boot_pin

    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    device_schema = DeviceSchema.model_validate(db_device)
    return device_schema


def delete_device(db: Session, hostname: str) -> DeviceSchema:
    device_db: Device = db.query(Device).filter(
        Device.hostname == hostname).first()

    if device_db is None:
        raise DeviceNotFoundError(f"Device with hostname {hostname} not found")

    db.delete(device_db)
    db.commit()

    device_schema = DeviceSchema.model_validate(device_db)
    return device_schema


def update_test_stage(db: Session, hostname: str, test_stage: DeviceTestStage) -> DeviceSchema:
    device_db: Device = db.query(Device).filter(
        Device.hostname == hostname).first()

    if device_db is None:
        raise DeviceNotFoundError(f"Device with hostname {hostname} not found")

    device_db.test_stage = test_stage

    db.commit()
    db.refresh(device_db)

    return DeviceSchema.model_validate(device_db)


def update_device(db: Session, hostname: str, device_update_schema: DeviceUpdateSchema) -> DeviceSchema:
    update_data = device_update_schema.model_dump(exclude_unset=True)

    if not update_data:
        return get_device(db, hostname)

    update_stmt = (
        update(Device)
        .where(Device.hostname == hostname)
        .values(**update_data)
    )

    result = db.execute(update_stmt)

    if result.rowcount == 0:
        raise DeviceNotFoundError(f"Device with hostname {hostname} not found")

    db.commit()

    device_db = db.query(Device).filter(Device.hostname == hostname).first()
    db.refresh(device_db)

    return DeviceSchema.model_validate(device_db)


def clear_device_data_table(db: Session):
    db.query(Device).delete()
    db.commit()
