# AutoMixer — Avisos de licencia

Este documento forma parte de la distribución de AutoMixer (decisión D5) y es
**obligatorio**: un paquete sin este fichero se rechaza en la validación de
release (SPEC010 AC-07). Los avisos son los de las bibliotecas y herramientas
realmente distribuidas.

## FFmpeg

AutoMixer distribuye binarios de **FFmpeg** (LGPLv2.1+ o GPLv2+, según la
configuración de los binarios incluidos). Se incluyen los avisos de licencia
de FFmpeg, con la posibilidad de ejercer las opciones que otorgan las
licencias (p. ej. sustituir componentes o facilitar el código fuente de los
filtros GPL si se usan). Más información:

- https://ffmpeg.org/legal.html
- https://git.ffmpeg.org/ffmpeg.git (código fuente)

## Códecs incluidos

- **LAME** (MP3 encoder, `libmp3lame`): se distribuye bajo la **LGPL**. La
  exportación MP3 de AutoMixer usa este códec.
  https://lame.sourceforge.io/

Si la distribución incluye códecs adicionales, este apartado deberá
ampliarse con sus correspondientes avisos.

## PySide6 (Qt para Python)

**PySide6** está bajo la **LGPLv3** (con obligaciones para el usuario de la
libertad de enlazar/ejecutar con versiones nuevas). AutoMixer enlaza con
PySide6 según lo permitido por dicha licencia.

- https://www.qt.io/licensing/
- https://doc.qt.io/qtforpython/licenses.html

## Python

**Python** se distribuye bajo la **PSF License Agreement**. AutoMixer incluye
un intérprete o componentes de Python empaquetados con PyInstaller.

- https://docs.python.org/3/license.html

## Empaquetado

El ejecutable se genera con **PyInstaller**, bajo la licencia de PyInstaller
(GPL, con exenciones para los artefactos que genera).
https://pyinstaller.org/en/stable/license.html

---
*Revisar antes de cada release que los avisos correspondan exactamente a los
binarios incluidos. El gate de release verifica la presencia de los términos
mínimos en este fichero.*