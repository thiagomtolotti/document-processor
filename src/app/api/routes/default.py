from uuid import UUID

from fastapi.routing import APIRouter
from fastapi.responses import FileResponse

from app import services

router = APIRouter()


@router.get("/")
def ping():
    return {"message": "Service is alive"}


@router.get("/arquivo/{id}")
def get_arquivo(id: UUID, response: FileResponse):
    file = services.file.get(id)

    if file is None:
        response.status_code = 404
        return {"message": "Arquivo não encontrado"}
