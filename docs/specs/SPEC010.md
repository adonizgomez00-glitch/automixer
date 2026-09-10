---
spec_id: "SPEC010"
version: "0.1.0"
status: "draft"
title: "Internacionalizacion, empaquetado y licencias"
created: "2026-08-31"
updated: "2026-08-31"
related_specs: ["SPEC008"]
tags: ["i18n", "packaging", "license"]
---

# SPEC010: Internacionalizacion, empaquetado y licencias

## Problema que se quiere resolver

AutoMixer debe poder usarse en espanol e ingles y distribuirse localmente en Linux y Windows con FFmpeg incluido y avisos de licencia correspondientes.

## Contexto de uso

El usuario instala una app de escritorio local. La interfaz usa el idioma del sistema inicialmente, pero permite selector manual persistente.

## Objetivo

Dado un entorno Linux o Windows soportado, el sistema inicia con interfaz en espanol o ingles, permite cambiar idioma y distribuye FFmpeg con avisos de licencia.

## Alcance

### Incluye

- Idiomas: espanol e ingles.
- Deteccion de idioma del sistema.
- Selector manual de idioma.
- Persistencia de preferencia de idioma.
- Catalogos de traduccion separados de la UI.
- Empaquetado para Linux.
- Empaquetado para Windows.
- Inclusion de FFmpeg en cada distribucion.
- Avisos de licencia de FFmpeg y codecs incluidos.

### No incluye

- Mas idiomas en MVP.
- Traduccion colaborativa en la app.
- Instaladores con actualizacion automatica.
- Version movil o web.
- Descarga de FFmpeg desde internet en tiempo de ejecucion.

## Comportamiento esperado

### Flujo principal

1. La app inicia.
2. Si existe idioma preferido, el sistema lo aplica.
3. Si no existe preferencia, el sistema usa idioma del sistema cuando sea espanol o ingles.
4. Si el idioma del sistema no esta soportado, el sistema usa el idioma predeterminado definido por producto: **espanol**.
5. El usuario puede cambiar idioma desde la UI.
6. El sistema persiste la preferencia.

### Flujos alternativos / edge cases

- Falta una traduccion: el sistema usa texto fallback definido.
- FFmpeg no esta disponible en la distribucion: la app informa error de instalacion/distribucion (`ffmpeg.not_found`).
- Licencia no incluida: el paquete no cumple el gate de release.

## Criterios de aceptacion

- AC-01: Dada una preferencia de idioma guardada, cuando inicia la app, entonces la UI usa ese idioma.
- AC-02: Dada ausencia de preferencia y sistema en espanol, cuando inicia la app, entonces la UI usa espanol.
- AC-03: Dada ausencia de preferencia y sistema en ingles, cuando inicia la app, entonces la UI usa ingles.
- AC-04: Dado un idioma no soportado del sistema, cuando inicia la app, entonces la UI usa el idioma predeterminado definido por producto.
- AC-05: Dado que el usuario cambia idioma, cuando confirma la seleccion, entonces la UI cambia idioma y persiste la preferencia.
- AC-06: Dado un paquete Linux o Windows, cuando se inspecciona la distribucion, entonces incluye FFmpeg y avisos de licencia requeridos.
- AC-07: Dado un paquete sin avisos de licencia FFmpeg/codecs, cuando se valida release, entonces el paquete se rechaza.

## Restricciones

- Tecnicas: traducciones en archivos separados; empaquetado con PyInstaller cuando se implemente.
- Negocio: solo Linux y Windows en MVP.
- Seguridad/legal: distribuir FFmpeg exige incluir avisos de licencia y revisar codecs incluidos.

## Empaquetado y licencias (decisión D5, 2026-08-31)

- **Empaquetado:** PyInstaller `--onedir`, tanto en Linux (`dist/automixer/`) como en Windows (`dist\AutoMixer\`).
- **FFmpeg incluido:** el binario `ffmpeg` (Linux) / `ffmpeg.exe` (Windows) se distribuye dentro del bundle, en `resources/` al lado del ejecutable. No se descarga nada en tiempo de ejecución.
- **Verificación al arrancar:** la app comprueba que FFmpeg está disponible en el bundle; si no, muestra `ffmpeg.not_found` y no permite mezclar/exportar.
- **`LICENSES.md`:** todo paquete de distribución incluye `LICENSES.md` con los avisos de licencia según las build realmente distribuidas: FFmpeg (GPLv3 u otras según configuración de los binarios), códecs incluidos (p. ej. LAME, LGPL, para MP3), PySide6 (LGPLv3) y Python (PSF License).
- **Gate de release:** un paquete sin `LICENSES.md` se rechaza en la validación de release (criterio AC-07).
- Nota: esta decisión no define scripts de build ni variable de entorno `AUTOMIXER_FFMPEG`; en desarrollo se podrá usar un `ffmpeg` del sistema, decisión de implementación fuera del MVP.

## Idioma predeterminado (decisión D6, 2026-08-31)

El idioma predeterminado de producto cuando el sistema no sea espanol/ingles es **espanol**. Este valor se aplica en el paso 4 del flujo principal y en el criterio AC-04.

## Notas

- Decisiones D5 (empaquetado y licencias) y D6 (idioma predeterminado) resueltas en este documento.

