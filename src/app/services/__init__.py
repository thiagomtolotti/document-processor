from .file import get, upload
from . import file as file  # re-exports the module itself

__all__ = ["get", "upload", "file"]
