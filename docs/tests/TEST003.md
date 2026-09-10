# TEST003 — Pruebas funcionales: Perfiles de mezcla y controles por stem

**Fuente:** `SPEC003` · **Criterios cubiertos:** AC-01 a AC-07 · **Estado:** borrador, sin ejecución · **Fecha:** 2026-08-31

Se verifican contra los perfiles JSON generados desde el Anexo A de `SPEC003` (decisión D1).

## TEST003-AC-01 — Género inicial Pop

- **Dado** un proyecto nuevo.
- **Cuando** se inicializa.
- **Entonces** el género activo es `pop`.

## TEST003-AC-02 — Aplicar perfil por género/tipo

- **Dado** un stem clasificado con un tipo concreto (p. ej. `voz`).
- **Cuando** el perfil para su género/tipo existe.
- **Entonces** el sistema aplica los ajustes automáticos definidos en ese perfil (ganancia base, paneo, HPF, EQ, compresión).

## TEST003-AC-03 — Perfil neutro para tipo Otro

- **Dado** un stem de tipo `otro`.
- **Cuando** se mezcla.
- **Entonces** el sistema aplica el perfil neutro (paneo 0, ganancia 0, sin EQ ni compresión).

## TEST003-AC-04 — Aceptar ganancia dentro de rango

- **Dado** un valor de ganancia entre −60 y +12 dB.
- **Cuando** el usuario lo aplica a un stem.
- **Entonces** el sistema guarda la ganancia manual del stem.

## TEST003-AC-05 — Rechazar ganancia fuera de rango

- **Dado** un valor de ganancia fuera de −60 a +12 dB.
- **Cuando** el usuario intenta aplicarlo.
- **Entonces** el sistema rechaza el cambio y muestra `stem.gain_out_of_range`.

## TEST003-AC-06 — Cambio de género restablece ganancias y marca regeneración

- **Dado** un proyecto con ganancias manuales modificadas.
- **Cuando** el usuario cambia de género.
- **Entonces** el sistema restablece las ganancias al perfil nuevo y marca la mezcla como pendiente de regeneración.

## TEST003-AC-07 — Restablecer devuelve al perfil activo

- **Dado** un stem con ganancia, desfase y/o correcciones manuales.
- **Cuando** el usuario selecciona `Restablecer`.
- **Entonces** el sistema devuelve volumen, desfase y correcciones al perfil activo.

## Notas

- La regeneración de la mezcla se prueba en `TEST005`.
- El desfase manual y `Restablecer` en tempo/alineación se prueban en `TEST004` (AC-08).