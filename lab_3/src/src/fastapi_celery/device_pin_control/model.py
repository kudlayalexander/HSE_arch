from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..dependencies import Base


class BolidPin(Base):
    __tablename__ = 'bolid_pins'

    id: Mapped[str] = mapped_column(
        String, primary_key=True, unique=True, nullable=False)
    number: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)

    bolid_name: Mapped[str | None] = mapped_column(ForeignKey('bolids.name'))
    bolid: Mapped["Bolid"] = relationship(
        "Bolid",
        back_populates="bolid_pins",
        uselist=False,
        lazy="joined",
        cascade="all, delete-orphan",
        single_parent=True
    )

    # device: Mapped["Device"] = relationship(
    #     "Device",
    #     back_populates="bolid_pin",
    #     uselist=False,
    #     lazy="joined"
    # )