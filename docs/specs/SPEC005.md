---
spec_id: "SPEC005"
version: "0.1.0"
status: "draft"
title: "Renderizado de mezcla temporal"
created: "2026-08-31"
updated: "2026-08-31"
related_specs: ["SPEC002", "SPEC003", "SPEC004", "SPEC006", "SPEC009"]
tags: ["render", "mix", "temporary"]
---

# SPEC005: Renderizado de mezcla temporal

## Problema que se quiere resolver

El usuario necesita escuchar una mezcla calculada antes de exportarla, sin modificar stems originales y sin generar archivos finales innecesarios.

## Contexto de uso

El usuario pulsa `Mezclar` despues de importar al menos un stem valido. El sistema genera un WAV temporal estereo para vista previa.

## Objetivo

Dado un proyecto con al menos un stem valido, el sistema renderiza una mezcla temporal estereo usando perfiles y correcciones activas, y entrega un WAV temporal reproducible.

## Alcance

### Incluye

- Render temporal para vista previa.
- Salida estereo.
- Duracion hasta el stem mas largo.
- Aplicar perfiles de genero/tipo.
- Aplicar ganancia manual, correcciones de tempo/inicio y desfase manual.
- Crear temporales privados de la aplicacion.
- Limpiar temporales al cerrar proyecto o aplicacion.

### No incluye

- Exportacion final.
- Mastering avanzado.
- Procesamiento por lotes.
- Edicion multipista no destructiva visual.
- Guardar el temporal como artefacto permanente.

## Comportamiento esperado

### Flujo principal

1. El usuario pulsa `Mezclar`.
2. El sistema valida que exista al menos un stem valido.
3. El sistema inicia un trabajo de audio.
4. El motor genera un WAV temporal estereo.
5. El sistema informa progreso.
6. Al terminar, el temporal queda disponible para vista previa.

### Flujos alternativos / edge cases

- Sin stems validos: `Mezclar` no esta disponible.
- Fallo de FFmpeg: el sistema muestra error y no reemplaza una preview valida anterior.
- Cancelacion: el sistema termina el proceso y limpia temporales incompletos propios.
- Cambio de genero o ajustes: la mezcla queda pendiente de regeneracion.

## Criterios de aceptacion

- AC-01: Dado al menos un stem valido, cuando el usuario pulsa `Mezclar`, entonces el sistema inicia el render de mezcla temporal.
- AC-02: Dado cero stems validos, cuando el usuario observa la UI, entonces la accion `Mezclar` esta deshabilitada.
- AC-03: Dado un render exitoso, cuando termina el trabajo, entonces existe un WAV temporal estereo reproducible.
- AC-04: Dado stems de distinta duracion, cuando se renderiza, entonces la mezcla termina con el stem mas largo.
- AC-05: Dado ajustes activos de perfil, ganancia, tempo, inicio y desfase, cuando se renderiza, entonces la mezcla temporal los aplica.
- AC-06: Dado un fallo de render, cuando el motor devuelve error, entonces el sistema muestra error claro y conserva el proyecto.
- AC-07: Dado un render cancelado, cuando la cancelacion termina, entonces el sistema limpia temporales incompletos propios.

## Restricciones

- Tecnicas: FFmpeg incluido e invocado sin shell; un trabajo de audio por vez.
- Negocio: el temporal no es exportacion final.
- Seguridad: borrar solo temporales creados por AutoMixer.

## Notas

- La reproduccion del temporal se especifica en `SPEC006`.
- El ciclo de progreso/cancelacion se especifica en `SPEC009`.

