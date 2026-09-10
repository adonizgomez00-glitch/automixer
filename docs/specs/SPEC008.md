---
spec_id: "SPEC008"
version: "0.1.0"
status: "draft"
title: "Persistencia .automixer y preferencias"
created: "2026-08-31"
updated: "2026-08-31"
related_specs: ["SPEC001", "SPEC002", "SPEC003", "SPEC004", "SPEC010"]
tags: ["persistence", "json", "settings"]
---

# SPEC008: Persistencia `.automixer` y preferencias

## Problema que se quiere resolver

El usuario necesita guardar y reabrir proyectos sin duplicar audios, preservando rutas, clasificacion, genero y ajustes no destructivos.

## Contexto de uso

AutoMixer usa un archivo JSON versionado `.automixer` para el proyecto y preferencias de aplicacion separadas para idioma y ajustes globales.

## Objetivo

Dado un proyecto con stems y ajustes, el sistema guarda y carga un archivo `.automixer` versionado con rutas a los audios, sin copiar los archivos fuente.

## Alcance

### Incluye

- Guardado manual.
- Guardado automatico tras cambios relevantes.
- Escritura atomica: temporal y reemplazo.
- Carga de proyecto `.automixer`.
- Rutas de stems y estado de disponibilidad.
- Genero, tipos, ganancias, correcciones de tempo/inicio, desfase manual y referencia.
- Preferencias de idioma mediante settings de aplicacion.
- Reubicar stem faltante.

### No incluye

- Base de datos.
- Copia o empaquetado de stems dentro del proyecto.
- Control de versiones interno del proyecto.
- Sincronizacion entre equipos.
- Cifrado de proyecto.

## Comportamiento esperado

### Flujo principal

1. El usuario crea o modifica un proyecto.
2. El sistema guarda cambios relevantes de forma atomica.
3. El usuario puede guardar manualmente.
4. Al abrir el archivo `.automixer`, el sistema reconstruye el proyecto.
5. Si faltan stems, el sistema los marca como no disponibles y permite localizarlos.

### Flujos alternativos / edge cases

- Fallo durante guardado: el archivo anterior queda intacto.
- Ruta de stem inexistente al cargar: el stem queda marcado como faltante.
- Usuario reubica un stem: se actualiza la ruta y se revalida.
- Version de esquema no soportada: el sistema rechaza la carga con error claro (`project.schema_unsupported`).

## Criterios de aceptacion

- AC-01: Dado un proyecto modificado, cuando se ejecuta guardado manual, entonces el sistema escribe un `.automixer` versionado.
- AC-02: Dado un cambio relevante del proyecto, cuando ocurre el cambio, entonces el sistema agenda o ejecuta guardado automatico.
- AC-03: Dado un fallo durante escritura, cuando el guardado falla, entonces el archivo previo permanece recuperable.
- AC-04: Dado un `.automixer` valido, cuando el usuario lo abre, entonces el sistema carga stems, genero y ajustes guardados.
- AC-05: Dado un stem cuya ruta ya no existe, cuando se carga el proyecto, entonces el sistema marca el stem como no disponible.
- AC-06: Dado un stem no disponible, cuando el usuario selecciona una nueva ruta valida, entonces el sistema actualiza la ruta y marca el stem como disponible.
- AC-07: Dada una preferencia de idioma guardada, cuando inicia la app, entonces el sistema la aplica salvo que no exista y deba usar idioma del sistema.

## Restricciones

- Tecnicas: JSON versionado para proyecto; QSettings para preferencias cuando se implemente.
- Negocio: no copiar audios mantiene proyectos ligeros.
- Seguridad: no borrar ni sobrescribir audios al guardar.

## Esquema JSON del proyecto (decisión D4, 2026-08-31)

`schema_version: 1`. El proyecto es un único archivo `.automixer`; no copia audios, solo rutas y ajustes.

```json
{
  "schema_version": 1,
  "id": "uuid-v4",
  "name": "Mi cancion",
  "genre": "pop",
  "reference_stem_id": null,
  "stems": [
    {
      "id": "uuid-v4",
      "path": "/ruta/voz.flac",
      "type": "voz",
      "gain_db": 0.0,
      "corrections": {
        "tempo_ratio": null,
        "start_offset_ms": null,
        "confidence": null,
        "manual_offset_ms": null
      }
    }
  ],
  "created_at": "2026-08-31T00:00:00Z",
  "updated_at": "2026-08-31T00:00:00Z"
}
```

Reglas:
- `genre`: `pop`, `rock` o `hip_hop`. `reference_stem_id`: si es `null` al cargar, se deriva (batería; si no existe, primer stem válido).
- Cada campo de `corrections` opcional es `null` = sin corrección aplicada. `manual_offset_ms` tiene prioridad solo en su stem.
- `available` **no se persiste**: se deriva al cargar comprobando que el `path` existe y decodifica (FFmpeg), y se revalida al reubicar un stem.
- Sobrescritura atómica: se escribe `<proyecto>.automixer.tmp` y se reemplaza con `os.replace`; si falla, el archivo previo queda intacto.
- Versiones soportadas: solo `1`. Un `schema_version` distinto rechaza la carga con `project.schema_unsupported`.
- Migraciones futuras: cada versión nueva añade una fila a esta tabla ejecutable en orden.

| Desde | Hasta | Acción |
|---|---|---|
| 1 | (actual) | Sin migración |

## Notas

- Decisión D4 (esquema JSON del proyecto) resuelta en este documento.
- El resto de decisiones (D5–D6) está resuelto en `DECISIONS.md` y en `SPEC010`.

