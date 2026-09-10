# AutoMixer — Núcleo (Fases 1–4)

Estructura del código según `ARCHITECTURE.md` (monolito MVC local):

```
src/
  app.py                          # composición de dependencias (DI manual)
  models/project.py               # MixProject, Stem, correcciones (esquema v1, D4)
  models/mix_profile.py           # StemProfile (D1) y EqBand
  ports/audio.py                  # contrato AudioEngine (análisis, render, export)
  ports/playback.py               # contrato Playback (preview QtMultimedia)
  ports/artifacts.py              # contrato ArtifactStore (temporales privados)
  ports/repositories.py           # contratos ProjectRepository, SettingsRepository
  repositories/                   # JSON .automixer atómico + preferencias
  adapters/ffmpeg_engine.py       # AudioEngine real con FFmpeg (Fase 3)
  adapters/qt_playback.py         # Playback QtMultimedia (Fase 3)
  adapters/fake_audio_engine.py   # AudioEngine fake inyectable (tests)
  adapters/fake_playback.py       # Playback de estado para tests (Fase 3)
  adapters/temp_artifact_store.py # ArtifactStore de temporales (Fase 3)
  services/project_service.py     # crear/guardar/cargar/cerrar/reubicar stem (SPEC001/008)
  services/profile_service.py     # perfiles D1 desde resources/profiles.json (SPEC003)
  services/alignment_service.py   # tempo/alineación con umbrales D2 (SPEC004)
  services/mix_service.py         # render/load_preview/export/close (SPEC005/006/007)
  services/i18n_service.py        # idioma: preferencia→sistema→español (SPEC010, D6)
  workers/cancelable.py           # trabajos cancelables, un audio a la vez (SPEC009)
  i18n/catalogs.py                # mensajes es/en (D3/D6)
  views/main_window.py            # UI 3 zonas (U1) + selector de idioma (U8)

scripts/
  build.py                        # empaquetado PyInstaller --onedir + FFmpeg (Fase 4)
  release_check.py                # gate de release: LICENSES.md + FFmpeg (AC-07)

# Avisos de licencia (obligatorio en el bundle).
LICENSES.md
```

## Cómo ejecutar

```bash
# Entorno
python -m venv .venv && .venv/bin/pip install PySide6 pyinstaller

# Núcleo + chequear composición (sin GUI)
.venv/bin/python -c "from src import app; app.build()"

# Pruebas (no requieren PySide6)
.venv/bin/python -m unittest discover -s tests -v

# Empaquetado y gate de release
.venv/bin/python scripts/build.py
.venv/bin/python scripts/release_check.py dist/automixer
```

## Alcance de las fases 1–4

- Fase 1 (SPEC001, SPEC008, SPEC009): gestión de proyecto local, persistencia `.automixer` y
  preferencias, trabajos cancelables/progreso y esqueleto UI (U1).
- Fase 2 (SPEC002, SPEC003, SPEC004): import/validación de stems con decodificación inyectable,
  perfiles D1 (JSON), ganancia manual, `mix_enabled`, sincronización de tempo y alineación con
  umbrales D2, cambio de género y `Restablecer`.
- Fase 3 (SPEC005, SPEC006, SPEC007): adapter FFmpeg real (`FFmpegEngine`), render temporal
  cancelable (`MixService.render_preview`), preview QtMultimedia (`QtPlayback`) y exportación
  WAV 44.1/24·MP3 320k (`MixService.export`) con confirmación de sobrescritura y conservación
  del proyecto ante fallos.
- Fase 4 (SPEC010): `I18nService` (resolución preferencia→sistema→español), catálogos `es`/`en`,
  selector de idioma en la UI, empaquetado `--onedir` con FFmpeg en `resources/` y gate de
  licencias (`release_check`).
