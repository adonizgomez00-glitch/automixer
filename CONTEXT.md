# AutoMixer — Contexto de continuidad

**Estado:** MVP + mejoras post-MVP (91/91 pruebas OK). **Última actualización:** 2026-09-09.

## Instrucción para la próxima sesión

Leer `agent.md`, `ARCHITECTURE.md`, `CONTEXT.md` y `docs/specs/`. Las Fases 1–4 (MVP) están completadas. Se agregaron mejoras post-MVP en la sesión del 2026-09-09.

## Producto

App local de escritorio Python/GUI para una canción por proyecto. Importa stems MP3/FLAC/WAV; **auto-detección de tipo desde nombre de archivo** (drums→Batería, vocals→Voz, bass→Bajo, etc.). Flujo: importar → (asignar tipo si es necesario) → elegir género → **Mezclar** → vista previa → **Exportar**.

## Mejoras post-MVP (sesión 2026-09-09)

### Selector de género en la UI
- `QComboBox` con Pop/Rock/Hip Hop en la barra superior (`src/views/main_window.py`).
- Al cambiar género se llama a `ProjectService.change_genre()` que restablece ganancias al perfil del nuevo género.
- El combo se sincroniza al crear/abrir proyecto y se deshabilita si no hay proyecto activo.

### Barra de progreso para Mezclar/Exportar
- `QProgressBar` en la parte inferior de la ventana.
- Mix y Export se ejecutan asíncronos via `AudioWorkerManager.start()` en hilo de fondo.
- `_set_busy()` bloquea todos los controles interactivos durante el procesamiento.
- `_set_idle()` restaura la GUI al completar (o al fallar).
- `_update_progress()` despacha actualizaciones al hilo principal via `QTimer.singleShot`.

### Slider de volumen con indicadores dB/LUFS/TruePeak
- Slider de volumen −60 a +12 dB en la barra de reproducción.
- Etiqueta `dB` que muestra el valor actual del slider.
- Etiqueta **LUFS** que muestra el target de normalización del género actual (ej: Pop −14.0, Rock −12.0, Hip Hop −13.0).
- Etiqueta **True Peak** fija en −1.0 dB (valor de los perfiles de normalización).
- `_update_normalization_display()` lee la normalización desde `ProfileService` y se actualiza al cambiar género.

### Auto-detección de tipo de stem desde nombre de archivo
- `src/utils/validators.py:detect_stem_type()` parsea keywords en el nombre: `drums`→bateria, `vocals`→voz, `bass`→bajo, `guitar`→guitarra, `keys`→teclados, `synth`→sintetizadores, `fx`→efectos, `drops`→drops.
- Si no encuentra keyword → `otro` (perfil neutro).
- Al importar stems se auto-asigna el tipo detectado.
- La lista de stems muestra `[Tipo] nombre_archivo`.
- Doble-clic en un stem abre `QInputDialog` para reasignar tipo manualmente.

### Corrección de exportación
- `ExportFormat.WAV_44100_24` y `ExportFormat.MP3_320` (nombres correctos del enum).

### Instaladores automáticos
- `setup.bat` (Windows): auto-instala Python via winget, FFmpeg via winget/descarga, crea venv, instala dependencias, crea acceso directo en escritorio.
- `setup.sh` (Linux): auto-instala Python/FFmpeg via gestor de paquetes (apt/dnf/pacman), instala prerrequisitos PySide6, crea lanzador `.desktop` y `automixer.sh`.

### README.md
- Descripción general, características, requisitos, instalación, ejecución, arquitectura, formatos, géneros, licencia.

### Traducciones (i18n)
- Claves `ui.genre_pop/rock/hip_hop`, `ui.volume`, `ui.lufs`, `ui.true_peak`.
- Claves `stem.type.voz/bateria/bajo/guitarra/teclados/sintetizadores/drops/efectos/otro`.
- Clave `stem.change_type` para el diálogo de reasignación.

## Implementación actual (Fases 1–4 + mejoras)

- **Fase 1 (Base)**: modelos, persistencia `.automixer` (esquema v1), preferencias, worker cancelable, servicio de proyecto, esqueleto UI (U1).
- **Fase 2 (Dominio de mezcla)**:
  - `src/resources/profiles.json`: perfiles D1 (3 géneros × 9 tipos, normalización LUFS/TP incluida).
  - `src/models/mix_profile.py`: `StemProfile` (gain base, paneo ±X alternado, HPF, EQ ≤2 bandas, compresor, makeup).
  - `src/ports/audio.py` (ABC `AudioEngine`) + `src/adapters/fake_audio_engine.py`.
  - `src/services/profile_service.py`: `default_gain`, `apply_defaults`, `pan_for_stem`, `normalization`, `reset_gain`, `reset_stem`.
  - `src/services/alignment_service.py`: referencia, `sync_tempo`/`align_start`, `set_reference`, `set_manual_offset`.
  - `src/services/project_service.py`: `add_stem`, `set_stem_type`, `set_gain`, `valid_stems`, `mix_enabled`, `change_genre`, `reset_stem`.
- **Fase 3 (Audio real)**:
  - `src/adapters/ffmpeg_engine.py`: `FFmpegEngine` (análisis, render, export; FFmpeg sin shell).
  - `src/adapters/temp_artifact_store.py`: temporales privados de preview.
  - `src/adapters/qt_playback.py`/`fake_playback.py`: `QtPlayback` (QtMultimedia) y `FakePlayback`.
  - `src/services/mix_service.py`: `render_preview` (cancelable), `load_preview`, `export` (WAV 44.1/24 y MP3 320k), `close`.
- **Fase 4 (Empaquetado e i18n)**:
  - `src/services/i18n_service.py`: `I18nService` (es/en).
  - `src/i18n/catalogs.py`: catálogos `es`/`en` ampliados.
  - `scripts/build.py`: empaquetado PyInstaller `--onedir` + FFmpeg.
  - `LICENSES.md`: avisos de FFmpeg, códecs, PySide6, Python.
- **Post-MVP**: selector género, progreso async, volumen/dB/LUFS/TruePeak, auto-detección tipo stem, instaladores.

## Decisiones cerradas

- Géneros fijos: Pop (predeterminado), Rock, Hip Hop.
- Tipos: voz, batería, bajo, guitarra, teclados, sintetizadores, drops, efectos, Otro (perfil neutro).
- Auto-detección de tipo desde nombre de archivo con keywords en inglés.
- Volumen por stem: manual, −60 a +12 dB. Paneo, normalización, EQ y compresión automáticos por género/tipo.
- Tempo: referencia batería; si no existe, primer stem. Umbrales D2.
- Salida estéreo termina con el más largo. Exportación WAV 44.1 kHz/24-bit o MP3 320 kbps.
- Linux/Windows; PySide6 + FFmpeg incluido; QtMultimedia para preview; perfiles JSON; UI español/inglés.
- Instaladores automáticos (winget en Windows, apt/dnf/pacman en Linux).

## Arquitectura aprobada

Monolito local: View → Controller → Service → Repository/Port → Adapter. Worker en segundo plano; un trabajo de audio a la vez; inyección manual en `app.py`.

## Archivos relevantes

- `agent.md`: prompt y alcance acordado.
- `ARCHITECTURE.md`: arquitectura aprobada.
- `CONTEXT.md`: este handoff.
- `README.md`: documentación general del proyecto.
- `setup.bat`: instalador automático Windows.
- `setup.sh`: instalador automático Linux.
- `src/utils/validators.py`: `detect_stem_type()` para auto-detección desde nombre.
- `src/views/main_window.py`: UI principal con género, progreso, volumen/dB/LUFS/TruePeak.
