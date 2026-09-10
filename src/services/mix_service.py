from __future__ import annotations
import os
from typing import Callable, Optional

from ..models.project import MixProject, Stem
from ..ports.artifacts import ArtifactStore
from ..ports.audio import (
    AudioCancelled,
    AudioEngine,
    ExportFormat,
    Normalization,
    RenderStem,
)
from ..ports.playback import Playback
from ..services.profile_service import ProfileService
from ..utils.result import DomainError, Result


class MixService:
    """Render de mezcla temporal, vista previa y exportación (SPEC005–SPEC007).

    - Consolidación de ajustes: perfil (D1) + ganancia manual + correcciones D2;
      el desfase manual tiene prioridad sobre la alineación automática (SPEC004).
    - El temporal anterior se conserva si el render nuevo falla (SPEC005 AC-06).
    - Solo se limpian temporales propios (SPEC005 restricciones).
    """

    def __init__(
        self,
        profile: ProfileService,
        engine: AudioEngine,
        artifacts: ArtifactStore,
        playback: Playback,
    ) -> None:
        self._profile = profile
        self._engine = engine
        self._artifacts = artifacts
        self._playback = playback
        self._preview_path: Optional[str] = None
        self._project: Optional[MixProject] = None

    # --- ajustes consolidados (SPEC005 AC-05) ---

    def _offset_for(self, stem: Stem) -> int:
        """Desfase aplicable: manual primero; si no, corrección automática."""
        corrections = stem.corrections
        if corrections.manual_offset_ms is not None:
            return int(corrections.manual_offset_ms)
        if corrections.start_offset_ms is not None:
            return int(corrections.start_offset_ms)
        return 0

    def build_render_stems(self, project: MixProject) -> list[RenderStem]:
        self._project = project
        stems: list[RenderStem] = []
        for stem in project.stems:
            if not stem.available:
                continue
            prof = self._profile.profile_for(project.genre, stem.type)
            pan = self._profile.pan_for_stem(project, stem)
            compressor = prof.compressor
            stems.append(
                RenderStem(
                    path=stem.path,
                    gain_db=stem.gain_db,
                    pan=pan,
                    hpf_hz=prof.hpf_hz,
                    eq=list(prof.eq),
                    compressor_threshold_db=compressor.threshold_db if compressor else None,
                    compressor_ratio=compressor.ratio if compressor else None,
                    compressor_attack_ms=compressor.attack_ms if compressor else None,
                    compressor_release_ms=compressor.release_ms if compressor else None,
                    makeup_gain_db=prof.makeup_gain_db,
                    tempo_ratio=stem.corrections.tempo_ratio,
                    offset_ms=self._offset_for(stem),
                )
            )
        return stems

    def _normalization(self, project: MixProject) -> Optional[Normalization]:
        norm = self._profile.normalization(project.genre)
        if norm is None:
            return None
        return Normalization(lufs=norm.lufs, true_peak_db=norm.true_peak_db)

    # --- render temporal (SPEC005) ---

    def render_preview(
        self,
        project: MixProject,
        on_progress: Optional[Callable[[int], None]] = None,
        cancel: Optional[Callable[[], bool]] = None,
    ) -> Result:
        """Renderiza el WAV temporal; devuelve su ruta (SPEC005 AC-01/03/04/05)."""
        valid = [s for s in project.stems if s.available]
        if not valid:
            return Result.err(DomainError("project.no_valid_stems"))
        new_path = self._artifacts.new_temp_path(".wav")
        try:
            self._engine.render_mix(
                self.build_render_stems(project),
                new_path,
                self._normalization(project),
                on_progress,
                cancel,
            )
        except AudioCancelled:
            self._artifacts.discard(new_path)
            return Result.err(DomainError("job.cancelled"))
        except DomainError as exc:
            self._artifacts.discard(new_path)
            return Result.err(exc)
        except Exception:  # noqa: BLE001 - limpia el parcial y conserva la preview anterior
            self._artifacts.discard(new_path)
            raise
        previous = self._preview_path
        self._preview_path = new_path
        if previous:
            self._artifacts.discard(previous)
        return Result.ok(new_path)

    @property
    def preview_path(self) -> Optional[str]:
        return self._preview_path

    # --- vista previa (SPEC006) ---

    def load_preview(self) -> Result:
        """Carga el temporal activo en el reproductor (SPEC006 AC-01/AC-07)."""
        if not self._preview_path or not os.path.isfile(self._preview_path):
            return Result.err(DomainError("preview.pending_mix"))
        return self._playback.load(self._preview_path)

    @property
    def playback(self) -> Playback:
        return self._playback

    # --- exportación (SPEC007) ---

    def export(
        self,
        project: MixProject,
        dest_path: Optional[str],
        fmt: ExportFormat,
        overwrite: bool = False,
        on_progress: Optional[Callable[[int], None]] = None,
        cancel: Optional[Callable[[], bool]] = None,
    ) -> Result:
        """Exporta la mezcla final; nunca modifica archivos originales (SPEC007)."""
        if not dest_path:
            # Diálogo cancelado: no se crea ningún archivo (SPEC007 AC-05).
            return Result.err(DomainError("export.cancelled"))
        if os.path.exists(dest_path) and not overwrite:
            # Sin confirmación no se sobrescribe (SPEC007 AC-03).
            return Result.err(DomainError("export.overwrite_confirmation"))
        try:
            self._engine.export_mix(
                self.build_render_stems(project),
                dest_path,
                fmt,
                self._normalization(project),
                on_progress,
                cancel,
            )
        except AudioCancelled:
            self._discard_if_empty_partial(dest_path)
            return Result.err(DomainError("job.cancelled"))
        except DomainError as exc:
            self._discard_if_empty_partial(dest_path)
            return Result.err(exc)
        except Exception:
            self._discard_if_empty_partial(dest_path)
            raise
        return Result.ok(dest_path)

    @staticmethod
    def _discard_if_empty_partial(dest_path: str) -> None:
        """Elimina una salida parcial vacía (el motor ya limpia las suyas)."""
        try:
            if os.path.isfile(dest_path) and os.path.getsize(dest_path) == 0:
                os.remove(dest_path)
        except OSError:
            pass

    # --- cierre (SPEC005 limpieza) ---

    def close(self) -> None:
        """Cierra la mezcla: para la preview y borra los temporales propios."""
        self._playback.unload()
        self._preview_path = None
        self._artifacts.cleanup_all()

