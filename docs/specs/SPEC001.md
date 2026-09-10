---
spec_id: "SPEC001"
version: "0.1.0"
status: "draft"
title: "Gestion de proyecto local"
created: "2026-08-31"
updated: "2026-08-31"
related_specs: ["SPEC008", "SPEC009"]
tags: ["project", "local", "mvp"]
---

# SPEC001: Gestion de proyecto local

## Problema que se quiere resolver

AutoMixer necesita organizar una mezcla como un proyecto local unico para una cancion, sin cuentas, nube ni biblioteca musical.

## Contexto de uso

Un productor crea un proyecto desde la app de escritorio, elige nombre y ubicacion, agrega stems locales y conserva ajustes no destructivos para retomarlos despues.

## Objetivo

Dado un nombre y una ubicacion validos, el sistema crea un proyecto local de una sola cancion y mantiene su estado disponible para importar, mezclar, previsualizar, guardar y exportar.

## Alcance

### Incluye

- Crear un proyecto nuevo solicitando nombre y ubicacion.
- Mantener un proyecto activo por ventana/sesion del MVP.
- Asociar el proyecto a una cancion.
- Permitir cerrar el proyecto activo.
- Confirmar cierre si existe un trabajo de audio en curso.

### No incluye

- Cuentas de usuario.
- Sincronizacion en nube.
- Biblioteca o catalogo multi-cancion.
- Varios proyectos abiertos simultaneamente.
- Plantillas de proyecto.

## Comportamiento esperado

### Flujo principal

1. El usuario crea un proyecto.
2. El sistema solicita nombre y ubicacion.
3. El sistema valida que la ubicacion pueda alojar el archivo de proyecto.
4. El sistema inicializa un proyecto vacio con genero Pop por defecto.
5. El sistema permite importar stems y modificar ajustes.

### Flujos alternativos / edge cases

- Nombre vacio: el sistema rechaza la creacion y muestra error (`project.name_empty`).
- Ubicacion no escribible: el sistema rechaza la creacion y muestra error (`project.folder_notwritable`).
- Cierre con trabajo activo: el sistema solicita confirmacion (`busy.confirm_close`) y cancela el trabajo antes de salir.
- Cierre sin trabajo activo: el sistema limpia temporales propios y cierra el proyecto.

## Criterios de aceptacion

- AC-01: Dado un nombre y una ubicacion validos, cuando el usuario crea un proyecto, entonces el sistema crea un proyecto activo con genero Pop predeterminado.
- AC-02: Dado un nombre vacio, cuando el usuario intenta crear un proyecto, entonces el sistema no crea el proyecto y muestra un error de validacion.
- AC-03: Dada una ubicacion no escribible, cuando el usuario intenta crear un proyecto, entonces el sistema no crea el proyecto y muestra un error de acceso.
- AC-04: Dado un proyecto con un trabajo de audio activo, cuando el usuario intenta cerrar, entonces el sistema solicita confirmacion antes de cancelar y cerrar.
- AC-05: Dado un proyecto sin trabajo activo, cuando el usuario cierra el proyecto, entonces el sistema limpia solo los temporales propios y conserva archivos fuente/exportados.

## Restricciones

- Tecnicas: app local de escritorio; una cancion por proyecto; dependencias compuestas manualmente en `app.py` cuando se implemente.
- Negocio: el MVP debe mantenerse simple y local.
- Seguridad: no debe borrar archivos originales ni archivos exportados al cerrar.

## Notas

- La persistencia concreta del proyecto se especifica en `SPEC008`.
- La cancelacion de trabajos se especifica en `SPEC009`.

