# TEST009 — Pruebas funcionales: Trabajos cancelables, progreso y cierre seguro

**Fuente:** `SPEC009` · **Criterios cubiertos:** AC-01 a AC-07 · **Estado:** borrador, sin ejecución · **Fecha:** 2026-08-31

Se probarán contra workers con señales de progreso y servicios que devuelven `Result`.

## TEST009-AC-01 — Iniciar trabajo en segundo plano

- **Dado** que no hay trabajo de audio activo.
- **Cuando** el usuario inicia mezcla o exportación.
- **Entonces** el sistema crea un trabajo cancelable en segundo plano y la UI sigue respondiendo.

## TEST009-AC-02 — El motor reporta avance y la UI muestra progreso

- **Dado** un trabajo activo.
- **Cuando** el motor reporta avance.
- **Entonces** la UI muestra el progreso del trabajo.

## TEST009-AC-03 — Impedir un segundo trabajo simultáneo

- **Dado** un trabajo activo.
- **Cuando** el usuario intenta iniciar otro trabajo de audio.
- **Entonces** el sistema impide la segunda ejecución (acción deshabilitada o rechazo).

## TEST009-AC-04 — Cancelar termina el proceso y conserva el proyecto

- **Dado** un trabajo activo.
- **Cuando** el usuario cancela.
- **Entonces** el sistema termina el proceso FFmpeg asociado y conserva el proyecto intacto.

## TEST009-AC-05 — Cancelación limpia solo artefactos del trabajo

- **Dado** un trabajo cancelado.
- **Cuando** termina la cancelación.
- **Entonces** el sistema limpia únicamente los temporales o parciales creados por ese trabajo.

## TEST009-AC-06 — Cerrar durante trabajo pide confirmación

- **Dado** un trabajo activo.
- **Cuando** el usuario intenta cerrar la aplicación.
- **Entonces** el sistema solicita confirmación (`busy.confirm_close`) antes de cancelar y salir.

## TEST009-AC-07 — Fallo externo de FFmpeg se vuelve error de dominio

- **Dado** un fallo externo del proceso FFmpeg.
- **Cuando** el worker lo recibe.
- **Entonces** el servicio devuelve un error de dominio claro y la UI lo muestra (p. ej. `export.failed`, `stem.decode_failed`).

## Notas

- La confirmación de cierre de proyecto se prueba en `TEST001` (AC-04).