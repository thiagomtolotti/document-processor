import shutil
from uuid import UUID, uuid4

from fastapi.datastructures import UploadFile


def get(id: UUID) -> None:
    return None


async def upload(file: UploadFile):
    if not file.filename:
        return

    extension = file.filename.split(".")[-1]
    id = uuid4()

    target_path = f"./src/app/static/{id}.{extension}"

    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
