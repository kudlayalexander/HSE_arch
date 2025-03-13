import uuid
from typing import Dict, List

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from ..device_data import service as device_data_service
from ..device_data.model import Device
from ..enums import DeviceReservationStatus, DeviceType
from ..exceptions import (DeviceNotFoundError, NotEnoughDevicesError,
                          ReservationNotFoundError)
from .convert_model_schema import convert_from_model_to_schema
from .model import Reservation
from .reservation_logic import is_enough_devices, select_devices_to_reserve
from .schemas import ReservationSchema, ReservationRequest


def get_reservations(db: Session) -> List[ReservationSchema]:
    reservations: List[Reservation] = db.query(Reservation).all()

    reservations_schemas = [convert_from_model_to_schema(
        reservation_db) for reservation_db in reservations]

    return reservations_schemas


def get_reservation_by_id(db: Session, reservation_id: str) -> ReservationSchema:
    reservation_db: Reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id).first()

    if reservation_db is None:
        raise ReservationNotFoundError(
            f"Reservation with ID {reservation_id} not found")

    reservation_schema = convert_from_model_to_schema(reservation_db)

    return reservation_schema


def get_reservation_by_device(db: Session, hostname: str) -> ReservationSchema:
    try:
        reservation_db: Reservation = db.query(Reservation).join(Device, Device.reservation_id == Reservation.id).filter(
            Device.hostname == hostname
        ).one()
    except NoResultFound as exc:
        raise ReservationNotFoundError(
            f"Reservation was not found by hostname '{hostname}'. Either no device with hostname or no attached reservation to this device.")

    reservation_schema = convert_from_model_to_schema(reservation_db)

    return reservation_schema


def delete_reservation_by_id(db: Session, reservation_id: int) -> None:
    """Deletes a reservation and releases the associated devices."""

    reservation: Reservation = db.query(Reservation).get(reservation_id)

    if reservation is None:
        raise ReservationNotFoundError(
            f"Reservation with id {reservation_id} not found")

    devices: List[Device] = reservation.devices

    try:
        for device in devices:
            device.reservation_status = DeviceReservationStatus.AVAILABLE
            device.reservation = None

        db.delete(reservation)
        db.commit()

        return convert_from_model_to_schema(reservation)

    except Exception as e:
        db.rollback()
        raise


def delete_reservation_by_device(db: Session, hostname: str) -> ReservationSchema:
    """Deletes the reservation associated with a specific device and releases that device."""

    device: Device = db.query(Device).filter(
        Device.hostname == hostname).first()

    if device is None:
        raise DeviceNotFoundError(f"Device with hostname {hostname} not found")

    if device.reservation is None:
        raise DeviceNotFoundError(
            f"Device with hostname {hostname} is not currently reserved")

    try:
        reservation: Reservation = device.reservation

        device.reservation_status = DeviceReservationStatus.AVAILABLE
        device.reservation = None

        db.commit()

        return convert_from_model_to_schema(reservation)

    except Exception as e:
        db.rollback()
        raise


def create_reservation(db: Session, reservation_request: ReservationRequest) -> ReservationSchema:
    """Selects devices for reservation, adds reservation to db if successfully found devices."""
    try:
        all_devices: List[Device] = db.query(Device).all()

        if not is_enough_devices(all_devices, reservation_request.requested_types):
            raise NotEnoughDevicesError(
                "Not enough devices to make this request (check request data and stand configuration)")

        available_devices = [
            device for device in all_devices if device.reservation_status == DeviceReservationStatus.AVAILABLE and device.reservation is None]

        reserved_devices: List[Device] = select_devices_to_reserve(
            available_devices, reservation_request.requested_types)

        reservation_db = Reservation(
            id=str(uuid.uuid4()),
            reserved_by=reservation_request.reserved_by
        )
        db.add(reservation_db)

        for device in reserved_devices:
            device.reservation_status = DeviceReservationStatus.RESERVED
            device.reservation = reservation_db

        db.commit()
        db.refresh(reservation_db)

        new_reservation_schema = convert_from_model_to_schema(reservation_db)
        return new_reservation_schema
    except Exception as e:
        db.rollback()
        raise
