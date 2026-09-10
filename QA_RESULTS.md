# AutoMixer — QA

**Estado:** Fases 1–4 ejecutadas (2026-09-01) — MVP completo.

## Pruebas documentadas

- `docs/tests/` contiene **68 casos funcionales Given/When/Then** (TEST001–TEST010), uno por cada criterio de aceptación de `SPEC001–SPEC010`.

## Resultados

- **Fase 1 (16/16 OK)**: TEST001 (creación/cierre de proyecto), TEST008 (persistencia y preferencias), TEST009 (worker).
- **Fase 2 (23/23 OK)**:
  - TEST002 — Importación y clasificación (6/6): importar válido, rechazo por extensión, rechazo por no-decodificable (`FakeAudioEngine`), tipo manual con duplicados, `mix_enabled` True/False.
  - TEST003 — Perfiles de mezcla (7/7): género inicial Pop, aplicación de perfil (gain base + EQ + normalización), neutro `otro`, gain en rango, gain fuera de rango, cambio de género restablece ganancias conservando correcciones, `Restablecer` vuelve al perfil.
  - TEST004 — Sincronización/alineación (10/10): referencia batería, referencia primer stem, corrección de tempo, corrección de inicio, baja confianza (confianza baja, ratio fuera de `[0.75, 1.33]`, desfase > 2 s), cambio de referencia conserva desfase manual, batería añadida se adapta a la referencia, `Restablecer` limpia correcciones y desfase.
- **Fase 3 (23/23 OK)**:
  - TEST005 — Render temporal (7/7): inicia con stem válido, deshabilitado sin stems, WAV estéreo reproducible, termina con el stem más largo, aplica ajustes activos (desfase manual con prioridad), fallo conserva preview previa, cancelación limpia parciales.
  - TEST006 — Vista previa (9/9): carga habilita controles, reproducir/pausar/detener, buscar posición, volumen de preview no toca la mezcla, sin temporal no se reproduce (incl. temporal eliminado y carga vía `MixService`).
  - TEST007 — Exportación (7/7): WAV 44.1/24, MP3 320k, no sobrescribir sin confirmación, sobrescribir con confirmación, diálogo cancelado no crea archivo, fallo de escritura conserva proyecto, cerrar no elimina exportados.
- **Fase 4 (14/14 OK)** (TEST010):
  - i18n — resolución de idioma: preferencia guardada se aplica (AC-01), sistema `es`→es (AC-02), sistema `en`→en (AC-03), no soportado→español D6 (AC-04), cambio de idioma persiste y retraduce la UI (AC-05); normalización de códigos de idioma y textos `es`/`en`.
  - Empaquetado/licencias: bundle con FFmpeg en `resources/` y `LICENSES.md` pasa el gate (AC-06); sin `LICENSES.md` se rechaza (AC-07); sin avisos/códecs o sin FFmpeg también se rechaza.
- **Suite completa: 76/76 OK** (`python3 -m unittest discover -s tests`).

## Notas

- La decodificación FFmpeg real (`stem.decode_failed`), el render temporal, la vista previa y la exportación se validan en **Fase 3** con `FFmpegEngine` real (binario del PATH o del bundle) y WAV/MP3 sintéticos.
- El análisis de tempo/alineación con `FFmpegEngine` (envolvente RMS + onsets) ya aplica los umbrales D2 (`confidence ≥ 0.80/0.85`, ratio `[0.75, 1.33]`, `|desfase| ≤ 2000 ms`).
- La **Fase 4** valida i18n (resolución y persistencia de idioma, D6), el empaquetado `--onedir` con FFmpeg en `resources/` y el gate de licencias (`scripts/release_check.py`, AC-07). Build real verificado: `dist/automixer`.
