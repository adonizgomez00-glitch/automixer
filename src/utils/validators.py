
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


# --- Auto-detección de tipo de stem desde nombre de archivo ---

_TYPE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "bateria":         ("drums", "drum", "bateria", "drumtrack", "kick", "snare"),
    "voz":             ("vocals", "vocal", "voice", "vox", "voz", "acapella", "lead_vocal"),
    "bajo":            ("bass", "bajo", "sub", "subbass"),
    "guitarra":        ("guitar", "guitarra", "gtr", "electric", "acoustic"),
    "teclados":        ("keys", "keyboard", "teclados", "piano", "rhodes", "organ"),
    "sintetizadores":  ("synth", "synths", "sintetizadores", "lead", "pad", "arpeggio"),
    "drops":           ("drops", "drop"),
    "efectos":         ("fx", "effects", "efectos", "sfx", "riser", "impact", "reverse"),
}


def detect_stem_type(filename: str) -> str:
    """Detecta el tipo de stem desde el nombre del archivo.

    Devuelve el valor string de StemType (ej: "bateria", "voz", "otro").
    Busca keywords en el nombre completo, ignore case.
    """
    name_lower = filename.lower()
    for stype, keywords in _TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw in name_lower:
                return stype
    return "otro"
