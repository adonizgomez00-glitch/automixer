---
spec_id: "SPEC007"
version: "0.1.0"
status: "draft"
title: "Exportacion de mezcla"
created: "2026-08-31"
updated: "2026-08-31"
related_specs: ["SPEC005", "SPEC009"]
tags: ["export", "wav", "mp3"]
---

# SPEC007: Exportacion de mezcla

## Problema que se quiere resolver

El usuario necesita generar un archivo final de la mezcla en un formato comun, con control sobre destino y confirmacion antes de sobrescribir.

## Contexto de uso

Despues de preparar una mezcla, el usuario pulsa `Exportar`, elige carpeta, nombre y formato. AutoMixer renderiza el resultado final con FFmpeg.

## Objetivo

Dado un proyecto con stems validos y destino confirmado, el sistema exporta la mezcla final como WAV 44.1 kHz/24-bit o MP3 320 kbps sin modificar archivos originales.

## Alcance

### Incluye

- Seleccionar carpeta y nombre de salida.
- Elegir WAV 44.1 kHz/24-bit.
- Elegir MP3 320 kbps.
- Confirmar sobrescritura si el destino ya existe.
- Mostrar progreso y permitir cancelacion.
- Conservar archivos exportados al cerrar proyecto o aplicacion.

### No incluye

- Exportacion por lotes.
- Otros formatos.
- Subida a servicios externos.
- Normalizacion/loudness configurable por usuario.
- Metadatos avanzados ID3.

## Comportamiento esperado

### Flujo principal

1. El usuario pulsa `Exportar`.
2. El sistema solicita carpeta, nombre y formato.
3. Si el destino existe, el sistema pide confirmacion.
4. El sistema renderiza la mezcla final.
5. Al terminar, el archivo queda en el destino seleccionado.

### Flujos alternativos / edge cases

- Usuario cancela el dialogo: no se exporta nada.
- Destino existente sin confirmacion: no se sobrescribe (`export.overwrite_confirmation`).
- Fallo de escritura: se muestra error (`export.failed`) y se conserva el proyecto.
- Cancelacion durante exportacion: se detiene el trabajo y se limpia salida parcial si pertenece a la operacion actual.

## Criterios de aceptacion

- AC-01: Dado un proyecto exportable, cuando el usuario elige WAV, entonces el sistema crea un archivo WAV 44.1 kHz/24-bit en el destino.
- AC-02: Dado un proyecto exportable, cuando el usuario elige MP3, entonces el sistema crea un archivo MP3 320 kbps en el destino.
- AC-03: Dado un destino existente, cuando el usuario no confirma sobrescritura, entonces el sistema no modifica el archivo existente.
- AC-04: Dado un destino existente, cuando el usuario confirma sobrescritura, entonces el sistema reemplaza el archivo con la exportacion nueva.
- AC-05: Dado que el usuario cancela seleccion de destino, cuando vuelve al proyecto, entonces no se crea archivo de exportacion.
- AC-06: Dado un fallo de escritura, cuando ocurre durante exportacion, entonces el sistema muestra error y conserva el proyecto.
- AC-07: Dado un archivo exportado correctamente, cuando el usuario cierra el proyecto, entonces el sistema no elimina ese archivo.

## Restricciones

- Tecnicas: exportacion mediante FFmpeg incluido e invocado sin shell.
- Negocio: formatos limitados al MVP.
- Seguridad: confirmar antes de sobrescribir y limpiar solo salidas parciales propias.

## Notas

- El texto exacto de confirmacion de sobrescritura esta definido en la decision D3 (`export.overwrite_confirmation`, `docs/specs/DECISIONS.md`).

