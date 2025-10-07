from sqlalchemy.orm import Mapped, relationship

from app.database.config import Base, int_pk, str_255


class User(Base):
    id: Mapped[int_pk]
    email: Mapped[str]
    hashed_password: Mapped[str_255]

    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")

    def __str__(self) -> str:
        return f"User #{self.id} ({self.email})"
