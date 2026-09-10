from __future__ import annotations

import locale
import os
from typing import Optional

from ..i18n.catalogs import (
    DEFAULT_LANGUAGE,
    PRODUCT_DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    t as translate,
)
from ..ports.repositories import SettingsRepository
from ..utils.result import DomainError, Result


def _normalize(code: Optional[str]) -> Optional[str]:
    """`'es-ES'`, `'es_ES'`, `'Es'` → `'es'`; devuelve None si no es soportado."""
    if not code:
        return None
    base = code.replace("_", "-").split("-")[0].strip().lower()
    return base if base in SUPPORTED_LANGUAGES else None


def detect_system_language() -> str:
    """Idioma del sistema (entorno/locale); `''` si no se puede determinar."""
    for var in ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"):
        value = os.environ.get(var, "").strip()
        if value:
            return value
    try:
        return (locale.getlocale(locale.LC_MESSAGES)[0] or "")
    except Exception:  # noqa: BLE001 - locale no inicializado
        return ""


class I18nService:
    """Idioma de la interfaz (SPEC010).

    Orden de resolución al inicio (SPEC010 AC-01..AC-04, decisión D6):
    1. preferencia guardada (AC-01);
    2. idioma del sistema si es `es`/`en` (AC-02/AC-03);
    3. idioma predeterminado de producto **español** si no hay soporte (AC-04).
    El selector manual persiste la preferencia vía `SettingsRepository` (AC-05).
    """

    def __init__(
        self,
        settings: SettingsRepository,
        system_language: Optional[str] = None,
    ) -> None:
        self._settings = settings
        self._system_language = system_language or detect_system_language()
        saved = _normalize(settings.get_language())
        system = _normalize(self._system_language)
        self._language: str = (
            saved
            or system
            or PRODUCT_DEFAULT_LANGUAGE
        )

    @staticmethod
    def supported_codes() -> tuple[str, ...]:
        return SUPPORTED_LANGUAGES

    @property
    def language(self) -> str:
        return self._language

    @property
    def system_language(self) -> str:
        return self._system_language

    def tr(self, code: str, params: Optional[dict] = None) -> str:
        """Texto localizado en el idioma activo (fallback a catálogo por defecto)."""
        return translate(code, self._language, params)

    def set_language(self, lang: str) -> Result:
        """Cambia el idioma al instante y persiste la preferencia (SPEC010 AC-05)."""
        normalized = _normalize(lang)
        if not normalized:
            return Result.err(DomainError("i18n.unsupported_language"))
        self._settings.set_language(normalized)
        self._language = normalized
        return Result.ok(normalized)

    def reset_language(self) -> Result:
        """Elimina la preferencia guardada (vuelve a detección por sistema/D6)."""
        try:
            self._settings.set_language("")
        except Exception:  # noqa: BLE001
            pass
        system = _normalize(self._system_language)
        self._language = system or PRODUCT_DEFAULT_LANGUAGE
        return Result.ok(self._language)