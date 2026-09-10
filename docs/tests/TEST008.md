# TEST008 — Pruebas funcionales: Persistencia `.automixer` y preferencias

**Fuente:** `SPEC008` · **Criterios cubiertos:** AC-01 a AC-07 · **Estado:** borrador, sin ejecución · **Fecha:** 2026-08-31

Esquema aplicado según la decisión D4 (`schema_version: 1`).

## TEST008-AC-01 — Guardado manual escribe `.automixer` versionado

- **Dado** un proyecto modificado.
- **Cuando** se ejecuta el guardado manual.
- **Entonces** el sistema escribe un archivo `.automixer` con `schema_version: 1` en la ubicación del proyecto.

## TEST008-AC-02 — Cambio relevante agenda guardado automático

- **Dado** un cambio relevante (tipo, ganancia, corrección, género, referencia…).
- **Cuando** ocurre el cambio.
- **Entonces** el sistema agenda o ejecuta el guardado automático del proyecto.

## TEST008-AC-03 — Fallo de escritura conserva el archivo previo

- **Dado** un fallo durante la escritura del temporal.
- **Cuando** el guardado falla.
- **Entonces** el archivo previo permanece intacto y recuperable (escritura atómica).

## TEST008-AC-04 — Carga de `.automixer` reconstruye el proyecto

- **Dado** un `.automixer` válido.
- **Cuando** el usuario lo abre.
- **Entonces** el sistema carga stems, género, referencia y ajustes guardados.

## TEST008-AC-05 — Stem con ruta inexistente queda no disponible

- **Dado** un stem cuya ruta ya no existe.
- **Cuando** se carga el proyecto.
- **Entonces** el sistema revalida y marca el stem como no disponible.

## TEST008-AC-06 — Reubicar stem actualiza ruta y valida

- **Dado** un stem no disponible.
- **Cuando** el usuario selecciona una nueva ruta válida.
- **Entonces** el sistema actualiza la ruta y marca el stem como disponible.

## TEST008-AC-07 — Preferencia de idioma aplicada al inicio

- **Dado** una preferencia de idioma guardada.
- **Cuando** inicia la aplicación.
- **Entonces** el sistema la aplica; si no existe, usa el idioma del sistema o el predeterminado (decisión D6; ver `TEST010`).

## Notas

- El rechazo de versiones de esquema no soportadas se probará con un `.automixer` con `schema_version` distinto de `1`, esperando `project.schema_unsupported`.