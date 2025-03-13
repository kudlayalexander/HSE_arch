from typing import List
from sqlalchemy.orm import Session
from .schemas import BolidSchema, BolidCreateSchema
from .model import Bolid
from ..exceptions import BolidNotFoundError

import uuid


def get_bolids(db: Session) -> List[BolidSchema]:
    bolids: List[Bolid] = db.query(Bolid).all()

    bolids_schemas: List[BolidSchema] = [
        BolidSchema.model_validate(bolid_db) for bolid_db in bolids]

    return bolids_schemas


def get_bolid_by_name(db: Session, bolid_name: str) -> BolidSchema:
    bolid_db: Bolid = db.query(Bolid).filter(
        Bolid.name == bolid_name).first()

    if bolid_db is None:
        raise BolidNotFoundError(
            f"Bolid with name {bolid_name} not found")

    bolid_schema = BolidSchema.model_validate(bolid_db)

    return bolid_schema


def create_bolid(db: Session, bolid_create_schema: BolidCreateSchema) -> BolidSchema:
    bolid_db = Bolid(
        name=bolid_create_schema.name,
        port=bolid_create_schema.port,
        pin_capacity=bolid_create_schema.pin_capacity,
        baudrate=bolid_create_schema.baudrate,
        parity=bolid_create_schema.parity,
        stopbits=bolid_create_schema.stopbits,
        bytesize=bolid_create_schema.bytesize
    )

    db.add(bolid_db)
    db.commit()
    db.refresh(bolid_db)

    bolid_schema = BolidSchema.model_validate(bolid_db)
    return bolid_schema


def delete_bolid(db: Session, bolid_name: str) -> BolidSchema:
    bolid_db: Bolid = db.query(Bolid).filter(
        Bolid.name == bolid_name).first()

    if bolid_db is None:
        raise BolidNotFoundError(
            f"Bolid with name '{bolid_name}' was not found in database")

    db.delete(bolid_db)
    db.commit()

    bolid_schema = BolidSchema.model_validate(bolid_db)
    return bolid_schema


def clear_bolid_table(db: Session):
    db.query(Bolid).delete()
    db.commit()
