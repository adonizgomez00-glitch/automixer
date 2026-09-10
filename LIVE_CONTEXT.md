# AutoMixer — Contexto vivo (SAQI) · Checkpoint Fase 2

**Metodología:** SAQI (Save / Acquire / Question / Inspire). **Fecha:** 2026-08-31.
**Estado:** Fase 2 — Dominio de mezcla **COMPLETADA** (39/39 pruebas OK).
**Siguiente:** Fase 3 — Audio real (SPEC005/006/007: render, preview, exportación FFmpeg).

---

## 1. Saved — Inventario de contexto externo

> **Jerarquía de fuentes (regla fija):** ante cualquier conflicto entre una skill o recomendación
> genérica y un documento del proyecto (`ARCHITECTURE.md`, `agent.md`, specs, `DECISIONS.md`),
> **prevalece el documento del proyecto**. Verificado en Fase 2: la implementación cumple
> `ARCHITECTURE.md` sin desviaciones; las skills tipo A se usan solo como checklist.

| Fuente | Ruta externa | Uso en contexto vivo |
|:-------|:--------------|:---------------------|
| Especificación funcional | `docs/specs/SPEC001.md` … `SPEC010.md` | Fuente de AC y restricciones |
| Decisiones (ADR ligero) | `docs/specs/DECISIONS.md` (D1–D6) | D1, D2, D3, D4 aplicados |
| Contexto de continuidad | `CONTEXT.md` | Handoff entre sesiones |
| Estado del proyecto | `PROJECT_STATE.md` | Fases y estrategia |
| Prompt acordado | `agent.md` | Alcance y exclusiones |
| Pruebas funcionales | `docs/tests/TEST001–010.md` | Gate por fase (68 casos) |
| Arquitectura aprobada | `ARCHITECTURE.md` | Layout puertos/adaptadores |
| Diseño UI | `docs/design/UI_DECISIONS.md` (U1–U8) | Cableado UI (Fase 3/4) |

**Decisiones aplicadas en Fase 2:**
- **D1** (`SPEC003` Anexo A): perfiles JSON por género×tipo. Normalización: Pop I=−14 LUFS,
  Rock I=−12, Hip Hop I=−13 (TP=−1.0 dBTP). Neutral `otro`. Paneo ±X alternado (−X si un solo stem).
- **D2** (`SPEC004`): tempo fiable `conf ≥ 0.80` y `ratio ∈ [0.75, 1.33]`; alineación fiable
  `conf ≥ 0.85` y `|desfase| ≤ 2000 ms`; bajo umbral: advertir y dejar el stem intacto.
- **D3**: `stem.decode_failed`, `stem.gain_out_of_range`, `sync.low_confidence_*`.
- **D4**: `corrections` (`tempo_ratio`, `start_offset_ms`, `confidence`, `manual_offset_ms`).

---

## 2. Acquire — Brechas cubiertas por Fase 2

| Brecha | Solución implementada |
|:-------|:----------------------|
| Decodificación (`stem.decode_failed`) | Puerto `AudioEngine.is_decodable` inyectable; fake en Fase 2 |
| Perfiles D1 inexistentes | `resources/profiles.json` + `models/mix_profile.py` + `services/profile_service.py` |
| Clasificación manual + defaults | `ProjectService.set_stem_type` (aplica ganancia base del perfil) |
| `Mezclar` habilitada | `ProjectService.mix_enabled` / `valid_stems` |
| Sincronización/alineación D2 | Puertos `analyze_tempo`/`analyze_alignment` + `services/alignment_service.py` |
| `Restablecer` completo | `ProjectService.reset_stem` → `ProfileService.reset_stem` (ganancia+correcciones) |
| Cambio de género | `ProjectService.change_genre` → `ProfileService.reset_gain` (conserva correcciones) |
| Composition root sin dominio | `app.py:build()` inyecta `ProfileService` + motor de audio |

---

## 3. Question — Decisiones derivadas verificadas

| Pregunta | Respuesta aplicada |
|:---------|:-------------------|
| ¿JSON o código para perfiles? | JSON (`src/resources/profiles.json`), generado del Anexo A. |
| ¿Cómo se calcula el paneo alternado? | Magnitud ±X del perfil; −X con un solo stem del tipo; −/+ por posición. |
| ¿El motor FFmpeg se inyecta? | Sí: ABC `AudioEngine` + `FakeAudioEngine` en Fase 2; adapter FFmpeg en Fase 3. |
| ¿Qué recibe `otro`? | Perfil neutro: gain 0, pan 0, sin EQ/compresión/HPF/normalización. |
| ¿Cambiar género borra correcciones? | No: `change_genre` solo restablece ganancias (dependen del audio, no del género). |
| ¿Alinear la referencia a sí misma? | Error `project.no_valid_reference` (un stem no se alinea a sí mismo). |
| ¿`Restablecer` limpia qué? | Ganancia al perfil + `tempo_ratio`, `start_offset_ms`, `confidence`, `manual_offset_ms`. |

---

## 4. Inspire — Artefactos creados (Fase 2)

**Modelos y datos**
- `src/resources/profiles.json` — 3 géneros × 9 tipos desde Anexo A (D1), normalización incluida.
- `src/models/mix_profile.py` — `EqBand`, `Compressor`, `StemProfile`, `MixNormalization`, `GenreProfile`.

**Puertos y adaptadores**
- `src/ports/audio.py` — ABC `AudioEngine`: `analyze_tempo`, `analyze_alignment`, `is_decodable`.
- `src/adapters/fake_audio_engine.py` — motor fake determinista con resultados inyectables.

**Servicios**
- `src/services/profile_service.py` — carga JSON, `default_gain`, `apply_defaults`, `pan_for_stem`,
  `normalization`, `reset_gain` (cambio de género) y `reset_stem` (Restablecer completo).
- `src/services/alignment_service.py` — `primary_reference`/`reference_for`/`set_reference`,
  `sync_tempo`/`align_start` (umbrales D2), `set_manual_offset`; sin `reset` (es de perfil).
- `src/services/project_service.py` — ampliado: `valid_stems`, `mix_enabled`, `add_stem` con
  decodificación, `set_stem_type`, `set_gain`, `change_genre`, `reset_stem`.

**Composition root y pruebas**
- `src/app.py:build()` — inyecta perfil y motor de audio (fake hasta Fase 3).
- `tests/test_stems.py` (TEST002, 6 casos), `tests/test_profiles.py` (TEST003, 7 casos),
  `tests/test_alignment.py` (TEST004, 10 casos: AC-05 dividido en confianza/ratio/desfase).

**Estrategia para Fase 3 (audio real)**
1. `src/adapters/ffmpeg_engine.py`: implementar `AudioEngine` con FFmpeg (`ffprobe` para tempo/onsets).
2. Puertos de render/export: `render_temp` (worker cancelable, WAV temporal), `export_mix` (WAV/MP3).
3. Preview: QtMultimedia sobre el WAV temporal; borrar temporales al cerrar.
4. Sustituir `FakeAudioEngine` por el adapter FFmpeg en `app.py`; el fake queda para tests.

---

## 5. Acceptance gates verificados (evidencia)

- **TEST002 (6/6)**: importar válido, rechazo de extensión, rechazo no-decodificable (fake),
  tipo manual con duplicados, `mix_enabled` True/False.
- **TEST003 (7/7)**: género inicial Pop, perfil aplicado (gain base + EQ + normalización),
  neutro `otro`, gain en rango, gain fuera de rango, cambio de género restablece ganancias
  (conserva correcciones), `Restablecer` vuelve al perfil.
- **TEST004 (10/10)**: referencia batería, referencia primer stem, corrección de tempo,
  corrección de inicio, baja confianza (confianza, ratio fuera de rango, desfase > 2 s),
  cambio de referencia conserva desfase manual, batería añadida se adapta, `Restablecer` limpia.
- **Suite completa: 39/39 OK** (`python3 -m unittest discover -s tests`), sin regresiones de Fase 1.

Resultados registrados también en `QA_RESULTS.md`.



--- CHECKPOINT FASE 3 (SAQI) ---
Modelo anterior: implementó SPEC005/006/007, FFmpegEngine, MixService, ports audio/playback/artifacts, tests test_render/test_playback/test_export. Prioridad ARCHITECTURE.md confirmada. Suite 62/62 OK.

--- CHECKPOINT FASE 3 COMPLETADO ---
- **62/62 pruebas OK** (`python3 -m unittest discover -s tests`)
- **SPEC005 (render temporal)**: `MixService.render_preview()` + `FFmpegEngine.render_mix()` con cancelación y limpieza de parciales
- **SPEC006 (vista previa)**: `FakePlayback` (tests) + `QtPlayback` (UI real); `MixService.load_preview()`
- **SPEC007 (exportación)**: `MixService.export()` + `FFmpegEngine.export_mix()` WAV 44.1/24 y MP3 320k; confirmación de sobrescritura, conserva proyecto en fallo, no elimina exportados al cerrar
- **Composition root** (`app.py`): `FFmpegEngine` real + `TempArtifactStore` + `QtPlayback`/`FakePlayback` + `AudioWorkerManager`
- **Parser RIFF robusto** en `FakePlayback._probe_duration_ms()` (busca chunk `data`, ignora LIST/INFO)
- Fase 3 cerrada por TEST005/006/007

--- PRÓXIMA SESIÓN: FASE 4 ---
- **Fase 4 — Empaquetado e i18n** (SPEC010 + licencias): UI español/inglés y PyInstaller (Linux/Windows). Ver `TEST010` y el gate de licencias.
- **No iniciar Fase 4 sin aprobación explícita** del usuario ("implementar fase 4").
- Archivos clave: `docs/specs/SPEC010.md`, `docs/tests/TEST010.md`, `src/i18n/`, `src/views/main_window.py`

--- CHECKPOINT FASE 4 COMPLETADO (2026-09-01) ---
- **76/76 pruebas OK** (`python3 -m unittest discover -s tests`)
- **SPEC010 (i18n + empaquetado + licencias)**:
  - `I18nService` (`src/services/i18n_service.py`): resolución preferencia→sistema (`es`/`en`)→español (D6); `set_language` persiste vía `SettingsRepository` y retrae texto (AC-01..05); `detect_system_language`/`_normalize`.
  - Catálogos `es`/`en` ampliados con claves de UI y `PRODUCT_DEFAULT_LANGUAGE="es"` (fallback de catálogo sigue siendo `en`, D3).
  - `src/views/main_window.py` → `MainWindow`: selector de idioma en Preferencias (U8) que retraduce la UI; `src/app.py:build()` inyecta `I18nService` y resuelve FFmpeg del bundle (PyInstaller `frozen`) o PATH.
  - `scripts/build.py`: PyInstaller `--onedir` + copia de FFmpeg a `resources/` + `LICENSES.md`; `scripts/release_check.py`: gate (rechaza sin `LICENSES.md`, AC-07; valida FFmpeg en `resources/`, AC-06).
  - `LICENSES.md` con avisos de FFmpeg, LAME (códecs), PySide6 y Python.
  - Build real validado: `dist/automixer` con FFmpeg + `LICENSES.md` (gate OK).
- Fase 4 cerrada por TEST010.

--- MVP COMPLETO (Fases 1–4) ---
- 76 pruebas OK, build PyInstaller validado, gate de licencias OK.
- Fuera del MVP acordado: cableado completo UI↔`MixService` (Mezclar/Exportar/preview con botones reales que usan los servicios), validación del bundle en Windows y ampliación de i18n. Requiere aprobación explícita.
