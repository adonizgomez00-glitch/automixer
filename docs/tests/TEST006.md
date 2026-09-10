# TEST006 — Pruebas funcionales: Vista previa y reproducción

**Fuente:** `SPEC006` · **Criterios cubiertos:** AC-01 a AC-07 · **Estado:** borrador, sin ejecución · **Fecha:** 2026-08-31

Se probarán contra el adaptador `Playback` (QtMultimedia) sobre un WAV temporal.

## TEST006-AC-01 — Carga del WAV temporal habilita controles

- **Dado** un WAV temporal válido renderizado.
- **Cuando** el sistema lo carga en el reproductor.
- **Entonces** los controles de preview quedan disponibles.

## TEST006-AC-02 — Reproducir inicia la reproducción

- **Dado** un WAV temporal cargado.
- **Cuando** el usuario pulsa reproducir.
- **Entonces** inicia la reproducción desde la posición actual.

## TEST006-AC-03 — Pausa conserva la posición

- **Dado** audio en reproducción.
- **Cuando** el usuario pulsa pausar.
- **Entonces** la reproducción se pausa conservando la posición.

## TEST006-AC-04 — Detener vuelve a la posición inicial

- **Dado** audio reproduciéndose o pausado.
- **Cuando** el usuario pulsa detener.
- **Entonces** la reproducción se detiene y la posición vuelve al inicio.

## TEST006-AC-05 — Cambiar posición busca en el audio

- **Dado** un WAV temporal cargado.
- **Cuando** el usuario cambia la posición (slider o entrada).
- **Entonces** el reproductor busca esa posición.

## TEST006-AC-06 — Volumen de preview no altera la mezcla

- **Dado** un WAV temporal cargado.
- **Cuando** el usuario cambia el volumen general de preview.
- **Entonces** el volumen de reproducción cambia sin modificar ajustes de mezcla ni la futura exportación.

## TEST006-AC-07 — Sin temporal no se reproduce

- **Dado** que no existe WAV temporal (o se eliminó).
- **Cuando** el usuario intenta reproducir.
- **Entonces** el sistema no reproduce y muestra el estado de mezcla pendiente de regeneración.

## Notas

- La generación y limpieza del temporal se prueba en `TEST005`.