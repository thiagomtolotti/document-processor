import logging
from uuid import UUID

from fastapi import UploadFile
from fastapi.routing import APIRouter
from fastapi.responses import RedirectResponse

from app import services

router = APIRouter()


@router.get("/")
def ping():
    return {"message": "Service is alive"}


@router.get("/arquivo/{id}")
def get_arquivo(id: UUID, chunk: int = 1):
    path = services.file.get(id, chunk)

    return RedirectResponse(str(path))


@router.post("/arquivo")
async def upload_arquivo(file: UploadFile):
    logging.info("RECEIVED FILE %s", file.filename)

    id = services.file.upload(file)

    return {"message": "O upload foi bem sucedido", "id": str(id)}
