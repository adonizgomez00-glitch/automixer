# TEST005 — Pruebas funcionales: Renderizado de mezcla temporal

**Fuente:** `SPEC005` · **Criterios cubiertos:** AC-01 a AC-07 · **Estado:** borrador, sin ejecución · **Fecha:** 2026-08-31

## TEST005-AC-01 — Iniciar render con al menos un stem válido

- **Dado** al menos un stem válido en el proyecto.
- **Cuando** el usuario pulsa `Mezclar`.
- **Entonces** el sistema inicia el render de una mezcla temporal en un worker de segundo plano (ver `TEST009`).

## TEST005-AC-02 — Mezclar deshabilitada sin stems válidos

- **Dado** cero stems válidos.
- **Cuando** el usuario observa la UI.
- **Entonces** la acción `Mezclar` está deshabilitada.

## TEST005-AC-03 — Render exitoso produce WAV temporal estéreo

- **Dado** un render que termina correctamente.
- **Cuando** el trabajo finaliza.
- **Entonces** existe un WAV temporal estéreo reproducible en el almacén de temporales de la aplicación.

## TEST005-AC-04 — La mezcla termina con el stem más largo

- **Dado** stems de distinta duración.
- **Cuando** se renderiza la mezcla.
- **Entonces** la duración del temporal es igual a la del stem más largo (incluye su desfase si lo hay).

## TEST005-AC-05 — El render aplica ajustes activos

- **Dado** ajustes activos de perfil, ganancia manual, correcciones de tempo/inicio y desfase manual.
- **Cuando** se renderiza la mezcla.
- **Entonces** el temporal incorpora dichos ajustes según lo definido en `SPEC003` y `SPEC004`.

## TEST005-AC-06 — Fallo de render conserva el proyecto y avisa

- **Dado** un fallo del motor al renderizar.
- **Cuando** el motor devuelve el error.
- **Entonces** el sistema muestra un error claro y conserva el proyecto y la preview válida anterior si existía.

## TEST005-AC-07 — Render cancelado limpia temporales parciales

- **Dado** un render cancelado por el usuario.
- **Cuando** termina la cancelación.
- **Entonces** el sistema limpia los temporales incompletos creados por ese trabajo y conserva el proyecto.

## Notas

- El ciclo de progreso y cancelación se prueba en `TEST009`.
- La reproducción del temporal se prueba en `TEST006`.