from abc import ABC
import logging
import shutil
import io

from pathlib import Path
from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from pypdf import PdfReader, PdfWriter
from pypdf._page import PageObject
from pypdf.generic import ArrayObject, NameObject

from typing import Any, BinaryIO, Generator
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


# TODO: handle files asynchronously
def upload(data: UploadFile) -> UUID:
    if not data.filename:
        raise HTTPException(status_code=400, detail="Arquivo sem nome.")

    Strategy = get_file_strategy(data.filename)

    strategy = Strategy(data.filename, data.file)

    return strategy.id


# TODO: handle errors (disk full, permissions)
def store_binary(file: BinaryIO, directory: Path, filename: str):
    file_path = directory / filename

    with file_path.open("wb") as f:
        shutil.copyfileobj(file, f)


class FileStrategy(ABC):
    def __init__(self, filename: str, file: BinaryIO) -> None:
        super().__init__()

        self.id = uuid4()
        self.filename = filename

        chunks = list(self._get_chunks(file))

        path = STATIC_PATH / str(self.id)

        path.mkdir(parents=True, exist_ok=True)

        for index, chunk in enumerate(chunks, start=1):
            logging.info("STORING CHUNK %d OF %d", index, len(chunks))

            store_binary(
                chunk, path, self._get_chunk_filename(index, total=len(chunks))
            )
            chunk.close()

    def _get_chunks(self, file: BinaryIO) -> Generator[io.BytesIO, None, None]:
        yield io.BytesIO(file.read())

    def _get_chunk_filename(self, chunk_number: int, total: int) -> str:
        if total == 1:
            return self.filename

        directory = Path(self.filename)

        return f"{directory.stem}_{chunk_number}{directory.suffix}"


class PdfStrategy(FileStrategy):
    def _get_chunks(self, file: BinaryIO) -> Generator[io.BytesIO, None, None]:
        # TODO: validate that the file is readable before reading

        logging.info("READING PDF FILE")

        reader = PdfReader(file)
        total_pages = len(reader.pages)

        logging.info("READ PDF FILE WITH %d PAGES", total_pages)

        for i in range(0, total_pages, CHUNK_SIZE):
            writer = PdfWriter()

            last_page = min(i + CHUNK_SIZE, total_pages)

            logging.info(
                "READING PAGES %d TO %d OF %d",
                i + 1,
                last_page,
                total_pages,
            )

            for page_num in range(i, last_page):
                page = reader.pages[page_num]

                self._remove_page_references(page)

                writer.add_page(page)

            stream = io.BytesIO()
            logging.info("WRITING CHUNK TO STREAM")
            # TODO: this is taking too long
            writer.write(stream)
            logging.info("WROTE CHUNK TO STREAM")

            stream.seek(0)

            yield stream

            logging.info(
                "READ PAGES %d TO %d",
                i + 1,
                last_page,
            )

    def _remove_page_references(self, page: PageObject):
        if not page.get("/Annots"):
            return

        annots = page["/Annots"].get_object()

        if not isinstance(annots, ArrayObject):
            return

        new_annots: list[Any] = []

        for annot_ref in annots:
            annot = (
                annot_ref.get_object()
                if hasattr(annot_ref, "get_object")
                else annot_ref
            )

            if annot.get("/Subtype") == "/Link":
                if "/Dest" in annot:
                    continue

                action = annot.get("/A")

                if action is not None:
                    if hasattr(action, "get_object"):
                        action = action.get_object()

                    if action.get("/S") == "/GoTo":
                        continue

            new_annots.append(annot_ref)

        page[NameObject("/Annots")] = ArrayObject(new_annots)


class DefaultStrategy(FileStrategy):
    pass


def get_file_strategy(filename: str) -> type[FileStrategy]:
    ext = Path(filename).suffix.lower()

    strategies = {".pdf": PdfStrategy}

    return strategies.get(ext, DefaultStrategy)
