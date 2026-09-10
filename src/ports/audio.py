from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Optional, Sequence

from ..models.mix_profile import EqBand


class AudioCancelled(Exception):
    """El motor detuvo la operación por solicitud de cancelación (SPEC005 AC-07)."""


class ExportFormat(Enum):
    """Formatos de exportación del MVP (SPEC007)."""

    WAV_44100_24 = "wav"
    MP3_320 = "mp3"


@dataclass
class TempoAnalysis:
    ratio: float            # ratio tempo stem/ref (>=1 = más rápido)
    confidence: float       # correlación normalizada [0,1]


@dataclass
class AlignmentAnalysis:
    offset_ms: int          # corrección a aplicar: +delay / -recorte (ms)
    confidence: float


@dataclass
class RenderStem:
    """Ajustes consolidados de un stem para render/export (SPEC005 AC-05)."""

    path: str
    gain_db: float = 0.0
    pan: float = 0.0                       # [-1, 1]; negativo = izquierda
    hpf_hz: Optional[float] = None
    eq: List[EqBand] = field(default_factory=list)
    compressor_threshold_db: Optional[float] = None
    compressor_ratio: Optional[float] = None
    compressor_attack_ms: Optional[float] = None
    compressor_release_ms: Optional[float] = None
    makeup_gain_db: float = 0.0
    tempo_ratio: Optional[float] = None    # corrección no destructiva (D2)
    offset_ms: int = 0                     # desfase aplicable (auto o manual, SPEC004)


@dataclass
class Normalization:
    """Objetivo de normalización final de la mezcla (D1)."""

    lufs: float
    true_peak_db: float


ProgressCallback = Callable[[int], None]
CancelCheck = Callable[[], bool]


class AudioEngine(ABC):
    """Puerto del motor de audio: analizar, renderizar y exportar (ARCHITECTURE.md)."""

    @abstractmethod
    def analyze_tempo(self, path: str, reference_path: str) -> TempoAnalysis:
        """Analiza la relación de tempo entre un stem y la referencia."""
        ...

    @abstractmethod
    def analyze_alignment(self, path: str, reference_path: str) -> AlignmentAnalysis:
        """Analiza el desfase de inicio entre un stem y la referencia."""
        ...

    @abstractmethod
    def is_decodable(self, path: str) -> bool:
        """Comprueba si FFmpeg puede decodificar el archivo."""
        ...

    @abstractmethod
    def render_mix(
        self,
        stems: Sequence[RenderStem],
        out_path: str,
        normalization: Optional[Normalization] = None,
        on_progress: Optional[ProgressCallback] = None,
        cancel: Optional[CancelCheck] = None,
    ) -> None:
        """Renderiza la mezcla estéreo a WAV temporal hasta el stem más largo.

        Lanza `AudioCancelled` si `cancel()` devuelve True (limpiando el parcial)
        y `DomainError` ante fallo de FFmpeg (SPEC005 AC-06/AC-07).
        """
        ...

    @abstractmethod
    def export_mix(
        self,
        stems: Sequence[RenderStem],
        out_path: str,
        fmt: ExportFormat,
        normalization: Optional[Normalization] = None,
        on_progress: Optional[ProgressCallback] = None,
        cancel: Optional[CancelCheck] = None,
    ) -> None:
        """Exporta la mezcla final: WAV 44.1 kHz/24-bit o MP3 320 kbps (SPEC007).

        Lanza `AudioCancelled` si se cancela (limpiando la salida parcial) y
        `DomainError` ante fallo de escritura o de FFmpeg (SPEC007 AC-06).
        """
        ...

