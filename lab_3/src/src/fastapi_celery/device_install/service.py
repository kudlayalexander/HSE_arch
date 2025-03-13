from sqlalchemy.orm import Session
from ..enums import PinType

def set_device_pin_status(db: Session, hostname: str, pin_type: PinType, pin_status: bool):
    pass

def stop_device_autoload():
    pass