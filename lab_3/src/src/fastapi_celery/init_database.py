import logging
from typing import List

from sqlalchemy.orm import Session

from .bolid.schemas import BolidSchema
from .bolid.service import (clear_bolid_table, create_bolid, delete_bolid,
                            get_bolid_by_name, get_bolids)
from .config import server_settings
from .database import get_db
from .device_data.model import Device
from .device_data.schemas import DeviceSchema
from .device_data.service import (clear_device_data_table, create_device,
                                  delete_device, get_device)
from .device_pin_control.schemas import (BolidPinCreateRangeSchema,
                                         BolidPinSchema)
from .device_pin_control.service import (clear_bolid_pin_table,
                                         create_bolid_pins_range)
from .exceptions import BolidNotFoundError, DeviceNotFoundError

logger = logging.getLogger("uvicorn.error")

def clear_tables():
    db_gen = get_db()
    db: Session = next(db_gen)
    
    clear_device_data_table(db)
    clear_bolid_pin_table(db)
    clear_bolid_table(db)


def init_bolids():
    db_gen = get_db()
    db: Session = next(db_gen)

    for bolid_schema in server_settings.BOLIDS:
        logger.info(f"Creating bolid {bolid_schema.name}")
        create_bolid(db, bolid_schema)

    init_bolid_pins(db)


def init_bolid_pins(db: Session):
    for bolid_schema in server_settings.BOLIDS:
        create_pins_schema = BolidPinCreateRangeSchema(
            number_from=1,
            number_to=bolid_schema.pin_capacity,
            bolid_name=bolid_schema.name
        )
        logger.info(f"Creating pins for bolid: {bolid_schema.name}")
        create_bolid_pins_range(db, create_pins_schema)


def init_devices():
    db_gen = get_db()
    db: Session = next(db_gen)

    for device_schema in server_settings.DEVICES:
        logger.info(f"Creating device {device_schema.hostname}")
        create_device(db, device_schema)
