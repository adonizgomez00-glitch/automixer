---
spec_id: "SPEC009"
version: "0.1.0"
status: "draft"
title: "Trabajos cancelables, progreso y cierre seguro"
created: "2026-08-31"
updated: "2026-08-31"
related_specs: ["SPEC001", "SPEC005", "SPEC007"]
tags: ["workers", "progress", "cancel"]
---

# SPEC009: Trabajos cancelables, progreso y cierre seguro

## Problema que se quiere resolver

Mezclar y exportar pueden tardar y consumir CPU. La UI debe seguir respondiendo, mostrar progreso y permitir cancelar sin dañar el proyecto.

## Contexto de uso

AutoMixer ejecuta renderizados y exportaciones en un worker de segundo plano. Solo se permite un trabajo de audio por vez.

## Objetivo

Dado un trabajo de audio en ejecucion, el sistema mantiene la UI responsive, emite progreso, permite cancelacion y limpia solo artefactos temporales propios.

## Alcance

### Incluye

- Worker de segundo plano para mezcla y exportacion.
- Un trabajo de audio por vez.
- Progreso visible.
- Cancelacion por usuario.
- Confirmacion al cerrar durante un trabajo.
- Terminacion del proceso FFmpeg asociado.
- Limpieza de temporales propios incompletos.

### No incluye

- Cola de multiples trabajos.
- Ejecucion paralela de renders.
- Reintentos automaticos complejos.
- Priorizacion de trabajos.
- Procesamiento distribuido.

## Comportamiento esperado

### Flujo principal

1. El usuario inicia mezcla o exportacion.
2. El sistema crea un trabajo cancelable.
3. El worker emite progreso.
4. La UI refleja estado y bloquea iniciar otro trabajo de audio.
5. Al terminar, el sistema entrega resultado o error.

### Flujos alternativos / edge cases

- El usuario cancela: el proceso termina, el proyecto se conserva y se limpian artefactos parciales propios.
- El usuario intenta iniciar otro trabajo: el sistema lo rechaza o mantiene la accion deshabilitada.
- El usuario cierra durante un trabajo: el sistema pide confirmacion (`busy.confirm_close`) y cancela antes de salir.
- FFmpeg falla: el sistema transforma el fallo externo en error de dominio.

## Criterios de aceptacion

- AC-01: Dado que no hay trabajo activo, cuando el usuario inicia mezcla o exportacion, entonces el sistema crea un trabajo en segundo plano.
- AC-02: Dado un trabajo activo, cuando el motor reporta avance, entonces la UI muestra progreso.
- AC-03: Dado un trabajo activo, cuando el usuario intenta iniciar otro trabajo de audio, entonces el sistema impide la segunda ejecucion.
- AC-04: Dado un trabajo activo, cuando el usuario cancela, entonces el sistema termina el proceso asociado y conserva el proyecto.
- AC-05: Dado un trabajo cancelado, cuando termina la cancelacion, entonces el sistema limpia solo temporales o parciales propios de ese trabajo.
- AC-06: Dado un trabajo activo, cuando el usuario intenta cerrar la app, entonces el sistema solicita confirmacion antes de cancelar y salir.
- AC-07: Dado un fallo externo de FFmpeg, cuando el worker lo recibe, entonces el servicio devuelve un error de dominio claro.

## Restricciones

- Tecnicas: workers con senales de progreso; servicios devuelven `Result` cuando se implemente.
- Negocio: no bloquear la UI durante trabajos pesados.
- Seguridad: no matar procesos ajenos ni borrar rutas no creadas por AutoMixer.

## Notas

- Pendiente: estados UI exactos y mensajes de progreso.

