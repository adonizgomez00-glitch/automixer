# AutoMixer — Estado del proyecto

**Fase:** Fase 4 (Empaquetado e i18n) completada · **Estado:** MVP completo · **Código:** `src/` + `tests/` (venv).

## Hecho

- **Fase 1 implementada**: modelos, persistencia `.automixer`, preferencias, worker cancelable, servicio de proyecto y esqueleto UI (U1). 16 pruebas pasando (TEST001, TEST008, TEST009).
- **Fase 2 implementada**: import/validación de stems (decodificación inyectable), perfiles D1 como JSON (`profiles.json` + `ProfileService`), ganancia manual con rango, `mix_enabled`, sincronización de tempo y alineación con umbrales D2 (`AlignmentService` + puerto `AudioEngine` con `FakeAudioEngine`), cambio de género con restablecimiento de ganancias y `Restablecer` completo. Composition root (`app.py`) cableado. 39 pruebas pasando (TEST001–004, TEST008, TEST009).
- **Fase 3 implementada**: adapter FFmpeg real (`FFmpegEngine`), render temporal en `MixService.render_preview()` con cancelación y limpieza de parciales, preview con `QtMultimedia` (`QtPlayback`) y `FakePlayback` para tests, exportación WAV 44.1/24 y MP3 320k (`MixService.export()`), confirmación de sobrescritura, conserva proyecto en fallo, no elimina exportados al cerrar. 62 pruebas pasando (TEST001–009).
- **Fase 4 implementada**: `I18nService` (resolución preferencia → sistema → español D6, selector manual que persiste), catálogos `es`/`en` ampliados, selector de idioma en la UI (Preferencias, U8), scripts de empaquetado (`scripts/build.py`, PyInstaller `--onedir`), gate de release (`scripts/release_check.py`, AC-07) y `LICENSES.md` con avisos. 76 pruebas pasando (TEST001–010).
- `agent.md`, `ARCHITECTURE.md`, `CONTEXT.md`, `LIVE_CONTEXT.md` (checkpoint SAQI), `PROJECT_STATE.md`.
- `docs/specs/` (10 specs + DECISIONS D1–D6), `docs/tests/` (68 casos), `docs/design/UI_DECISIONS.md` (U1–U8).

## En curso / próximo

- MVP completo (Fases 1–4). Siguiente (fuera del MVP acordado): cableado completo del flujo UI↔servicios (Mezclar/Exportar/preview conectados a `MixService`), validación del bundle en Windows y ampliación de perfiles i18n si se desea.

## Estrategia de implementación (acordada, 2026-08-31)

Implementación **híbrida en 4 fases incrementales**, cada fase cerrada por sus pruebas (`docs/tests/`) antes de seguir:

1. **Fase 1 — Base** (SPEC001, SPEC008, SPEC009): ✅ completada.
2. **Fase 2 — Dominio de mezcla** (SPEC002, SPEC003, SPEC004): ✅ completada.
3. **Fase 3 — Audio** (SPEC005, SPEC006, SPEC007): ✅ completada.
4. **Fase 4 — Empaquetado e i18n** (SPEC010 + licencias): ✅ completada.

## Riesgos pendientes

No quedan riesgos derivados de las decisiones; permanecen los técnicos de arquitectura (CPU/duración de render, calidad de sincronización/alineación con análisis real —en Fase 2 validado solo con umbrales— y licencias FFmpeg).
