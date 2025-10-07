from fastapi import APIRouter, Depends
from pydantic import TypeAdapter

from app.dao.bookings import BookingDAO
from app.database.models.user import User
from app.exceptions import BookingNotExist, RoomCannotBeBooked
# from tasks import send_booking_confirmation_email
from app.api.users.dependencies import get_current_user

from .schemas import SBookings, SNewBooking

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)


@router.get("/get", summary='Получить брони')
async def get_bookings(user: User = Depends(get_current_user)) -> list[SBookings]:
    return await BookingDAO.find_all(user_id=user.id)


@router.post("/add", summary='Добавить бронь')
async def add_booking(booking: SNewBooking, user: User = Depends(get_current_user)) -> SNewBooking:
    booking = await BookingDAO.add(
        user.id,
        booking.room_id,
        booking.date_from,
        booking.date_to,
    )

    if not booking:
        raise RoomCannotBeBooked

    booking = TypeAdapter(SNewBooking).validate_python(booking).model_dump()
    # send_booking_confirmation_email.delay(booking, user.email)
    return booking


@router.delete("/{booking_id}", summary='Удалить бронь')
async def cancel_booking(booking_id: int, user: User = Depends(get_current_user)) -> dict[str, str]:
    success = await BookingDAO.delete(booking_id, user.id)

    if not success:
        raise BookingNotExist

    return {"message": "Бронь отменена"}
