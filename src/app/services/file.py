import shutil

from uuid import UUID, uuid4
from pathlib import Path

from fastapi.datastructures import UploadFile

STATIC_PATH = Path("./src/app/static")


def get(id: UUID) -> None:
    return None


async def upload(file: UploadFile):
    if not file.filename:
        return

    id = uuid4()

    target_path = STATIC_PATH / str(id)
    file_path = target_path / file.filename

    target_path.mkdir(parents=True)

    with file_path.open("w") as f:
        shutil.copyfileobj(file.file, f.buffer)
