from pathlib import Path
import shutil

from uuid import UUID, uuid4
from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from pypdf import PdfReader, PdfWriter

from app.constants import CHUNK_SIZE, STATIC_PATH


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


async def upload(file: UploadFile) -> UUID:
    reader = PdfReader(file.file)
    total_pages = len(reader.pages)

    await file.seek(0)
    reader.close()

    if total_pages <= CHUNK_SIZE:
        id = await upload_single_chunk_pdf(file)
        return id

    id = await upload_multiple_chunk_pdf(file, total_pages)
    return id


async def upload_single_chunk_pdf(file: UploadFile) -> UUID:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Arquivo sem nome.")

    id = uuid4()

    target_path = STATIC_PATH / str(id)
    file_path = target_path / file.filename

    target_path.mkdir(parents=True)

    with file_path.open("w") as f:
        shutil.copyfileobj(file.file, f.buffer)

    return id


async def upload_multiple_chunk_pdf(file: UploadFile, total_pages: int) -> UUID:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Arquivo sem nome.")

    reader = PdfReader(file.file)

    id = uuid4()

    target_path = STATIC_PATH / str(id)
    target_path.mkdir(parents=True)

    for i in range(0, total_pages, CHUNK_SIZE):
        writer = PdfWriter()

        for page_num in range(i, min(i + CHUNK_SIZE, total_pages)):
            writer.add_page(reader.pages[page_num])

        chunk = i // CHUNK_SIZE + 1
        extension = "pdf"

        output_filename = (
            f"{''.join(file.filename.split('.')[:-1])}_{chunk}.{extension}"
        )

        file_path = target_path / output_filename

        with file_path.open("wb") as f:
            writer.write(f)

    return id
