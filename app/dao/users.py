from app.database.models import User
from app.dao.base import BaseDAO


class UsersDAO(BaseDAO):
    model = User
