from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base, int_pk


class Room(Base):
    id: Mapped[int_pk]
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[int]
    options: Mapped[list[str]] = mapped_column(JSONB)
    quantity: Mapped[int]
    image_id: Mapped[int]

    hotel: Mapped["Hotel"] = relationship(back_populates="rooms")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="room")

    def __str__(self) -> str:
        return f"Room #{self.id} ({self.name})"
