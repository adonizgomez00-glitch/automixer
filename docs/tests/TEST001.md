# TEST001 — Pruebas funcionales: Gestión de proyecto local

**Fuente:** `SPEC001` · **Criterios cubiertos:** AC-01 a AC-05 · **Estado:** borrador, sin ejecución · **Fecha:** 2026-08-31

Cada caso se redacta en Given/When/Then (Dado/Cuando/Entonces). Se convertirán en pruebas automatizables contra el `ProjectRepository` y servicios con puertos falsos al implementar (<code>ARCHITECTURE.md</code>).

## TEST001-AC-01 — Creación de proyecto con género Pop

- **Dado** un nombre de proyecto válido y una ubicación escribible.
- **Cuando** el usuario crea el proyecto.
- **Entonces** el sistema crea un proyecto activo con `genre = "pop"` (criterio heredado de SPEC003 AC-01) y lo deja disponible para importar stems.

## TEST001-AC-02 — Rechazo por nombre vacío

- **Dado** un nombre de proyecto vacío.
- **Cuando** el usuario intenta crear el proyecto.
- **Entonces** el sistema no crea el proyecto y muestra el mensaje `project.name_empty`.

## TEST001-AC-03 — Rechazo por ubicación no escribible

- **Dado** una ubicación sin permisos de escritura.
- **Cuando** el usuario intenta crear el proyecto.
- **Entonces** el sistema no crea el proyecto y muestra el mensaje `project.folder_notwritable`.

## TEST001-AC-04 — Cierre con trabajo activo pide confirmación

- **Dado** un proyecto con un trabajo de audio en curso.
- **Cuando** el usuario intenta cerrar el proyecto.
- **Entonces** el sistema solicita confirmación (`busy.confirm_close`) y cancela el trabajo antes de salir.

## TEST001-AC-05 — Cierre limpia solo temporales propios

- **Dado** un proyecto sin trabajo activo.
- **Cuando** el usuario cierra el proyecto.
- **Entonces** el sistema limpia solo los temporales creados por AutoMixer y conserva los archivos fuente y exportados.

## Notas

- La cancelación de trabajos se prueba en `TEST009`.
- El esquema y el guardado se prueban en `TEST008`.