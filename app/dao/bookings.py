from datetime import date

from sqlalchemy import RowMapping, and_, delete, func, insert, or_, select
from sqlalchemy.exc import SQLAlchemyError

from app.dao.base import BaseDAO
from app.database.config import async_session_maker
from app.database.models.booking import Booking
from app.database.models.room import Room
from app.exceptions import RoomFullyBooked
from app.logger import logger



class BookingDAO(BaseDAO):
    model = Booking

    @classmethod
    async def add(
        cls,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date,
    ) -> (RowMapping | None):
        """
        WITH booked_rooms AS (
            SELECT * FROM bookings
            WHERE room_id = 1 AND
                (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
                (date_from <= '2023-05-15' AND date_to > '2023-05-15')
        )
        SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms
        LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
        WHERE rooms.id = 1
        GROUP BY rooms.quantity, booked_rooms.room_id
        """
        try:
            async with async_session_maker() as session:
                existing_booking = select(Booking).where(
                    and_(
                        Booking.room_id == room_id,
                        Booking.user_id == user_id,
                        date_from <= Booking.date_to,
                    ),
                )
                result = await session.execute(existing_booking)
                existing_booking: Booking | None = result.scalar_one_or_none()
                if existing_booking is not None:
                    raise RoomFullyBooked

                booked_rooms = (
                    select(Booking)
                    .where(
                        and_(
                            Booking.room_id == room_id,
                            or_(
                                and_(
                                    Booking.date_from >= date_from,
                                    Booking.date_from <= date_to,
                                ),
                                and_(
                                    Booking.date_from <= date_from,
                                    Booking.date_to > date_from,
                                ),
                            ),
                        ),
                    )
                    .cte("booked_rooms")
                )

                """
                SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms
                LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
                WHERE rooms.id = 1
                GROUP BY rooms.quantity, booked_rooms.room_id
                """

                get_rooms_left = (
                    select(
                        (
                            Room.quantity
                            - func.count(booked_rooms.c.room_id).filter(
                                booked_rooms.c.room_id.is_not(None),
                            )
                        ).label("rooms_left"),
                    )
                    .select_from(Room)
                    .join(
                        booked_rooms,
                        booked_rooms.c.room_id == Room.id,
                        isouter=True,
                    )
                    .where(Room.id == room_id)
                    .group_by(Room.quantity, booked_rooms.c.room_id)
                )
                rooms_left = await session.execute(get_rooms_left)
                rooms_left: int = rooms_left.scalar()

                if rooms_left > 0:
                    get_price = select(Room.price).filter_by(id=room_id)
                    price = await session.execute(get_price)
                    price: int = price.scalar()
                    add_booking = (
                        insert(Booking)
                        .values(
                            room_id=room_id,
                            user_id=user_id,
                            date_from=date_from,
                            date_to=date_to,
                            price=price,
                        )
                        .returning(
                            Booking.id,
                            Booking.user_id,
                            Booking.room_id,
                            Booking.date_from,
                            Booking.date_to,
                        )
                    )

                    new_booking = await session.execute(add_booking)
                    await session.commit()
                    return new_booking.mappings().one()
                else:
                    raise RoomFullyBooked
        except RoomFullyBooked:
            raise RoomFullyBooked
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot add booking"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot add booking"
            extra = {
                "user_id": user_id,
                "room_id": room_id,
                "date_from": date_from,
                "date_to": date_to,
            }
            logger.error(msg, extra=extra, exc_info=True)

    @classmethod
    async def delete(cls, booking_id: int, user_id: int) -> (bool | None):
        try:
            async with async_session_maker() as session:
                delete_booking = (
                    delete(Booking)
                    .where(Booking.id == booking_id)
                    .where(Booking.user_id == user_id)
                )

                result = await session.execute(delete_booking)
                await session.commit()
                return result.rowcount > 0
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot delete booking"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot delete booking"
            extra = {
                "booking_id": booking_id,
                "user_id": user_id,
            }
            logger.error(msg, extra=extra, exc_info=True)
