from __future__ import annotations
import json
import os
from typing import Optional

from ..ports.repositories import SettingsRepository


class FileSettingsRepository(SettingsRepository):
    """Preferencias en un fichero JSON de la carpeta de configuración de usuario."""

    def __init__(self, path: Optional[str] = None):
        self._path = path or self._default_path()
        if self._path is not None:
            os.makedirs(os.path.dirname(self._path), exist_ok=True)

    @staticmethod
    def _default_path() -> Optional[str]:
        base = os.environ.get("AUTOMIXER_CONFIG_DIR")
        if not base:
            return None
        return os.path.join(base, "settings.json")

    def _load(self) -> dict:
        if not self._path or not os.path.exists(self._path):
            return {}
        try:
            with open(self._path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, json.JSONDecodeError):
            return {}

    def _save(self, data: dict) -> None:
        if not self._path:
            return
        tmp = self._path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, self._path)

    def get_language(self) -> Optional[str]:
        return self._load().get("language")

    def set_language(self, lang: str) -> None:
        data = self._load()
        data["language"] = lang
        self._save(data)
