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
def get_arquivo(id: UUID):
    path = services.file.get(id)

    return RedirectResponse(str(path))


@router.post("/arquivo")
async def upload_arquivo(file: UploadFile):
    id = await services.file.upload(file)

    return {"message": "O upload foi bem sucedido", "id": str(id)}
