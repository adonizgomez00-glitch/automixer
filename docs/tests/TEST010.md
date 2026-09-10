# TEST010 — Pruebas funcionales: Internacionalización, empaquetado y licencias

**Fuente:** `SPEC010` · **Criterios cubiertos:** AC-01 a AC-07 · **Estado:** borrador, sin ejecución · **Fecha:** 2026-08-31

## TEST010-AC-01 — Preferencia de idioma guardada se aplica

- **Dado** una preferencia de idioma guardada (p. ej. `en`).
- **Cuando** inicia la aplicación.
- **Entonces** la UI usa ese idioma.

## TEST010-AC-02 — Sistema en español sin preferencia usa español

- **Dado** ausencia de preferencia y un idioma de sistema `es`.
- **Cuando** inicia la aplicación.
- **Entonces** la UI usa español.

## TEST010-AC-03 — Sistema en inglés sin preferencia usa inglés

- **Dado** ausencia de preferencia y un idioma de sistema `en`.
- **Cuando** inicia la aplicación.
- **Entonces** la UI usa inglés.

## TEST010-AC-04 — Idioma no soportado usa el predeterminado de producto

- **Dado** un idioma de sistema no soportado (ni `es` ni `en`) y sin preferencia.
- **Cuando** inicia la aplicación.
- **Entonces** la UI usa el idioma predeterminado de producto: **español** (decisión D6).

## TEST010-AC-05 — Cambiar idioma persiste la preferencia

- **Dado** que el usuario abre el selector de idioma.
- **Cuando** confirma una selección distinta.
- **Entonces** la UI cambia de idioma al instante y la preferencia queda persistida (QSettings).

## TEST010-AC-06 — El paquete incluye FFmpeg y avisos de licencia

- **Dado** un paquete Linux (`dist/automixer/`) o Windows (`dist\AutoMixer\`).
- **Cuando** se inspecciona la distribución.
- **Entonces** incluye `ffmpeg`/`ffmpeg.exe` en `resources/` y `LICENSES.md` con los avisos requeridos.

## TEST010-AC-07 — Paquete sin licencias se rechaza en release

- **Dado** un paquete sin avisos de licencia FFmpeg/códecs.
- **Cuando** se valida el release.
- **Entonces** el paquete se rechaza (gate de release).

## Notas

- `ffmpeg.not_found` se muestra si el binario falta al arrancar; ver `TEST009` para la transformación de fallos.