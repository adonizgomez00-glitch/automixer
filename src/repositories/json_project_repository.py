from __future__ import annotations
import json
import os
from typing import Any, Dict

from ..models.project import MixProject, SCHEMA_VERSION
from ..ports.repositories import ProjectRepository
from ..utils.result import DomainError
from ..utils import validators


# Extensión del archivo de proyecto.
PROJECT_EXTENSION = ".automixer"


class JsonProjectRepository(ProjectRepository):
    """Repositorio basado en JSON versionado con escritura atómica."""

    def save(self, project: MixProject, path: str) -> None:
        project.mark_updated()
        data: Dict[str, Any] = project.to_dict()
        tmp_path = path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp_path, path)
        except OSError as exc:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except OSError:
                pass
            raise DomainError("project.save_failed", {"detail": str(exc)}) from exc

    def load(self, path: str) -> MixProject:
        if not validators.file_exists(path):
            raise DomainError("project.not_found", {"path": path})
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            raise DomainError("project.load_failed", {"detail": str(exc)}) from exc

        schema = data.get("schema_version")
        if schema != SCHEMA_VERSION:
            raise DomainError("project.schema_unsupported", {"version": schema})
        try:
            return MixProject.from_dict(data)
        except (ValueError, TypeError, KeyError) as exc:
            raise DomainError("project.load_failed", {"detail": str(exc)}) from exc

    def revalidate_availability(self, project: MixProject) -> None:
        """Deriva `available` de cada stem desde el sistema de ficheros."""
        for stem in project.stems:
            stem.available = validators.file_exists(stem.path)
