# TEST004 — Pruebas funcionales: Sincronización de tempo y alineación temporal

**Fuente:** `SPEC004` · **Criterios cubiertos:** AC-01 a AC-08 · **Estado:** borrador, sin ejecución · **Fecha:** 2026-08-31

Umbrales aplicados según la decisión D2: tempo fiable si `confidence ≥ 0.80` y `ratio ∈ [0.75, 1.33]`; alineación fiable si `confidence ≥ 0.85` y `|desfase| ≤ 2000 ms`.

## TEST004-AC-01 — Referencia inicial: batería

- **Dado** un proyecto con al menos un stem de tipo batería válido.
- **Cuando** se establece la referencia inicial.
- **Entonces** la batería queda fijada como referencia.

## TEST004-AC-02 — Referencia inicial sin batería: primer stem válido

- **Dado** un proyecto sin batería y con stems válidos.
- **Cuando** se establece la referencia inicial.
- **Entonces** el primer stem válido queda como referencia.

## TEST004-AC-03 — Corrección no destructiva de tempo

- **Dado** un análisis de tempo fiable para un stem.
- **Cuando** el usuario sincroniza el tempo del stem.
- **Entonces** el sistema guarda una corrección no destructiva `tempo_ratio` en el proyecto (el audio original no se modifica).

## TEST004-AC-04 — Corrección no destructiva de inicio

- **Dado** un análisis de inicio fiable para un stem.
- **Cuando** el usuario alinea el inicio del stem.
- **Entonces** el sistema guarda una corrección no destructiva `start_offset_ms` en el proyecto.

## TEST004-AC-05 — Baja fiabilidad: advertir y no alterar

- **Dado** un análisis con confianza por debajo del umbral de su operación.
- **Cuando** el usuario sincroniza o alinea.
- **Entonces** el sistema advierte (`sync.low_confidence_tempo` / `sync.low_confidence_alignment`) y deja el stem sin modificar.

## TEST004-AC-06 — Cambio de referencia conserva desfase manual

- **Dado** un stem con desfase manual (`manual_offset_ms`) y otro sin él.
- **Cuando** se recalcula la referencia.
- **Entonces** el sistema conserva el desfase manual de ese stem y recalcula solo los stems sin desfase manual.

## TEST004-AC-07 — Batería añadida después se adapta a la referencia

- **Dado** una referencia fijada sin batería (p. ej. primer stem).
- **Cuando** se agrega una batería y se recalcula la mezcla.
- **Entonces** la batería se adapta a la referencia existente (no la reemplaza).

## TEST004-AC-08 — Restablecer elimina correcciones y desfase

- **Dado** un stem con correcciones de tempo/inicio y/o desfase manual.
- **Cuando** el usuario selecciona `Restablecer`.
- **Entonces** el sistema elimina correcciones y desfase manual de ese stem y vuelve al perfil activo.

## Notas

- Los fallos de análisis de FFmpeg se transforman en error de dominio en `TEST009` (AC-07).
- La aplicación de correcciones al render se prueba en `TEST005` (AC-05).