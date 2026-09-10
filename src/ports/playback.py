from __future__ import annotations
from abc import ABC, abstractmethod

from ..utils.result import Result


class Playback(ABC):
    """Reproducción del WAV temporal de vista previa (SPEC006, ARCHITECTURE.md).

    El volumen de preview no altera la mezcla ni la exportación (SPEC006 AC-06).
    """

    @abstractmethod
    def load(self, path: str) -> Result:
        """Carga el WAV temporal; habilita los controles si es válido (AC-01)."""
        ...

    @abstractmethod
    def has_source(self) -> bool:
        """Indica si hay un temporal cargado y accesible (AC-07)."""
        ...

    @abstractmethod
    def play(self) -> Result:
        """Inicia la reproducción desde la posición actual (AC-02)."""
        ...

    @abstractmethod
    def pause(self) -> Result:
        """Pausa conservando la posición (AC-03)."""
        ...

    @abstractmethod
    def stop(self) -> Result:
        """Detiene y vuelve a la posición inicial (AC-04)."""
        ...

    @abstractmethod
    def seek(self, position_ms: int) -> Result:
        """Busca la posición indicada (AC-05)."""
        ...

    @abstractmethod
    def set_volume(self, volume: float) -> Result:
        """Volumen general de preview en [0, 1] (AC-06)."""
        ...

    @abstractmethod
    def position_ms(self) -> int:
        """Posición actual de reproducción."""
        ...

    @abstractmethod
    def duration_ms(self) -> int:
        """Duración del temporal cargado (0 si no hay fuente)."""
        ...

    @abstractmethod
    def is_playing(self) -> bool:
        """Estado de reproducción."""
        ...

    @abstractmethod
    def unload(self) -> None:
        """Libera la fuente activa (p. ej. al cerrar o al regenerar la mezcla)."""
        ...
