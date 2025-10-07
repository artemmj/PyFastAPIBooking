from sqlalchemy import RowMapping, insert
from sqlalchemy.exc import SQLAlchemyError

from app.database.config import async_session_maker
from app.database.models import Hotel
from app.dao.base import BaseDAO
from app.logger import logger


class HotelsDAO(BaseDAO):
    model = Hotel

    @classmethod
    async def add(cls, name: str, address: str, image_id: int) -> (RowMapping | None):
        try:
            async with async_session_maker() as session:
                add_hotel = (
                    insert(Hotel)
                    .values(name=name, address=address, image_id=image_id)
                    .returning(Hotel.__table__.c)
                )
                new_hotel = await session.execute(add_hotel)
                await session.commit()
                return new_hotel.mappings().one()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, (SQLAlchemyError, Exception)):
                msg = "HotelsDAO.add() Exc: Cannot add hotel"
            logger.error(msg, exc_info=True)
