from fastapi import FastAPI

from app.settings import settings

app = FastAPI()


@app.get("/ping")
def pong():
    return {"ping": "pong!", "settings": settings}
