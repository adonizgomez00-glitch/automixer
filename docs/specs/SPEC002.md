---
spec_id: "SPEC002"
version: "0.1.0"
status: "draft"
title: "Importacion y clasificacion manual de stems"
created: "2026-08-31"
updated: "2026-08-31"
related_specs: ["SPEC003", "SPEC004", "SPEC008"]
tags: ["stems", "import", "validation"]
---

# SPEC002: Importacion y clasificacion manual de stems

## Problema que se quiere resolver

El usuario necesita agregar stems MP3, FLAC y WAV a un proyecto y clasificarlos manualmente por tipo para que los perfiles de mezcla apliquen reglas consistentes.

## Contexto de uso

El productor arrastra archivos de audio locales a la ventana de AutoMixer. La app no detecta automaticamente instrumentos; el usuario asigna el tipo de cada stem.

## Objetivo

Dado al menos un archivo MP3, FLAC o WAV existente y decodificable, el sistema lo agrega al proyecto como stem valido con inicio en 0 y tipo manual asignable.

## Alcance

### Incluye

- Drag and drop de archivos MP3, FLAC y WAV.
- Validacion de extension, existencia y decodificacion.
- Clasificacion manual: voz, bateria, bajo, guitarra, teclados, sintetizadores, drops, efectos u otro.
- Varios stems por tipo.
- Estado de disponibilidad por stem.
- Habilitar `Mezclar` con al menos un stem valido.

### No incluye

- Deteccion automatica de instrumento.
- Copiar audio al proyecto.
- Edicion destructiva del archivo original.
- Importacion por lotes con reglas avanzadas.
- Formatos distintos a MP3, FLAC y WAV.

## Comportamiento esperado

### Flujo principal

1. El usuario arrastra uno o varios archivos al proyecto.
2. El sistema valida cada archivo por separado.
3. El sistema agrega los archivos validos como stems con inicio en 0.
4. El usuario asigna manualmente el tipo de cada stem.
5. Si existe al menos un stem valido, el sistema habilita la mezcla.

### Flujos alternativos / edge cases

- Extension no soportada: el archivo se rechaza sin afectar los demas (`stem.format_unsupported`).
- Archivo inexistente o inaccesible: el stem queda no disponible o no se agrega, segun el momento del fallo (`stem.not_found`).
- Archivo no decodificable por FFmpeg: el sistema informa error y no lo marca como valido (`stem.decode_failed`).
- Varios stems del mismo tipo: el sistema los acepta.

## Criterios de aceptacion

- AC-01: Dado un archivo MP3, FLAC o WAV existente y decodificable, cuando el usuario lo importa, entonces el sistema lo agrega como stem valido con inicio en 0.
- AC-02: Dado un archivo con extension no soportada, cuando el usuario lo importa, entonces el sistema lo rechaza y muestra error de formato.
- AC-03: Dado un archivo no decodificable, cuando el usuario lo importa, entonces el sistema lo rechaza y muestra error de decodificacion.
- AC-04: Dado un stem importado, cuando el usuario selecciona un tipo manual, entonces el sistema guarda ese tipo en el proyecto.
- AC-05: Dado al menos un stem valido, cuando el proyecto se actualiza, entonces el sistema habilita la accion `Mezclar`.
- AC-06: Dado cero stems validos, cuando el proyecto se actualiza, entonces el sistema mantiene deshabilitada la accion `Mezclar`.

## Restricciones

- Tecnicas: FFmpeg se invoca sin shell; la vista no valida audio directamente.
- Negocio: la asignacion de tipo es siempre manual en el MVP.
- Seguridad: no interpolar rutas en comandos; no modificar originales.

## Notas

- Los mensajes exactos de error estan definidos en la decision D3 (`docs/specs/DECISIONS.md`).

