import uuid

from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..dependencies import Base
from ..enums import ImageType


class Image(Base):
    __tablename__ = 'images'

    id: Mapped[str] = mapped_column(
        primary_key=True, unique=True, nullable=False)
    type: Mapped[ImageType]
    version: Mapped[str]
    commit: Mapped[str] = mapped_column(nullable=True)
    filename: Mapped[str]

    device: Mapped["Device"] = relationship(
        "Device",
        back_populates="image",
        uselist=False,
        single_parent=True
    )
