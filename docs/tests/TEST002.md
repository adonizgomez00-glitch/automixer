# TEST002 — Pruebas funcionales: Importación y clasificación manual de stems

**Fuente:** `SPEC002` · **Criterios cubiertos:** AC-01 a AC-06 · **Estado:** borrador, sin ejecución · **Fecha:** 2026-08-31

## TEST002-AC-01 — Importar archivo válido como stem

- **Dado** un archivo MP3, FLAC o WAV existente y decodificable.
- **Cuando** el usuario lo importa.
- **Entonces** el sistema lo agrega como stem válido en el proyecto, con inicio en 0 ms y disponible para clasificar.

## TEST002-AC-02 — Rechazo por extensión no soportada

- **Dado** un archivo con extensión no soportada (p. ej. `.ogg`, `.aiff`).
- **Cuando** el usuario lo importa junto a otros válidos.
- **Entonces** el archivo se rechaza sin afectar a los demás y se muestra `stem.format_unsupported`.

## TEST002-AC-03 — Rechazo por archivo no decodificable

- **Dado** un archivo con extensión soportada pero no decodificable por FFmpeg.
- **Cuando** el usuario lo importa.
- **Entonces** el sistema informa el error `stem.decode_failed` y no lo marca como válido.

## TEST002-AC-04 — Asignación manual de tipo

- **Dado** un stem importado.
- **Cuando** el usuario selecciona un tipo manual (voz, batería, bajo, guitarra, teclados, sintetizadores, drops, efectos u otro).
- **Entonces** el sistema guarda ese tipo en el proyecto y acepta varios stems por tipo.

## TEST002-AC-05 — Habilitar Mezclar con al menos un stem válido

- **Dado** al menos un stem válido.
- **Cuando** el proyecto se actualiza.
- **Entonces** la acción `Mezclar` queda habilitada.

## TEST002-AC-06 — Mantener Mezclar deshabilitada sin stems válidos

- **Dado** cero stems válidos en el proyecto.
- **Cuando** el proyecto se actualiza.
- **Entonces** la acción `Mezclar` permanece deshabilitada.

## Notas

- Los estados de `Mezclar` se prueban también en `TEST005` (AC-02).
- Los perfiles que usan el tipo se prueban en `TEST003`.