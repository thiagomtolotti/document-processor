from uuid import UUID

from fastapi import UploadFile
from fastapi.routing import APIRouter
from fastapi.responses import Response

from app import services

router = APIRouter()


@router.get("/")
def ping():
    return {"message": "Service is alive"}


@router.get("/arquivo/{id}")
def get_arquivo(id: UUID, response: Response):
    file = services.file.get(id)

    if file is None:
        response.status_code = 404
        return {"message": "Arquivo não encontrado"}


@router.post("/arquivo")
async def upload_arquivo(file: UploadFile, response: Response):
    id = await services.file.upload(file)

    return {"message": "O upload foi bem sucedido", "id": str(id)}
