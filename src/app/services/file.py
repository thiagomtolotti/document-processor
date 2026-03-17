from pathlib import Path
import shutil

from uuid import UUID, uuid4
from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException

from app.constants import STATIC_PATH


class FileNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Arquivo não encontrado")


def get(id: UUID) -> str:
    target_path = STATIC_PATH / str(id)

    if not target_path.is_dir():
        raise FileNotFoundException

    files = [f for f in target_path.iterdir() if f.is_file()]

    match len(files):
        case 0:
            raise FileNotFoundException
        case 1:
            web_path = Path("static") / str(id) / files[0].name

            return f"/{web_path.as_posix()}"
        case _:
            raise HTTPException(
                status_code=422, detail="Múltiplos arquivos encontrados."
            )


async def upload(file: UploadFile) -> UUID | None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Arquivo sem nome.")

    id = uuid4()

    target_path = STATIC_PATH / str(id)
    file_path = target_path / file.filename

    target_path.mkdir(parents=True)

    with file_path.open("w") as f:
        shutil.copyfileobj(file.file, f.buffer)

    return id
