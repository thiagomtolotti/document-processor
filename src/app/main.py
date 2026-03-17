from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.main import api_router
from app.constants import STATIC_PATH

app = FastAPI()


STATIC_PATH.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

app.include_router(api_router)
