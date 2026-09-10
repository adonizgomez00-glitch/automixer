from __future__ import annotations

"""Composición de dependencias (inyección manual) para la Fase 1.

Este módulo arma los puertos/repositorios/servicios reales. La construcción
completa de la GUI se habilita cuando PySide6 está disponible; si no, la app
arranca en modo núcleo (sin ventana) para desarrollo y pruebas.
"""

import os
import sys
from typing import Optional

from .adapters.ffmpeg_engine import FFmpegEngine
from .adapters.fake_playback import FakePlayback
from .adapters.temp_artifact_store import TempArtifactStore
from .repositories.json_project_repository import JsonProjectRepository
from .repositories.settings_repository import FileSettingsRepository
from .services.mix_service import MixService
from .services.i18n_service import I18nService
from .services.profile_service import ProfileService
from .services.project_service import ProjectService
from .workers.cancelable import AudioWorkerManager


def _bundled_resources_dir() -> Optional[str]:
    """Directorio `resources/` del bundle (D5) si la app está empaquetada.

    En una distribución PyInstaller `--onedir`, `resources/` vive al lado del
    ejecutable; en desarrollo (no congelado) no hay bundle y se usa el PATH.
    """
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "resources")
    return None


def _build_playback():
    """Preview con QtMultimedia si está disponible; fake en modo núcleo (SPEC006)."""
    try:
        from .adapters.qt_playback import QtPlayback  # noqa: PLC0415

        return QtPlayback()
    except Exception:  # noqa: BLE001 - headless / sin PySide6
        return FakePlayback()


def build(
    config_dir: Optional[str] = None,
    settings: Optional[FileSettingsRepository] = None,
) -> dict:
    """Compone los servicios principales (Fases 1–3).

    - `FFmpegEngine` real para análisis, render temporal y exportación.
    - `TempArtifactStore` para los temporales privados de preview.
    - Playback QtMultimedia sobre el WAV temporal (fake si no hay Qt).
    """
    settings_repo = settings or FileSettingsRepository(
        os.path.join(config_dir or ".", "settings.json")
    )
    project_repo = JsonProjectRepository()
    profile_service = ProfileService()
    audio_engine = FFmpegEngine(_bundled_resources_dir())
    artifacts = TempArtifactStore()
    playback = _build_playback()
    i18n_service = I18nService(settings_repo)
    project_service = ProjectService(
        project_repo, settings_repo, profile=profile_service, engine=audio_engine
    )
    mix_service = MixService(profile_service, audio_engine, artifacts, playback)
    worker_manager = AudioWorkerManager()
    return {
        "project_service": project_service,
        "profile_service": profile_service,
        "audio_engine": audio_engine,
        "mix_service": mix_service,
        "artifacts": artifacts,
        "playback": playback,
        "worker_manager": worker_manager,
        "i18n_service": i18n_service,
        "settings": settings_repo,
        "language": i18n_service.language,
    }


def main() -> int:
    services = build()
    print("AutoMixer — núcleo.")
    print("Idioma:", services["language"])
    print("Servicios disponibles:", ", ".join(sorted(services.keys())))
    # Si PySide6 está instalado, se abre la ventana principal (UI).
    try:
        from .views.main_window import build_main_window  # noqa: PLC0415
    except Exception:
        return 0
    from PySide6 import QtWidgets  # noqa: PLC0415

    app = QtWidgets.QApplication(sys.argv)
    win = build_main_window(services)
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
