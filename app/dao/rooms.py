from sqlalchemy import RowMapping, and_, func, insert, select
from sqlalchemy.exc import SQLAlchemyError

from app.database.config import async_session_maker
from app.database.models import Room
from app.dao.base import BaseDAO
from app.logger import logger


class RoomsDAO(BaseDAO):
    model = Room

    @classmethod
    async def find_all(cls, options=None):
        async with async_session_maker() as session:
            query = select(cls.model)
            if options:
                conditions = []
                for option in options:
                    # Используем func.jsonb_build_array для создания jsonb-массива
                    jsonb_option = func.jsonb_build_array(option)
                    conditions.append(cls.model.options.op('@>')(jsonb_option))
                query = query.where(and_(*conditions))
            result = await session.scalars(query)
            rooms = result.all()
            return rooms

    @classmethod
    async def add(
        cls, hotel_id: int, name: str, description: str, price: int,
        options: list[str], quantity: int, image_id: int,
    ) -> (RowMapping | None):
        try:
            async with async_session_maker() as session:
                add_room = (
                    insert(cls.model)
                    .values(
                        hotel_id=hotel_id,
                        name=name,
                        description=description,
                        price=price,
                        options=options,
                        quantity=quantity,
                        image_id=image_id,
                    )
                    .returning(cls.model.__table__.c)
                )
                new_room = await session.execute(add_room)
                await session.commit()
                return new_room.mappings().one()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, (SQLAlchemyError, Exception)):
                msg = "RoomsDAO.add() Exc: Cannot add room"
            logger.error(msg, exc_info=True)

    @classmethod
    async def get_options(cls):
        try:
            async with async_session_maker() as session:
                options = select(cls.model.options)
                opts = await session.execute(options)
                return opts.mappings().all()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, (SQLAlchemyError, Exception)):
                msg = "RoomsDAO.get_options() Exc: Cannot get options"
            logger.error(msg, exc_info=True)
