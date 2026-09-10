from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence

from ..ports.audio import (
    AlignmentAnalysis,
    AudioCancelled,
    AudioEngine,
    ExportFormat,
    Normalization,
    RenderStem,
    TempoAnalysis,
)
from ..utils.result import DomainError


@dataclass
class FakeResult:
    tempo: Optional[TempoAnalysis] = None
    alignment: Optional[AlignmentAnalysis] = None
    decodable: bool = True


class FakeAudioEngine(AudioEngine):
    """Motor fake para pruebas (determinista e inyectable).

    - `set` fija resultados de análisis por ruta de stem (umbrales D2).
    - Render/export crean un archivo en `out_path` y registran los ajustes
      recibidos (`renders`), salvo `fail_render=True` o cancelación.
    """

    def __init__(self, *, fail_render: bool = False) -> None:
        self.fail_render = fail_render
        self.renders: List[List[RenderStem]] = []
        self.results: Dict[str, FakeResult] = {}
        self.calls: List[str] = []

    def set(self, path: str, *, tempo=None, alignment=None, decodable=True) -> None:
        self.results[path] = FakeResult(
            tempo=tempo, alignment=alignment, decodable=decodable
        )

    def _result(self, path: str) -> FakeResult:
        return self.results.get(path, FakeResult())

    def analyze_tempo(self, path: str, reference_path: str) -> TempoAnalysis:
        self.calls.append(f"tempo:{path}")
        return self._result(path).tempo or TempoAnalysis(ratio=1.0, confidence=1.0)

    def analyze_alignment(self, path: str, reference_path: str) -> AlignmentAnalysis:
        self.calls.append(f"align:{path}")
        return self._result(path).alignment or AlignmentAnalysis(
            offset_ms=0, confidence=1.0
        )

    def is_decodable(self, path: str) -> bool:
        self.calls.append(f"decode:{path}")
        return self._result(path).decodable

    # --- render / export (Fase 3) ---

    def _render(
        self,
        stems: Sequence[RenderStem],
        out_path: str,
        failure_code: str,
        on_progress: Optional[Callable[[int], None]],
        cancel: Optional[Callable[[], bool]],
        tag: str,
    ) -> None:
        self.renders.append(list(stems))
        if self.fail_render:
            raise DomainError(failure_code)
        if cancel is not None and cancel():
            raise AudioCancelled()
        if any(not os.path.isfile(s.path) for s in stems):
            raise DomainError("stem.decode_failed")
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "wb") as fh:
            fh.write(f"RIFF-{tag}".encode())
        if on_progress:
            on_progress(100)

    def render_mix(
        self,
        stems: Sequence[RenderStem],
        out_path: str,
        normalization: Optional[Normalization] = None,
        on_progress: Optional[Callable[[int], None]] = None,
        cancel: Optional[Callable[[], bool]] = None,
    ) -> None:
        self._render(stems, out_path, "render.failed", on_progress, cancel, "preview")

    def export_mix(
        self,
        stems: Sequence[RenderStem],
        out_path: str,
        fmt: ExportFormat,
        normalization: Optional[Normalization] = None,
        on_progress: Optional[Callable[[int], None]] = None,
        cancel: Optional[Callable[[], bool]] = None,
    ) -> None:
        self._render(stems, out_path, "export.failed", on_progress, cancel, fmt.value)
