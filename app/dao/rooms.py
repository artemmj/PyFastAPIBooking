from sqlalchemy import RowMapping, insert
from sqlalchemy.exc import SQLAlchemyError

from app.database.config import async_session_maker
from app.database.models import Room
from app.dao.base import BaseDAO
from app.logger import logger


class RoomsDAO(BaseDAO):
    model = Room

    @classmethod
    async def add(
        cls,
        hotel_id: int,
        name: str,
        description: str,
        price: int,
        options: list[str],
        quantity: int,
        image_id: int,
    ) -> (RowMapping | None):
        try:
            async with async_session_maker() as session:
                add_room = (
                    insert(Room)
                    .values(
                        hotel_id=hotel_id,
                        name=name,
                        description=description,
                        price=price,
                        options=options,
                        quantity=quantity,
                        image_id=image_id,
                    )
                    .returning(Room.__table__.c)
                )
                new_room = await session.execute(add_room)
                await session.commit()
                return new_room.mappings().one()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, (SQLAlchemyError, Exception)):
                msg = "RoomsDAO.add() Exc: Cannot add room"
            logger.error(msg, exc_info=True)
