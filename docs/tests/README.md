# AutoMixer — Pruebas funcionales (índice)

**Estado:** borrador, sin ejecución · **Fecha:** 2026-08-31 · **Base:** `docs/specs/SPEC00x.md`, `docs/specs/DECISIONS.md`

Cada `SPEC00x` define criterios de aceptación (AC). Este directorio los convierte en casos **Given / When / Then** (Dado / Cuando / Entonces) para convertirlos después en pruebas automatizables. La ejecución real quedará registrada en `QA_RESULTS.md`.

| Suite | Fuente | Función | Casos |
|---|---|---|---|
| `TEST001.md` | `SPEC001` | Gestión de proyecto local | 5 |
| `TEST002.md` | `SPEC002` | Importación y clasificación manual de stems | 6 |
| `TEST003.md` | `SPEC003` | Perfiles de mezcla y controles por stem | 7 |
| `TEST004.md` | `SPEC004` | Sincronización de tempo y alineación temporal | 8 |
| `TEST005.md` | `SPEC005` | Renderizado de mezcla temporal | 7 |
| `TEST006.md` | `SPEC006` | Vista previa y reproducción | 7 |
| `TEST007.md` | `SPEC007` | Exportación de mezcla | 7 |
| `TEST008.md` | `SPEC008` | Persistencia `.automixer` y preferencias | 7 |
| `TEST009.md` | `SPEC009` | Trabajos cancelables, progreso y cierre seguro | 7 |
| `TEST010.md` | `SPEC010` | Internacionalización, empaquetado y licencias | 7 |

Total: **68 casos** (uno por AC).

Convenciones:
- ID de caso: `TEST0XX-AC-0Y`.
- Los mensajes esperados se referencian por clave `msg.*` definida en la decisión D3 (`DECISIONS.md`).
- Un caso solo se marca "ejecutado" con evidencia en `QA_RESULTS.md` o en la herramienta de CI.