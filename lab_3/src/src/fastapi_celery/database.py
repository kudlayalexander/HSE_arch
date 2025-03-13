from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .bolid.model import Bolid
from .config import env_settings
from .dependencies import Base
from .device_data.model import Device
from .device_pin_control.model import BolidPin
from .device_reserve.model import Reservation
from .images.model import Image

engine = create_engine(str(env_settings.SQLALCHEMY_DATABASE_URI))
Base.metadata.create_all(engine, checkfirst=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

