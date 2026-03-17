import shutil
import io

from pathlib import Path
from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from pypdf import PdfReader, PdfWriter

from typing import BinaryIO, Generator
from uuid import UUID, uuid4

from app.constants import CHUNK_SIZE, STATIC_PATH


class FileNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Arquivo não encontrado")


class InvalidChunkException(HTTPException):
    def __init__(self):
        super().__init__(status_code=422, detail="Chunk inválido")


def get(id: UUID, chunk: int = 1) -> str:
    chunk_index = chunk - 1

    if chunk_index < 0:
        raise InvalidChunkException

    target_path = STATIC_PATH / str(id)

    if not target_path.is_dir():
        raise FileNotFoundException

    files = [f for f in target_path.iterdir() if f.is_file()]

    total_files = len(files)

    if total_files == 0:
        raise FileNotFoundException

    if chunk_index >= total_files:
        raise InvalidChunkException

    target = files[chunk - 1]
    web_path = Path("static") / str(id) / target.name

    return f"/{web_path.as_posix()}"


async def upload(data: UploadFile) -> UUID:
    if not data.filename:
        raise HTTPException(status_code=400, detail="Arquivo sem nome.")

    with PdfReader(data.file) as reader:
        total_pages = len(reader.pages)

    await data.seek(0)

    id = uuid4()

    if total_pages <= CHUNK_SIZE:
        store_file(data.file, data.filename, id)
    else:
        for idx, chunk in enumerate(get_chunks(data.file)):
            store_file(chunk, data.filename, id, idx + 1)
            chunk.close()

    return id


def get_chunks(original_file: BinaryIO) -> Generator[io.BytesIO, None, None]:
    reader = PdfReader(original_file)
    total_pages = len(reader.pages)

    for i in range(0, total_pages, CHUNK_SIZE):
        writer = PdfWriter()

        last_page = min(i + CHUNK_SIZE, total_pages)

        for page_num in range(i, last_page):
            writer.add_page(reader.pages[page_num])

        stream = io.BytesIO()
        writer.write(stream)

        stream.seek(0)

        yield stream


def store_file(
    file: BinaryIO, filename: str, id: UUID, chunk_number: int | None = None
):
    file_name = get_filename(filename, chunk_number)

    target_path = STATIC_PATH / str(id)
    file_path = target_path / file_name

    target_path.mkdir(parents=True, exist_ok=True)

    with file_path.open("wb") as f:
        shutil.copyfileobj(file, f)


def get_filename(filename: str, chunk_number: int | None) -> str:
    if chunk_number is None:
        return filename

    path = Path(filename)

    return f"{path.stem}_{chunk_number}.{path.suffix}"
