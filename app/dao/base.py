from sqlalchemy import insert, select
from sqlalchemy.engine.row import RowMapping

from app.database.config import async_session_maker


class BaseDAO:
    """DAO (Data Access Objects) - объекты, предоставляющие абстрактный интерфейс для работы с БД."""
    model = None

    @classmethod
    async def find_one_or_none(cls, **filter_by) -> RowMapping | None:
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            res = await session.execute(query)
            return res.mappings().one_or_none()

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            res = await session.execute(query)
            return res.mappings().all()

    @classmethod
    async def add(cls, **data) -> None:
        async with async_session_maker() as session:
            stmt = insert(cls.model).values(**data)
            new_object = await session.execute(stmt)
            await session.commit()
            # return new_object.scalar_one()
