---
spec_id: "SPEC004"
version: "0.1.0"
status: "draft"
title: "Sincronizacion de tempo y alineacion temporal"
created: "2026-08-31"
updated: "2026-08-31"
related_specs: ["SPEC002", "SPEC003", "SPEC005"]
tags: ["tempo", "alignment", "audio"]
---

# SPEC004: Sincronizacion de tempo y alineacion temporal

## Problema que se quiere resolver

Stems de una misma cancion pueden tener diferencias de tempo o inicio. AutoMixer debe corregirlos de forma no destructiva y permitir ajuste manual cuando el analisis no sea fiable.

## Contexto de uso

El usuario trabaja con stems locales importados en 0. La referencia inicial es bateria; si no existe, el primer stem. La referencia queda fijada y puede cambiarse manualmente.

## Objetivo

Dado un proyecto con stems validos, el sistema usa una referencia fija para calcular correcciones no destructivas de tempo e inicio, preservando el desfase manual de cada stem cuando exista.

## Alcance

### Incluye

- Referencia inicial: bateria; si no existe, primer stem.
- Fijar referencia al establecer tempo/alineacion.
- Cambiar referencia manualmente.
- Recalcular stems sin desfase manual al cambiar referencia.
- Sincronizar tempo por stem.
- Alinear inicio por stem.
- Desfase manual positivo/negativo en milisegundos.
- Advertir y dejar intacto el stem cuando el analisis tiene baja fiabilidad.

### No incluye

- Edicion visual multipista.
- Warping manual avanzado.
- Beat grid editable.
- Deteccion automatica de tipo de stem.
- Garantia de correccion perfecta en material ambiguo.

## Comportamiento esperado

### Flujo principal

1. El sistema determina la referencia inicial.
2. El usuario solicita sincronizar tempo o alinear inicio.
3. El sistema analiza stem y referencia.
4. Si el analisis es fiable, guarda correcciones no destructivas.
5. Si el analisis no es fiable, advierte y mantiene el stem sin modificar.
6. Al renderizar, el sistema aplica correcciones y desfase manual.

### Flujos alternativos / edge cases

- No hay bateria: el primer stem valido es referencia.
- Se agrega bateria despues de fijar otra referencia: la bateria se adapta a la referencia existente.
- El usuario cambia referencia: se recalculan stems sin desfase manual.
- Un stem tiene desfase manual: ese valor tiene prioridad solo en ese stem.
- `Restablecer`: elimina desfase y correcciones, y vuelve al perfil activo.

## Criterios de aceptacion

- AC-01: Dado un proyecto con bateria valida, cuando se establece la referencia inicial, entonces la bateria queda como referencia.
- AC-02: Dado un proyecto sin bateria y con stems validos, cuando se establece la referencia inicial, entonces el primer stem valido queda como referencia.
- AC-03: Dado un analisis de tempo fiable, cuando el usuario sincroniza un stem, entonces el sistema guarda una correccion no destructiva de tempo.
- AC-04: Dado un analisis de inicio fiable, cuando el usuario alinea un stem, entonces el sistema guarda una correccion no destructiva de inicio.
- AC-05: Dado un analisis de baja fiabilidad, cuando el usuario sincroniza o alinea, entonces el sistema advierte y no altera el stem.
- AC-06: Dado un stem con desfase manual, cuando se recalcula la referencia, entonces el sistema conserva el desfase manual de ese stem.
- AC-07: Dado una nueva bateria agregada despues de fijar referencia, cuando se recalcula la mezcla, entonces la bateria se adapta a la referencia existente.
- AC-08: Dado un stem con correcciones, cuando el usuario selecciona `Restablecer`, entonces el sistema elimina correcciones y desfase manual de ese stem.

## Restricciones

- Tecnicas: correcciones almacenadas como metadatos del proyecto; audio original intacto.
- Negocio: si la calidad del analisis no es fiable, se prefiere advertir antes que alterar.
- Seguridad: solo se procesan archivos seleccionados por el usuario.

## Fiabilidad y umbrales (decisión D2, 2026-08-31)

Se define `confidence` como la correlación normalizada del análisis (envolvente/onsets) entre el stem y la referencia, en el rango `[0, 1]`. Un análisis es **fiable** solo si cumple los dos criterios de su operación:

| Operación | Confianza mínima | Límite físico adicional | Por debajo |
|---|---|---|---|
| Sincronizar tempo | `confidence ≥ 0.80` | `ratio tempo ∈ [0.75, 1.33]` (aceleración/desaceleración fuera de −25 %/+33 % se descarta) | Advertir y dejar el stem intacto |
| Alinear inicio | `confidence ≥ 0.85` | `\|desfase\| ≤ 2000 ms` | Advertir y dejar el stem intacto |

Reglas:
- El valor de `confidence` resultante se guarda como metadato del proyecto junto a la corrección; la advertencia muestra el valor obtenido (clave de mensaje `sync.low_confidence_tempo` / `sync.low_confidence_alignment`).
- `Restablecer` elimina la corrección y el `confidence` asociado, y vuelve al perfil activo.
- Si la operación no es fiable no se crea ni se modifica ninguna corrección.

## Notas

- Decisión D2 (umbrales de fiabilidad) resuelta en este documento.
- El resto de decisiones (D3–D6) está resuelto en `DECISIONS.md` y en sus specs correspondientes.

