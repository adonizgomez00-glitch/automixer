---
spec_id: "SPEC006"
version: "0.1.0"
status: "draft"
title: "Vista previa y reproduccion"
created: "2026-08-31"
updated: "2026-08-31"
related_specs: ["SPEC005", "SPEC009"]
tags: ["preview", "playback", "ui"]
---

# SPEC006: Vista previa y reproduccion

## Problema que se quiere resolver

El usuario necesita evaluar la mezcla temporal antes de exportarla mediante controles basicos de reproduccion.

## Contexto de uso

Despues de mezclar, AutoMixer carga el WAV temporal en el reproductor de vista previa usando QtMultimedia.

## Objetivo

Dado un WAV temporal renderizado correctamente, el sistema permite reproducir, pausar, detener, buscar posicion y ajustar volumen general de vista previa.

## Alcance

### Incluye

- Cargar WAV temporal de mezcla.
- Reproducir.
- Pausar.
- Detener.
- Mostrar y cambiar posicion.
- Volumen general de preview.

### No incluye

- Reproduccion individual por stem.
- Solo/mute por pista.
- Edicion de regiones.
- Medidores profesionales.
- Exportar desde el componente de preview.

## Comportamiento esperado

### Flujo principal

1. El render temporal termina.
2. El sistema carga el WAV temporal en el reproductor.
3. El usuario reproduce la mezcla.
4. El usuario puede pausar, detener, mover posicion y ajustar volumen.

### Flujos alternativos / edge cases

- No existe mezcla temporal: los controles de reproduccion no inician audio.
- Temporal eliminado o inaccesible: el sistema informa error y solicita regenerar.
- Nuevo render exitoso: reemplaza la fuente de preview anterior.

## Criterios de aceptacion

- AC-01: Dado un WAV temporal valido, cuando el sistema lo carga, entonces los controles de preview quedan disponibles.
- AC-02: Dado un WAV temporal cargado, cuando el usuario pulsa reproducir, entonces la reproduccion inicia.
- AC-03: Dado audio reproduciendose, cuando el usuario pulsa pausar, entonces la reproduccion se pausa conservando posicion.
- AC-04: Dado audio reproduciendose o pausado, cuando el usuario pulsa detener, entonces la reproduccion se detiene y vuelve a la posicion inicial.
- AC-05: Dado un WAV temporal cargado, cuando el usuario cambia posicion, entonces el reproductor busca esa posicion.
- AC-06: Dado un WAV temporal cargado, cuando el usuario cambia volumen general, entonces el volumen de preview cambia sin modificar ajustes de mezcla.
- AC-07: Dado que no existe WAV temporal, cuando el usuario intenta reproducir, entonces el sistema no reproduce y muestra estado de mezcla pendiente.

## Restricciones

- Tecnicas: preview mediante QtMultimedia sobre WAV temporal.
- Negocio: el volumen de preview no altera la mezcla ni la exportacion.
- Seguridad: no acceder a rutas que no pertenezcan al temporal activo.

## Notas

- Los estados visuales exactos de los controles quedan definidos en las decisiones de Diseño UI (`docs/design/UI_DECISIONS.md`, U1–U8).

