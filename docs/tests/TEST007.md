# TEST007 — Pruebas funcionales: Exportación de mezcla

**Fuente:** `SPEC007` · **Criterios cubiertos:** AC-01 a AC-07 · **Estado:** borrador, sin ejecución · **Fecha:** 2026-08-31

## TEST007-AC-01 — Exportar WAV 44.1 kHz/24-bit

- **Dado** un proyecto exportable.
- **Cuando** el usuario elige formato WAV, carpeta y nombre.
- **Entonces** el sistema crea un archivo WAV de 44.1 kHz y 24 bit en el destino.

## TEST007-AC-02 — Exportar MP3 320 kbps

- **Dado** un proyecto exportable.
- **Cuando** el usuario elige formato MP3, carpeta y nombre.
- **Entonces** el sistema crea un archivo MP3 de 320 kbps en el destino.

## TEST007-AC-03 — No sobrescribir sin confirmación

- **Dado** un destino que ya existe.
- **Cuando** el usuario no confirma la sobrescritura.
- **Entonces** el sistema no modifica el archivo existente.

## TEST007-AC-04 — Sobrescribir con confirmación

- **Dado** un destino que ya existe.
- **Cuando** el usuario confirma la sobrescritura (`export.overwrite_confirmation`).
- **Entonces** el sistema reemplaza el archivo con la exportación nueva.

## TEST007-AC-05 — Cancelar selección de destino no crea archivo

- **Dado** que el usuario cancela el diálogo de destino.
- **Cuando** vuelve al proyecto.
- **Entonces** no se crea ningún archivo de exportación.

## TEST007-AC-06 — Fallo de escritura conserva el proyecto

- **Dado** un fallo de escritura en el destino.
- **Cuando** ocurre durante la exportación.
- **Entonces** el sistema muestra `export.failed` y conserva el proyecto.

## TEST007-AC-07 — Cerrar no elimina archivos exportados

- **Dado** un archivo exportado correctamente.
- **Cuando** el usuario cierra el proyecto o la aplicación.
- **Entonces** el sistema no elimina ese archivo.

## Notas

- La cancelación durante exportación se prueba en `TEST009` (AC-05).