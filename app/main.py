from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from app.api.users.router import router as router_users
from app.api.hotels.router import router as router_hotels
from app.api.rooms.router import router as router_rooms
from app.api.bookings.router import router as router_bookings
from app.database.config import get_async_db
from app.database.models.hotel import Hotel

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db = Depends(get_async_db)):
    hotels = await db.scalars(select(Hotel))
    hotels = hotels.all()
    return templates.TemplateResponse("index.html", {'request': request, "hotels": hotels})


@app.get("/booking.html", response_class=HTMLResponse)
async def index(request: Request, db = Depends(get_async_db)):
    return templates.TemplateResponse("booking.html", {'request': request})


app.include_router(router_users)
app.include_router(router_hotels)
app.include_router(router_rooms)
app.include_router(router_bookings)
