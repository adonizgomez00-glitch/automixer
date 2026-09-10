
from __future__ import annotations
import os

from .result import DomainError


MIN_GAIN_DB = -60.0
MAX_GAIN_DB = 12.0
SUPPORTED_EXTENSIONS = ("mp3", "flac", "wav")


def is_supported_extension(path: str) -> bool:
    return path.lower().endswith(SUPPORTED_EXTENSIONS)


def validate_gain(gain_db: float) -> None:
    if not (MIN_GAIN_DB <= gain_db <= MAX_GAIN_DB):
        raise DomainError("stem.gain_out_of_range")


def folder_is_writable(path: str) -> bool:
    try:
        return os.path.isdir(path) and os.access(path, os.W_OK)
    except OSError:
        return False


def file_exists(path: str) -> bool:
    try:
        return os.path.isfile(path)
    except OSError:
        return False
