import uuid
from typing import List

from sqlalchemy.orm import Session

from ..bolid.model import Bolid
from ..bolid.service import get_bolid_by_name
from ..exceptions import BolidPinNotFoundError, BolidPinLimitExceededError, BolidNotFoundError
from .model import BolidPin
from .schemas import BolidPinCreateSchema, BolidPinSchema, BolidPinCreateRangeSchema


def get_bolid_pins(db: Session) -> List[BolidPinSchema]:
    bolid_pins: List[BolidPin] = db.query(BolidPin).all()

    bolid_pins_schemas: List[BolidPinSchema] = [
        BolidPinSchema.model_validate(bolid_pin_db) for bolid_pin_db in bolid_pins]

    return bolid_pins_schemas


def get_bolid_pin_by_id(db: Session, bolid_pin_id: str) -> BolidPinSchema:
    bolid_pin_db: BolidPin = db.query(BolidPin).filter(
        BolidPin.id == bolid_pin_id).first()

    if bolid_pin_db is None:
        raise BolidPinNotFoundError(
            f"Bolid pin with ID {bolid_pin_id} not found")

    bolid_schema = BolidPinSchema.model_validate(bolid_pin_db)

    return bolid_schema


def create_bolid_pin(db: Session, bolid_create_schema: BolidPinCreateSchema) -> BolidPinSchema:
    bolid_name = bolid_create_schema.bolid_name
    requested_pin_amount = 1
    bolid_db: Bolid = get_bolid_by_name(
        db, bolid_name=bolid_name)

    if bolid_db.pin_capacity < len(bolid_db.bolid_pins) + requested_pin_amount:
        raise BolidPinLimitExceededError(
            f"Pin limit on bolid {bolid_name} exceeded. Max pins: {bolid_db.pin_capacity}. Busy pins: {len(bolid_db.bolid_pins)}. Requested amount: {requested_pin_amount}")

    bolid_pin_db = BolidPin(
        id=str(uuid.uuid4()),
        number=bolid_create_schema.number,
        bolid_name=bolid_create_schema.bolid_name
    )
    db.add(bolid_pin_db)

    # Append new bolid pin to bolid pin list
    bolid_db: Bolid = db.query(Bolid).filter(
        Bolid.name == bolid_name).first()

    if bolid_db is None:
        raise BolidNotFoundError(
            f"Bolid with name {bolid_name} not found")
    bolid_db.bolid_pins.append(bolid_pin_db)

    db.commit()
    db.refresh(bolid_pin_db)

    bolid_pin_schema = BolidPinSchema.model_validate(bolid_pin_db)
    return bolid_pin_schema


def create_bolid_pins_range(db: Session, pin_create_range_schema: BolidPinCreateRangeSchema) -> List[BolidPinSchema]:
    new_pins: List[BolidPin] = []

    bolid_name = pin_create_range_schema.bolid_name
    requested_pin_amount = pin_create_range_schema.number_to - \
        pin_create_range_schema.number_to
    
    bolid_db: Bolid = db.query(Bolid).filter(
        Bolid.name == bolid_name).first()

    if bolid_db is None:
        raise BolidNotFoundError(
            f"Bolid with name {bolid_name} not found")

    if bolid_db.pin_capacity < len(bolid_db.bolid_pins) + requested_pin_amount:
        raise BolidPinLimitExceededError(
            f"Pin limit on bolid {bolid_name} exceeded. Max pins: {bolid_db.pin_capacity}. Busy pins: {len(bolid_db.bolid_pins)}. Requested amount: {requested_pin_amount}")

    number_from = pin_create_range_schema.number_from
    number_to = pin_create_range_schema.number_to + 1
    for output_number in range(number_from, number_to):
        bolid_pin_db = BolidPin(
            id=str(uuid.uuid4()),
            number=output_number,
            bolid_name=pin_create_range_schema.bolid_name
        )
        db.add(bolid_pin_db)
        bolid_db.bolid_pins.append(bolid_pin_db)

    db.commit()
    db.refresh(bolid_pin_db)

    new_pins_schemas: List[BolidPinSchema] = [
        BolidPinSchema.model_validate(bolid_pin) for bolid_pin in new_pins]

    return new_pins_schemas


def delete_bolid_pin(db: Session, bolid_pin_id: str) -> BolidPinSchema:
    bolid_pin_db: BolidPin = db.query(BolidPin).filter(
        BolidPin.id == bolid_pin_id).first()

    if bolid_pin_db is None:
        raise BolidPinNotFoundError(
            f"Bolid pin with ID '{bolid_pin_id}' was not found in database")

    db.delete(bolid_pin_db)
    db.commit()

    bolid_pin_schema = BolidPinSchema.model_validate(bolid_pin_db)
    return bolid_pin_schema


def clear_bolid_pin_table(db: Session):
    db.query(BolidPin).delete()
    db.commit()
