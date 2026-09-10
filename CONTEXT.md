# AutoMixer — Contexto de continuidad

**Estado:** Fases 1–4 implementadas (76/76 pruebas OK) — MVP completo. **Última actualización:** 2026-09-01.

## Instrucción para la próxima sesión

Leer `agent.md`, `ARCHITECTURE.md`, `CONTEXT.md`, `LIVE_CONTEXT.md` (checkpoint SAQI) y `docs/specs/`. Las Fases 1–4 (MVP) están completadas y cerradas por sus pruebas. No hay fase pendiente dentro del MVP; cualquier extensión requiere aprobación explícita del usuario.

## Producto

App local de escritorio Python/GUI para una canción por proyecto. Importa stems MP3/FLAC/WAV mediante drag & drop; asignación de tipo solo manual, varios stems por tipo. Flujo: agregar → asignar → elegir género → **Mezclar** → vista previa → **Exportar**.

## Implementación actual

- **Fase 1 (Base)**: modelos, persistencia `.automixer` (esquema v1), preferencias, worker cancelable, servicio de proyecto, esqueleto UI (U1).
- **Fase 2 (Dominio de mezcla)**:
  - `src/resources/profiles.json`: perfiles D1 (3 géneros × 9 tipos, normalización LUFS/TP incluida).
  - `src/models/mix_profile.py`: `StemProfile` (gain base, paneo ±X alternado, HPF, EQ ≤2 bandas, compresor, makeup).
  - `src/ports/audio.py` (ABC `AudioEngine`) + `src/adapters/fake_audio_engine.py` (resultados inyectables; el adapter FFmpeg real llega en Fase 3).
  - `src/services/profile_service.py`: `default_gain`, `apply_defaults`, `pan_for_stem`, `normalization`, `reset_gain`, `reset_stem`.
  - `src/services/alignment_service.py`: referencia (batería → primer stem), `sync_tempo`/`align_start` con umbrales D2, `set_reference` (conserva desfase manual), `set_manual_offset`.
  - `src/services/project_service.py`: `add_stem` (valida extensión/existencia/decodificación), `set_stem_type`, `set_gain` (−60..+12), `valid_stems`, `mix_enabled`, `change_genre` (restablece ganancias, conserva correcciones), `reset_stem` (Restablecer completo).
  - `src/app.py:build()` inyecta `ProfileService` y motor de audio en `ProjectService`.
- **Fase 3 (Audio real)**:
  - `src/ports/audio.py`+`src/adapters/ffmpeg_engine.py`: `FFmpegEngine` (análisis envolvente/onsets D2, `render_mix`, `export_mix`; FFmpeg sin shell).
  - `src/ports/artifacts.py` + `src/adapters/temp_artifact_store.py`: `ArtifactStore`/`TempArtifactStore` (temporales privados de preview).
  - `src/ports/playback.py` + `src/adapters/qt_playback.py`/`fake_playback.py`: `Playback`/`QtPlayback` (QtMultimedia) y `FakePlayback` (tests).
  - `src/services/mix_service.py`: `render_preview` (cancelable, conserva preview previa si falla), `load_preview`, `export` (WAV 44.1/24 y MP3 320k; confirmación de sobrescritura), `close` (limpieza de temporales).
  - `src/app.py:build()` compone `MixService` con `FFmpegEngine` real, `TempArtifactStore`, `QtPlayback`/`FakePlayback` y `AudioWorkerManager`.
- **Fase 4 (Empaquetado e i18n)**:
  - `src/services/i18n_service.py`: `I18nService` — resolución de idioma (preferencia → sistema es/en → español D6), selector manual que persiste (`set_language`), `tr()` para textos localizados.
  - `src/i18n/catalogs.py`: catálogos `es`/`en` ampliados con claves de UI y `PRODUCT_DEFAULT_LANGUAGE="es"`.
  - `src/views/main_window.py`: `MainWindow` con selector de idioma (diálogo Preferencias, U8) que retraduce la UI y persiste (SPEC010 AC-05); FFmpeg del bundle en `resources/` (PyInstaller).
  - `src/app.py:build()` inyecta `I18nService` y resuelve el directorio de recursos empaquetados.
  - `scripts/build.py`: empaquetado PyInstaller `--onedir` + copia de FFmpeg a `resources/` + `LICENSES.md`.
  - `scripts/release_check.py`: gate de release (rechaza paquete sin `LICENSES.md`, AC-07).
  - `LICENSES.md`: avisos de FFmpeg, códecs (LAME), PySide6 y Python.

## Decisiones cerradas

- Géneros fijos: Pop (predeterminado), Rock, Hip Hop; cambiar género regenera la mezcla y restablece ganancias al perfil (las correcciones de tempo/alineación se conservan).
- Tipos: voz, batería, bajo, guitarra, teclados, sintetizadores, drops, efectos, Otro (perfil neutro).
- Volumen por stem: manual, −60 a +12 dB. Paneo, normalización, EQ y compresión automáticos por género/tipo.
- Tempo: referencia batería; si no existe, primer stem. Desfase manual ±ms prioridad solo en ese stem. Umbrales D2: tempo `conf ≥ 0.80` y `ratio ∈ [0.75, 1.33]`; alineación `conf ≥ 0.85` y `|desfase| ≤ 2000 ms`; por debajo, advertir y no alterar. **Restablecer** vuelve al perfil (ganancia + correcciones).
- Stems importan en 0; salida estéreo termina con el más largo. Un stem válido habilita Mezclar. Nunca modificar originales.
- Vista previa temporal con reproducir/pausar/detener/posición/volumen; temporales se eliminan al cerrar. Exportación WAV 44.1 kHz/24-bit o MP3 320 kbps.
- Linux/Windows; PySide6 + FFmpeg incluido; QtMultimedia para preview; perfiles JSON; UI español/inglés.

## Arquitectura aprobada

Monolito local: View → Controller → Service → Repository/Port → Adapter. Worker en segundo plano; un trabajo de audio a la vez; inyección manual en `app.py`. Ver detalles, Mermaid, puertos y riesgos en `ARCHITECTURE.md`.

## Especificación funcional completada

Las 10 specs (SPEC001–SPEC010) y las decisiones D1–D6 resueltas (`docs/specs/DECISIONS.md`).

Implementación: **Fases 1–4 completadas** (76 pruebas) — MVP completo. Ver `LICENSES.md` y `scripts/` para el empaquetado y el gate de licencias.

## Archivos relevantes

- `agent.md`: prompt y alcance acordado.
- `ARCHITECTURE.md`: arquitectura aprobada.
- `CONTEXT.md`: este handoff.
- `LIVE_CONTEXT.md`: checkpoint SAQI con artefactos y gates verificados.

