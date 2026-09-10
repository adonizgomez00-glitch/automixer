---
spec_id: "SPEC003"
version: "0.1.0"
status: "draft"
title: "Perfiles de mezcla y controles por stem"
created: "2026-08-31"
updated: "2026-08-31"
related_specs: ["SPEC002", "SPEC004", "SPEC005"]
tags: ["profiles", "mix", "controls"]
---

# SPEC003: Perfiles de mezcla y controles por stem

## Problema que se quiere resolver

AutoMixer debe aplicar decisiones de mezcla coherentes por genero y tipo de stem, permitiendo solo ajustes manuales simples para mantener el MVP acotado.

## Contexto de uso

El usuario elige Pop, Rock o Hip Hop. El sistema aplica automaticamente volumen base, paneo, normalizacion, EQ y compresion segun genero/tipo, mientras el usuario solo ajusta volumen por stem.

## Objetivo

Dado un proyecto con genero activo y stems clasificados, el sistema aplica un perfil fijo de mezcla por genero/tipo y permite ajustar manualmente la ganancia de cada stem entre -60 y +12 dB.

## Alcance

### Incluye

- Generos fijos: Pop, Rock y Hip Hop.
- Pop seleccionado por defecto.
- Perfil neutro para stems de tipo `Otro`.
- Ganancia manual por stem entre -60 y +12 dB.
- Restablecer volumen al perfil activo.
- Cambio de genero con regeneracion de mezcla y restablecimiento de ganancias al nuevo perfil.

### No incluye

- Editor visual de EQ.
- Editor de compresion.
- Paneo manual.
- Normalizacion manual.
- Creacion o edicion de perfiles por el usuario.
- Plugins de audio.

## Comportamiento esperado

### Flujo principal

1. El proyecto inicia con genero Pop.
2. El usuario clasifica stems.
3. El sistema calcula ajustes automaticos segun genero y tipo.
4. El usuario puede modificar solo la ganancia manual por stem.
5. Al mezclar, el sistema usa ajustes automaticos mas ganancia manual.

### Flujos alternativos / edge cases

- El usuario cambia de genero: se restablecen ganancias al perfil nuevo y se regenera la mezcla.
- El usuario usa `Restablecer`: volumen, desfase y correcciones vuelven al perfil activo.
- Stem `Otro`: recibe tratamiento neutro.
- Ganancia fuera de rango: el sistema rechaza el valor (`stem.gain_out_of_range`).

## Criterios de aceptacion

- AC-01: Dado un proyecto nuevo, cuando se inicializa, entonces el genero activo es Pop.
- AC-02: Dado un stem clasificado, cuando existe un perfil para su genero/tipo, entonces el sistema aplica los ajustes automaticos definidos para ese perfil.
- AC-03: Dado un stem de tipo `Otro`, cuando se mezcla, entonces el sistema aplica el perfil neutro.
- AC-04: Dado un valor de ganancia entre -60 y +12 dB, cuando el usuario lo aplica a un stem, entonces el sistema guarda la ganancia manual.
- AC-05: Dado un valor de ganancia fuera de -60 a +12 dB, cuando el usuario lo aplica, entonces el sistema rechaza el cambio.
- AC-06: Dado un proyecto con ganancias modificadas, cuando el usuario cambia de genero, entonces el sistema restablece ganancias al perfil nuevo y marca la mezcla para regeneracion.
- AC-07: Dado un stem con cambios manuales, cuando el usuario selecciona `Restablecer`, entonces el sistema devuelve volumen, desfase y correcciones al perfil activo.

## Restricciones

- Tecnicas: los perfiles deben vivir como datos JSON cuando se implemente.
- Negocio: perfiles fijos para MVP.
- Seguridad: ningun ajuste debe modificar archivos fuente.

## Anexo A: Parámetros de perfiles (decisión D1, 2026-08-31)

Los perfiles se almacenan como datos JSON fijos que se generan a partir de esta tabla en la implementación; no se editan desde la UI en el MVP. El tipo `otro` recibe el perfil neutro: sin EQ, sin compresión, sin normalización, paneo 0 y ganancia 0 dB.

Convenciones:
- `EQ` se expresa como ganancia (dB) a una frecuencia; banda 1 y banda 2 son opcionales (`—` = sin banda).
- Compresor: umbral (dB) / ratio / ataque / soltura. `—` = sin compresión.
- `Paneo ±X`: los stems de un mismo tipo se alternan entre `−X` y `+X` (izquierda/derecha) para evitar acumulación en un solo lado; con un solo stem se usa `−X`.
- Normalización y límite se aplican sobre la salida estéreo final (target de la mezcla completa, no por stem).

### Normalización final de mezcla

| Género | Normalización integrada | Límite de pico verdadero |
|---|---|---|
| Pop | I = −14 LUFS | TP = −1.0 dBTP |
| Rock | I = −12 LUFS | TP = −1.0 dBTP |
| Hip Hop | I = −13 LUFS | TP = −1.0 dBTP |

### Pop — parámetros por tipo

| Tipo | Ganancia base (dB) | Paneo | HPF | Banda 1 | Banda 2 | Compresor | Gan. recup. (dB) |
|---|---|---|---|---|---|---|---|
| voz | 0 | 0 | 100 Hz | −1.5 dB @ 400 Hz | +2 dB @ 3 kHz | −16 dB / 3:1 / 15 ms / 150 ms | 0 |
| batería | 0 | 0 | 25 Hz | +1.5 dB @ 5 kHz | — | −18 dB / 3:1 / 10 ms / 100 ms | 0 |
| bajo | 0 | 0 | 30 Hz | +1 dB @ 120 Hz | — | −20 dB / 4:1 / 20 ms / 120 ms | 0 |
| guitarra | 0 | ±0.15 | 90 Hz | −1 dB @ 400 Hz | +2 dB @ 2.5 kHz | −18 dB / 2.5:1 / 10 ms / 100 ms | 0 |
| teclados | 0 | ±0.20 | 80 Hz | −1.5 dB @ 800 Hz | — | — | 0 |
| sintes | 0 | ±0.10 | 60 Hz | +1 dB @ 3.5 kHz | — | — | 0 |
| drops | 0 | 0 | 30 Hz | +1 dB @ 100 Hz | — | — | 0 |
| efectos | −6 | ±0.30 | 100 Hz | −2 dB @ 1 kHz | — | — | 0 |
| otro | 0 | 0 | — | — | — | — | 0 |

### Rock — parámetros por tipo

| Tipo | Ganancia base (dB) | Paneo | HPF | Banda 1 | Banda 2 | Compresor | Gan. recup. (dB) |
|---|---|---|---|---|---|---|---|
| voz | 0 | 0 | 110 Hz | −1 dB @ 500 Hz | +1.5 dB @ 2.5 kHz | — | 0 |
| batería | +1 | 0 | 25 Hz | +2 dB @ 4 kHz | — | −18 dB / 3:1 / 10 ms / 100 ms | 0 |
| bajo | 0 | 0 | 30 Hz | +2 dB @ 100 Hz | — | −20 dB / 4:1 / 20 ms / 120 ms | +1 |
| guitarra | +1 | ±0.25 | 90 Hz | −1.5 dB @ 600 Hz | +2.5 dB @ 2 kHz | −18 dB / 2.5:1 / 10 ms / 100 ms | 0 |
| teclados | −3.5 | ±0.20 | 80 Hz | — | — | — | 0 |
| sintes | −3 | ±0.15 | 60 Hz | — | — | — | 0 |
| drops | −1.5 | 0 | 30 Hz | — | — | — | 0 |
| efectos | −7 | ±0.35 | 100 Hz | — | — | — | 0 |
| otro | 0 | 0 | — | — | — | — | 0 |

### Hip Hop — parámetros por tipo

| Tipo | Ganancia base (dB) | Paneo | HPF | Banda 1 | Banda 2 | Compresor | Gan. recup. (dB) |
|---|---|---|---|---|---|---|---|
| voz | 0 | 0 | 90 Hz | −2 dB @ 250 Hz | +2 dB @ 3 kHz | −16 dB / 3:1 / 15 ms / 150 ms | 0 |
| batería | +1.5 | 0 | 25 Hz | +3 dB @ 60 Hz | — | −18 dB / 4:1 / 10 ms / 100 ms | 0 |
| bajo | +2 | 0 | 28 Hz | +2.5 dB @ 60 Hz | — | −20 dB / 4:1 / 20 ms / 120 ms | 0 |
| guitarra | −2.5 | ±0.20 | 90 Hz | — | — | — | 0 |
| teclados | −4 | ±0.25 | 80 Hz | — | — | — | 0 |
| sintes | −3 | ±0.15 | 60 Hz | — | — | — | 0 |
| drops | +1 | 0 | 30 Hz | +2 dB @ 55 Hz | — | — | 0 |
| efectos | −7 | ±0.35 | 100 Hz | — | — | — | 0 |
| otro | 0 | 0 | — | — | — | — | 0 |

## Notas

- Decisión D1 (parámetros de perfiles) resuelta en este Anexo A.
- El resto de decisiones (D2–D6) está resuelto en `DECISIONS.md` y en sus specs correspondientes.

