from fastapi import FastAPI

from app.settings import settings
from app.api.users.router import router as router_users
from app.api.hotels.router import router as router_hotels
from app.api.rooms.router import router as router_rooms

app = FastAPI()
app.include_router(router_users)
app.include_router(router_hotels)
app.include_router(router_rooms)
