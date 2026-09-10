from __future__ import annotations
import os
from typing import Optional

from ..models.project import Genre, MixProject, Stem, StemType
from ..ports.audio import AudioEngine
from ..ports.repositories import ProjectRepository, SettingsRepository
from ..repositories.json_project_repository import PROJECT_EXTENSION
from ..services.profile_service import ProfileService
from ..utils import validators
from ..utils.result import DomainError, Result


# Formato del nombre de archivo por defecto de un proyecto.
def project_file_path(folder: str, name: str) -> str:
    safe = name.strip()
    if not safe:
        safe = "proyecto"
    return os.path.join(folder, safe + PROJECT_EXTENSION)


class ProjectService:
    """Reglas de aplicación de gestión de proyecto local (SPEC001, SPEC002, SPEC008)."""

    def __init__(
        self,
        repo: ProjectRepository,
        settings: SettingsRepository,
        profile: Optional[ProfileService] = None,
        engine: Optional[AudioEngine] = None,
    ) -> None:
        self._repo = repo
        self._settings = settings
        self._profile = profile
        self._engine = engine
        self._active: Optional[MixProject] = None
        self._active_path: Optional[str] = None

    # --- acceso ---

    @property
    def active_project(self) -> Optional[MixProject]:
        return self._active

    @property
    def active_path(self) -> Optional[str]:
        return self._active_path

    @property
    def valid_stems(self) -> list[Stem]:
        return [s for s in self._active.stems if s.available] if self._active else []

    @property
    def mix_enabled(self) -> bool:
        """`Mezclar` requiere al menos un stem válido (SPEC002 AC-05/06)."""
        return len(self.valid_stems) >= 1

    def create(self, name: str, folder: str) -> Result:
        """Crea (en memoria) un proyecto activo. SPEC001 AC-01..03."""
        name = (name or "").strip()
        if not name:
            return Result.err(DomainError("project.name_empty"))
        if not validators.folder_is_writable(folder):
            return Result.err(DomainError("project.folder_notwritable"))
        project = MixProject(name=name)
        self._active = project
        self._active_path = project_file_path(folder, name)
        return Result.ok(project)

    def save(self, *, autosave: bool = False) -> Result:
        """Guarda el proyecto activo de forma atómica. SPEC008 AC-01/02."""
        if self._active is None or self._active_path is None:
            return Result.err(DomainError("project.not_open"))
        try:
            self._repo.save(self._active, self._active_path)
        except DomainError as exc:
            return Result.err(exc)
        return Result.ok(self._active_path)

    def save_to(self, project: MixProject, path: str) -> Result:
        try:
            self._repo.save(project, path)
        except DomainError as exc:
            return Result.err(exc)
        return Result.ok(path)

    def open(self, path: str) -> Result:
        try:
            project = self._repo.load(path)
        except DomainError as exc:
            return Result.err(exc)
        self._repo.revalidate_availability(project)
        self._active = project
        self._active_path = path
        return Result.ok(project)

    def close(self) -> Result:
        """Cierra el proyecto activo (los temporales se gestionan en Fase 3)."""
        self._active = None
        self._active_path = None
        return Result.ok()


    # --- SPEC002: importación y clasificación ---

    def add_stem(self, path: str, stype: StemType = StemType.OTRO) -> Result:
        """Agrega un stem validando extensión, existencia y decodificación. SPEC002 AC-01/02/03."""
        if self._active is None:
            return Result.err(DomainError("project.not_open"))
        if not validators.is_supported_extension(path):
            return Result.err(DomainError("stem.format_unsupported"))
        if not validators.file_exists(path):
            return Result.err(DomainError("stem.not_found", {"path": path}))
        if self._engine is not None and not self._engine.is_decodable(path):
            return Result.err(DomainError("stem.decode_failed"))
        stem = Stem(path=path, type=stype, available=True)
        if self._profile is not None:
            self._profile.apply_defaults(self._active, stem)
        self._active.add_stem(stem)
        return Result.ok(stem)

    def set_stem_type(self, stem_id: str, stype: StemType) -> Result:
        """Clasifica manualmente un stem y aplica defaults del perfil activo. SPEC002 AC-04."""
        if self._active is None:
            return Result.err(DomainError("project.not_open"))
        stem = self._active.find_stem(stem_id)
        if stem is None:
            return Result.err(DomainError("stem.not_found", {"stem_id": stem_id}))
        stem.type = stype
        if self._profile is not None:
            self._profile.apply_defaults(self._active, stem)
        return Result.ok(stem)

    def relocate_stem(self, stem_id: str, new_path: str) -> Result:
        """Actualiza la ruta de un stem y revalida su disponibilidad. SPEC008 AC-06."""
        if self._active is None:
            return Result.err(DomainError("project.not_open"))
        if not validators.is_supported_extension(new_path):
            return Result.err(DomainError("stem.format_unsupported"))
        stem = self._active.find_stem(stem_id)
        if stem is None:
            return Result.err(DomainError("stem.not_found", {"stem_id": stem_id}))
        stem.path = new_path
        stem.available = validators.file_exists(new_path)
        if self._engine is not None and stem.available:
            stem.available = self._engine.is_decodable(new_path)
        return Result.ok(stem)

    def set_gain(self, stem_id: str, gain_db: float) -> Result:
        """Ganancia manual por stem (-60 a +12 dB). SPEC003 AC-04/05."""
        if self._active is None:
            return Result.err(DomainError("project.not_open"))
        try:
            validators.validate_gain(gain_db)
        except DomainError as exc:
            return Result.err(exc)
        stem = self._active.find_stem(stem_id)
        if stem is None:
            return Result.err(DomainError("stem.not_found", {"stem_id": stem_id}))
        stem.gain_db = gain_db
        return Result.ok(stem)


    # --- SPEC003: cambio de género y restablecer ---

    def change_genre(self, genre: Genre) -> Result:
        """Cambia el género activo y restablece ganancias al nuevo perfil. SPEC003 AC-06."""
        if self._active is None:
            return Result.err(DomainError("project.not_open"))
        self._active.genre = genre
        if self._profile is not None:
            for stem in self._active.stems:
                self._profile.reset_gain(self._active, stem)
        return Result.ok(genre)

    def reset_stem(self, stem_id: str) -> Result:
        """Restablecer: vuelve al perfil activo (ganancia, correcciones, desfase). SPEC003 AC-07 / SPEC004 AC-08."""
        if self._active is None:
            return Result.err(DomainError("project.not_open"))
        stem = self._active.find_stem(stem_id)
        if stem is None:
            return Result.err(DomainError("stem.not_found", {"stem_id": stem_id}))
        if self._profile is not None:
            self._profile.reset_stem(self._active, stem)
        else:
            stem.gain_db = 0.0
            stem.corrections.tempo_ratio = None
            stem.corrections.start_offset_ms = None
            stem.corrections.confidence = None
            stem.corrections.manual_offset_ms = None
        return Result.ok(stem)

    # --- SPEC010: preferencias de idioma ---

    def get_language(self) -> Optional[str]:
        return self._settings.get_language()

    def set_language(self, lang: str) -> None:
        self._settings.set_language(lang)

