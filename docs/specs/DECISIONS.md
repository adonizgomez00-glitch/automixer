# AutoMixer — Registro de decisiones (ADR ligero)

**Propósito:** resolver las decisiones abiertas heredadas de la especificación funcional. Cada entrada fija una decisión, su estado y dónde se aplica en las specs. Fecha base: 2026-08-31.

## D1 — Parámetros de perfiles Pop/Rock/Hip Hop

- **Estado:** resuelta (2026-08-31) · **Aplica en:** `SPEC003` (Anexo A).
- **Decisión:** perfiles fijos como datos JSON generados desde el Anexo A. Normalización final de mezcla: Pop I=−14 LUFS, Rock I=−12 LUFS, Hip Hop I=−13 LUFS; límite TP = −1.0 dBTP en los tres. Por tipo: ganancia base, paneo (± alternado), HPF y hasta 2 bandas EQ, compresión (umbral/ratio/ataque/soltura) y ganancia de recuperación. `otro` usa perfil neutro (sin EQ, sin compresión, sin normalización, paneo 0, ganancia 0).
- **Motivo:** reglas de mezcla coherentes y verificables por género/tipo, mantenidas como datos (no en la UI).

## D2 — Umbrales de fiabilidad para sincronización y alineación

- **Estado:** resuelta (2026-08-31) · **Aplica en:** `SPEC004`.
- **Decisión:** `confidence` = correlación normalizada del análisis (envolvente/onsets) entre stem y referencia, en [0,1].
  - Sincronizar tempo: fiable si `confidence ≥ 0.80` y `ratio tempo ∈ [0.75, 1.33]`.
  - Alinear inicio: fiable si `confidence ≥ 0.85` y `|desfase| ≤ 2000 ms`.
  - Por debajo: advertir (`sync.low_confidence_tempo` / `sync.low_confidence_alignment`) y dejar el stem intacto. El `confidence` se guarda como metadato.
- **Motivo:** preferir advertir antes que alterar; límites físicos evitan correcciones absurdas.

## D3 — Catálogo mínimo de mensajes de validación y error

- **Estado:** resuelta (2026-08-31) · **Aplica en:** `SPEC001`, `SPEC002`, `SPEC003`, `SPEC004`, `SPEC007`, `SPEC008`, `SPEC009`, `SPEC010`.
- **Decisión:** conjunto mínimo de claves `msg.*` necesarias para el flujo del MVP (crear → importar/validar → mezclar/sincronizar → exportar → cierre seguro). Se almacenan en el catálogo i18n separado de la UI; fallback por defecto es inglés. Los placeholders usan `{0}`.

| Clave | Español | English |
|---|---|---|
| `project.name_empty` | El nombre del proyecto no puede estar vacío. | Project name cannot be empty. |
| `project.folder_notwritable` | No se puede escribir en la ubicación seleccionada. | The selected location is not writable. |
| `project.schema_unsupported` | Versión del esquema del proyecto no soportada. | Unsupported project schema version. |
| `stem.format_unsupported` | Formato no soportado: solo MP3, FLAC y WAV. | Unsupported format: only MP3, FLAC and WAV. |
| `stem.decode_failed` | No se puede decodificar el archivo de audio. | Cannot decode the audio file. |
| `stem.not_found` | Stem faltante: localízalo para continuar. | Missing stem: locate it to continue. |
| `stem.gain_out_of_range` | Ganancia fuera de rango (−60 a +12 dB). | Gain out of range (−60 to +12 dB). |
| `sync.low_confidence_tempo` | Sincronización poco fiable (confianza {0}%). Stem sin modificar. | Low-confidence tempo sync ({0}%). Stem left unchanged. |
| `sync.low_confidence_alignment` | Alineación poco fiable (confianza {0}%). Stem sin modificar. | Low-confidence alignment ({0}%). Stem left unchanged. |
| `export.overwrite_confirmation` | El destino ya existe. ¿Sobrescribir? | The destination already exists. Overwrite? |
| `export.failed` | No se pudo exportar la mezcla. | Could not export the mix. |
| `busy.confirm_close` | Hay un trabajo de audio en curso. ¿Cancelar y cerrar? | An audio job is running. Cancel and close? |
| `ffmpeg.not_found` | FFmpeg no está disponible en esta instalación. | FFmpeg is not available in this installation. |

## D4 — Esquema JSON del proyecto `.automixer`

- **Estado:** resuelta (2026-08-31) · **Aplica en:** `SPEC008`.
- **Decisión:** esquema `schema_version: 1`, mínimo por stem: `id`, `path`, `type`, `gain_db` y objeto anidado `corrections` (`tempo_ratio`, `start_offset_ms`, `confidence`, `manual_offset_ms`; cada uno `null` = sin corrección). `reference_stem_id` nulo se deriva al cargar (batería, si no, primer stem). `available` no se persiste: deriva de la existencia/decode del `path` en carga. Escritura atómica `.automixer.tmp` + `os.replace`. Solo se admite la versión 1; fuera de ella, `project.schema_unsupported`.

## D5 — Empaquetado por plataforma y licencias

- **Estado:** resuelta (2026-08-31) · **Aplica en:** `SPEC010`.
- **Decisión:** PyInstaller `--onedir` en Linux y Windows con `ffmpeg`/`ffmpeg.exe` dentro del bundle (`resources/`), verificado al arrancar (`ffmpeg.not_found` si falta). Todo paquete incluye `LICENSES.md` con avisos de FFmpeg, códecs (LAME/LGPL), PySide6 (LGPLv3) y Python (PSF). Gate de release: sin `LICENSES.md` el paquete se rechaza. Sin scripts de build ni variable de entorno en el MVP.

## D6 — Idioma predeterminado

- **Estado:** resuelta (2026-08-31) · **Aplica en:** `SPEC010`.
- **Decisión:** el idioma predeterminado de producto para sistemas cuyo idioma no sea espanol/ingles es **espanol** (paso 4 del flujo principal y AC-04).

## Pendientes

Ninguna: D1–D6 resueltas.