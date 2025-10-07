from fastapi import APIRouter, Depends
from pydantic import TypeAdapter

from app.api.users.dependencies import get_current_user
from app.dao.hotels import HotelsDAO
from app.database.models import User
from app.exceptions import HotelCannotBeCreated

from .schemas import HotelSchema, NewHotelSchema

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("", summary='Получить все отели')
async def get_all_hotels() -> list[HotelSchema]:
    """Получить все отели."""
    return await HotelsDAO.find_all()


@router.post("", summary='Добавить новый отель (TODO только для админа)')
async def add_new_hotel(hotel: NewHotelSchema, user: User = Depends(get_current_user)) -> NewHotelSchema:
    """Добавить новый отель (TODO только для админа)."""
    hotel = await HotelsDAO.add(hotel.name, hotel.address, hotel.image_id)
    if not hotel:
        raise HotelCannotBeCreated
    return TypeAdapter(NewHotelSchema).validate_python(hotel).model_dump()
