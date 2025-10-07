from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy.engine.row import RowMapping

from app.exceptions import IncorrectEmailOrPasswordException
from app.dao.users import UsersDAO
from app.settings import settings

_pwd_context = CryptContext(schemes=["bcrypt", "pbkdf2_sha256"], default="pbkdf2_sha256", deprecated="auto")


def get_password_hash(password: str) -> str:
    """Получает пароль, делает из него хеш и возвращает его."""
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashes_password: str) -> bool:
    """Получает пароль и хеш из БД, возвращает результат их сравнения."""
    return _pwd_context.verify(plain_password, hashes_password)


def create_access_token(data: dict) -> str:
    """Создание JWT-токена. Истекает через 'access_token_expires'."""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    expire = datetime.utcnow() + access_token_expires
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        settings.ALGORITHM,
    )
    return encoded_jwt


async def authenticate_user(email: EmailStr, password: str) -> RowMapping:
    """Если логин/пароль верны, возвращает пользователя."""
    user: RowMapping | None = await UsersDAO.find_one_or_none(email=email)
    if not user:
        raise IncorrectEmailOrPasswordException
    if not verify_password(password, user.hashed_password):
        raise IncorrectEmailOrPasswordException
    return user
