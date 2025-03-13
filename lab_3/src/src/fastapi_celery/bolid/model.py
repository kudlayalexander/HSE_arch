from typing import List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..dependencies import Base


class Bolid(Base):
    __tablename__ = 'bolids'

    name: Mapped[str] = mapped_column(
        String, primary_key=True, unique=True, nullable=False)
    port: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    pin_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    baudrate: Mapped[int] = mapped_column(Integer, nullable=False)
    parity: Mapped[str] = mapped_column(String, nullable=False)
    stopbits: Mapped[int] = mapped_column(Integer, nullable=False)
    bytesize: Mapped[int] = mapped_column(Integer, nullable=False)

    bolid_pins: Mapped[List["BolidPin"]] = relationship(
        "BolidPin",
        back_populates="bolid",
        lazy="joined"
    )
