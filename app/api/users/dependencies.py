from fastapi import Depends, Request
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy import RowMapping

from app.dao.users import UsersDAO
from app.exceptions import (
    IncorrectTokenFormatException,
    TokenAbsentException,
    TokenExpiredException,
    UserIsNotPresentException,
)
from app.settings import settings


def _get_token(request: Request) -> str:
    """
    Функция из HTTP-запроса извлекает куку с JWT-токеном.
    """
    token = request.cookies.get("booking_access_token")
    if not token:
        raise TokenAbsentException
    return token


async def get_current_user(token: str = Depends(_get_token)) -> RowMapping:
    """
    Получает JWT-токен. Декодирует токен в полезную нагрузку (dict) и проверяет ее.
    Если в ней есть subject (id), ищет его в БД. Если такой есть, возвращает юзера.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
    except ExpiredSignatureError:
        raise TokenExpiredException
    except JWTError:
        raise IncorrectTokenFormatException

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException

    user = await UsersDAO.find_one_or_none(id=int(user_id))
    if not user:
        raise UserIsNotPresentException

    return user
