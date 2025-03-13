import uuid
from datetime import datetime

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref
from sqlalchemy.types import DateTime
from ..enums import DeviceReservationStatus, DeviceConnectionStatus, DeviceTestStage, DeviceType, DeviceTypeGroup, StandUser
from ..dependencies import Base


class Device(Base):
    __tablename__ = 'devices'

    hostname: Mapped[str] = mapped_column(
        String(32), primary_key=True, unique=True, nullable=False)
    mac: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    ip: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    type: Mapped[DeviceType] = mapped_column(nullable=False)
    https_port: Mapped[int] = mapped_column(Integer, nullable=False)
    ws_port: Mapped[int] = mapped_column(Integer, nullable=False)
    rs232_port: Mapped[str] = mapped_column(String(32), nullable=False)
    connection_status: Mapped[DeviceConnectionStatus] = mapped_column(
        nullable=True)
    reservation_status: Mapped[DeviceReservationStatus] = mapped_column(
        String(32), nullable=True)
    test_stage: Mapped[DeviceTestStage] = mapped_column(nullable=True)
    device_group: Mapped[DeviceTypeGroup] = mapped_column(nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    output_power_id: Mapped[str | None] = mapped_column(
        ForeignKey('bolid_pins.id'), nullable=True)
    output_power: Mapped["BolidPin"] = relationship(
        "BolidPin",
        backref=backref("output_power", uselist=False),
        cascade="all, delete-orphan",
        single_parent=True,
        lazy="joined",
        foreign_keys=[output_power_id]
    )

    output_boot_id: Mapped[str | None] = mapped_column(
        ForeignKey('bolid_pins.id'), nullable=True)
    output_boot: Mapped["BolidPin"] = relationship(
        "BolidPin",
        backref=backref("output_boot", uselist=False),
        cascade="all, delete-orphan",
        single_parent=True,
        lazy="joined",
        foreign_keys=[output_boot_id]
    )

    image_id: Mapped[str | None] = mapped_column(ForeignKey('images.id'))
    image: Mapped["Image"] = relationship(
        "Image",
        back_populates="device",
        uselist=False,
        lazy="joined",
        cascade="all, delete-orphan",
        single_parent=True
    )

    reservation_id: Mapped[str | None] = mapped_column(
        ForeignKey('reservations.id'), nullable=True)
    reservation: Mapped["Reservation"] = relationship(
        "Reservation",
        back_populates="devices",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True,
        lazy="joined"
    )
