from __future__ import annotations
from abc import ABC, abstractmethod


class ArtifactStore(ABC):
    """Gestión de temporales privados de la aplicación (ARCHITECTURE.md, SPEC005).

    Solo se crean y borran archivos generados por AutoMixer (SPEC005 restricciones):
    cada ruta se registra en el momento de crearse y `discard`/`cleanup_all`
    ignoran rutas ajenas.
    """

    @abstractmethod
    def new_temp_path(self, suffix: str = ".wav") -> str:
        """Crea (y registra) la ruta de un temporal nuevo y devuelve su ruta."""
        ...

    @abstractmethod
    def discard(self, path: str) -> None:
        """Elimina un temporal propio si existe; ignora rutas no registradas."""
        ...

    @abstractmethod
    def cleanup_all(self) -> None:
        """Elimina todos los temporales propios (cierre de proyecto o app)."""
        ...
