from typing import List

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime

from ..dependencies import Base
from ..enums import StandUser


class Reservation(Base):
    __tablename__ = 'reservations'

    id: Mapped[str] = mapped_column(
        primary_key=True, unique=True, nullable=False)
    reserved_by: Mapped[StandUser | None] = mapped_column(
        String(32), nullable=True)
    time_start: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    time_end: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    devices: Mapped[List["Device"]] = relationship(
        back_populates="reservation",
        lazy="joined"
    )
