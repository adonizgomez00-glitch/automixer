from __future__ import annotations
from typing import Optional

from ..models.project import MixProject, Stem, StemType
from ..ports.audio import AudioEngine
from ..utils.result import DomainError, Result


# Umbrales de fiabilidad (decisión D2).
TEMPO_MIN_CONFIDENCE = 0.80
TEMPO_MIN_RATIO = 0.75
TEMPO_MAX_RATIO = 1.33
ALIGN_MIN_CONFIDENCE = 0.85
ALIGN_MAX_OFFSET_MS = 2000


class AlignmentService:
    """Sincronización de tempo y alineación temporal (SPEC004) con umbrales D2."""

    def __init__(self, engine: AudioEngine) -> None:
        self._engine = engine

    # --- Referencia ---

    def primary_reference(self, project: MixProject) -> Optional[Stem]:
        """Referencia por defecto: batería; si no existe, primer stem válido (SPEC004 AC-01/02)."""
        available = [s for s in project.stems if s.available]
        for stem in available:
            if stem.type == StemType.BATERIA:
                return stem
        return available[0] if available else None

    def reference_for(self, project: MixProject) -> Optional[Stem]:
        """Resuelve la referencia fijada en el proyecto o la primaria."""
        if project.reference_stem_id:
            stem = project.find_stem(project.reference_stem_id)
            if stem is not None and stem.available:
                return stem
        return self.primary_reference(project)

    def set_reference(self, project: MixProject, stem: Stem) -> Result:
        """Fija manualmente la referencia; recalcula stems sin desfase manual (SPEC004 AC-06)."""
        if stem.id not in {s.id for s in project.stems}:
            return Result.err(DomainError("stem.not_found", {"stem_id": stem.id}))
        project.reference_stem_id = stem.id
        ref = self.reference_for(project)
        if ref is None:
            return Result.err(DomainError("project.no_valid_stems"))
        # Recalc de stems sin desfase manual (los con manual_offset_ms se conservan).
        for s in project.stems:
            if s.id == ref.id:
                continue
            if s.corrections.manual_offset_ms is None:
                s.corrections.tempo_ratio = None
                s.corrections.start_offset_ms = None
                s.corrections.confidence = None
        return Result.ok(ref)

    # --- Sincronizar tempo / alinear inicio ---

    def sync_tempo(self, project: MixProject, stem: Stem) -> Result:
        """Sincroniza tempo; aplica solo si el análisis es fiable y dentro de límites (SPEC004 AC-03)."""
        ref = self.reference_for(project)
        if ref is None or ref.id == stem.id:
            return Result.err(DomainError("project.no_valid_reference"))
        analysis = self._engine.analyze_tempo(stem.path, ref.path)
        reliable = analysis.confidence >= TEMPO_MIN_CONFIDENCE
        within_ratio = TEMPO_MIN_RATIO <= analysis.ratio <= TEMPO_MAX_RATIO
        if not reliable or not within_ratio:
            # Advertencia y stem intacto (SPEC004 AC-05).
            return Result.err(
                DomainError(
                    "sync.low_confidence_tempo",
                    {"confidence": round(analysis.confidence * 100)},
                )
            )
        stem.corrections.tempo_ratio = analysis.ratio
        stem.corrections.confidence = analysis.confidence
        return Result.ok(analysis)

    def align_start(self, project: MixProject, stem: Stem) -> Result:
        """Alinea inicio; aplica solo si es fiable y |desfase| <= 2 s (SPEC004 AC-04)."""
        ref = self.reference_for(project)
        if ref is None or ref.id == stem.id:
            return Result.err(DomainError("project.no_valid_reference"))
        analysis = self._engine.analyze_alignment(stem.path, ref.path)
        reliable = analysis.confidence >= ALIGN_MIN_CONFIDENCE
        within_offset = abs(analysis.offset_ms) <= ALIGN_MAX_OFFSET_MS
        if not reliable or not within_offset:
            return Result.err(
                DomainError(
                    "sync.low_confidence_alignment",
                    {"confidence": round(analysis.confidence * 100)},
                )
            )
        stem.corrections.start_offset_ms = analysis.offset_ms
        stem.corrections.confidence = analysis.confidence
        return Result.ok(analysis)

    # --- Desfase manual ---

    def set_manual_offset(self, project: MixProject, stem: Stem, ms: int) -> Result:
        """Desfase manual ±ms, prioridad solo en ese stem (SPEC004 AC-06)."""
        stem.corrections.manual_offset_ms = int(ms)
        return Result.ok(stem)
