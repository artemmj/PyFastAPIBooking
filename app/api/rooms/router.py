from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import TypeAdapter

from app.api.users.dependencies import get_current_user
from app.dao.rooms import RoomsDAO
from app.database.models.user import User
from app.exceptions import HotelCannotBeCreated
from .schemas import RoomSchema, NewRoomSchema

router = APIRouter(prefix="/rooms", tags=["Комнаты"])


@router.get("", summary='Получить все комнаты')
async def get_all_rooms(
    hotel_id: int | None = None,
    options: Optional[List[str]] = Query(None, alias="options", description="Фильтр по удобствам"),
) -> list[RoomSchema]:
    """Получить все комнаты."""
    return await RoomsDAO.find_all(options, hotel_id)


@router.post("", summary='Добавить новую комнату (TODO только для админа)')
async def add_new_room(room: NewRoomSchema, user: User = Depends(get_current_user)) -> NewRoomSchema:
    """Добавить новую комнату (TODO только для админа, рефакторинг)."""
    room = await RoomsDAO.add(
        room.hotel_id,
        room.name,
        room.description,
        room.price,
        room.options,
        room.quantity,
        room.image_id,
    )
    if not room:
        raise HotelCannotBeCreated
    return TypeAdapter(NewRoomSchema).validate_python(room).model_dump()


@router.get("/options", summary='Получить список доступных опций комнат для фильтрации')
async def get_room_options():
    """Получить список всех доступных опций, чтобы фильтровать по ним."""
    options = await RoomsDAO.get_options()
    opts_set = set()
    for room in options:
        for opt in room['options']:
            opts_set.add(opt)
    return opts_set
