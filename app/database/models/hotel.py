from sqlalchemy.orm import Mapped, relationship

from app.database.config import Base, int_pk


class Hotel(Base):
    id: Mapped[int_pk]
    name: Mapped[str]
    address: Mapped[str]
    image_id: Mapped[int]

    rooms: Mapped[list["Room"]] = relationship(back_populates="hotel")

    def __str__(self) -> str:
        return f"Hotel #{self.id} ({self.name})"
