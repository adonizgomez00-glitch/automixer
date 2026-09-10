from __future__ import annotations
import os
import shutil
import tempfile
from typing import Optional, Set

from ..ports.artifacts import ArtifactStore


class TempArtifactStore(ArtifactStore):
    """Temporales privados en un directorio propio (SPEC005, SPEC009).

    - `new_temp_path` registra cada ruta creada; solo esas se borran luego.
    - `cleanup_all` elimina el directorio completo de temporales propios.
    """

    def __init__(self, base_dir: Optional[str] = None) -> None:
        self._base = base_dir or tempfile.mkdtemp(prefix="automixer-preview-")
        self._owned: Set[str] = set()
        os.makedirs(self._base, exist_ok=True)

    @property
    def base_dir(self) -> str:
        return self._base

    def new_temp_path(self, suffix: str = ".wav") -> str:
        fd, path = tempfile.mkstemp(prefix="mix-", suffix=suffix, dir=self._base)
        os.close(fd)
        self._owned.add(path)
        return path

    def discard(self, path: str) -> None:
        if path in self._owned and os.path.isfile(path):
            os.remove(path)
        self._owned.discard(path)

    def cleanup_all(self) -> None:
        shutil.rmtree(self._base, ignore_errors=True)
        self._owned.clear()
