from fastapi import APIRouter, Depends, Response

from app.dao.users import UsersDAO
from app.database.models import User
from app.exceptions import UserAlreadyExistsException
from app.api.users.auth import authenticate_user, create_access_token, get_password_hash
from app.api.users.dependencies import get_current_user
from app.api.users.schemas import UserAuthSchema, UserMeSchema

router = APIRouter(prefix="/auth", tags=["Аутентификация, пользователи"])


@router.post("/register")
async def register_user(user_data: UserAuthSchema) -> None:
    """Создается новый user, если такого еще нет."""
    existing_user = await UsersDAO.find_one_or_none(email=user_data.email)
    if existing_user:
        raise UserAlreadyExistsException
    hashed_password = get_password_hash(user_data.password)
    await UsersDAO.add(email=user_data.email, hashed_password=hashed_password)


@router.post("/login")
async def login_user(responce: Response, user_data: UserAuthSchema) -> dict[str, str]:
    """Если логин/пароль верны, то с помощью HTTP-ответа создается кука с JWT-токеном."""
    user = await authenticate_user(email=user_data.email, password=user_data.password)
    access_token = create_access_token({"sub": str(user.id)})
    responce.set_cookie("booking_access_token", access_token, httponly=True)
    return {"access_token": access_token}


@router.post("/logout")
async def logout_user(responce: Response) -> None:
    """С помощью HTTP-ответа удаляется кука с JWT-токеном."""
    responce.delete_cookie("booking_access_token")


@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)) -> UserMeSchema:
    """Возвращает id и email аутентифицированного пользователя, либо Exception."""
    return UserMeSchema(id=current_user.id, email=current_user.email)
