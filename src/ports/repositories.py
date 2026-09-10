
from __future__ import annotations
from abc import ABC, abstractmethod

from ..models.project import MixProject


class ProjectRepository(ABC):
    """Contrato del puerto de persistencia de proyectos `.automixer`."""

    @abstractmethod
    def save(self, project: MixProject, path: str) -> None:
        """Guarda de forma atómica. Lanza `DomainError` ante fallos."""
        ...

    @abstractmethod
    def load(self, path: str) -> MixProject:
        """Carga y valida el esquema. Lanza `DomainError` ante fallos."""
        ...


class SettingsRepository(ABC):
    """Contrato del puerto de preferencias de aplicación (p. ej. idioma)."""

    @abstractmethod
    def get_language(self) -> str | None:
        ...

    @abstractmethod
    def set_language(self, lang: str) -> None:
        ...
