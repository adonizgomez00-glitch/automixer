# AutoMixer

Aplicación de escritorio para mezclar stems de canciones de forma local y sencilla. Importa pistas individuales (voz, batería, bajo, guitarra, etc.), clasifícalas manualmente, aplica un perfil de mezcla por género y exporta el resultado final.

## Características

- **Importación por drag & drop** de stems en formato MP3, FLAC y WAV.
- **Clasificación manual** de stems en 9 tipos: voz, batería, bajo, guitarra, teclados, sintetizadores, drops, efectos y Otro (perfil neutro).
- **Perfiles de mezcla** para Pop (predeterminado), Rock e Hip Hop, con ganancia, paneo, EQ, compresión y normalización LUFS automáticos por género/tipo.
- **Control manual** de volumen por stem (−60 a +12 dB) y desfase manual en milisegundos.
- **Sincronización de tempo** automática con referencia a batería (o primer stem), con umbrales de confianza.
- **Vista previa** con reproductor (reproducir/pausar/detener/posición/volumen) usando WAV temporal.
- **Exportación** a WAV 44.1 kHz/24-bit o MP3 320 kbps, con confirmación de sobrescritura.
- **Interfaz bilingüe** español/inglés con selector de idioma persistente.
- **Proyectos locales** guardados en formato `.automixer` (JSON versionado) — nunca modifica los archivos originales.

## Requisitos

- Python >= 3.10
- FFmpeg disponible en el PATH (o incluido en el bundle empaquetado)

## Instalación

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd automixer

# Crear entorno virtual e instalar dependencias
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
pip install -e .
```

## Ejecución

```bash
python -m src.app
```

O mediante el script definido en `pyproject.toml`:

```bash
automixer
```

## Empaquetado

Para generar un bundle distribuible con PyInstaller:

```bash
pip install pyinstaller
python scripts/build.py
```

Opcionalmente, especifica la carpeta de FFmpeg:

```bash
python scripts/build.py --ffmpeg-dir /ruta/a/ffmpeg
```

El bundle se genera en `dist/automixer/` e incluye FFmpeg y `LICENSES.md`.

## Arquitectura

```
src/
  app.py                 # composición de dependencias
  models/                # MixProject, Stem, MixProfile, ExportSettings
  views/                 # ventana, lista de stems, reproductor, diálogos
  controllers/           # eventos de la UI y actualización de la vista
  services/              # proyecto, mezcla, exportación, alineación, ajustes
  ports/                 # contratos de audio, reproducción y persistencia
  repositories/          # JSON de proyecto y QSettings
  adapters/              # FFmpeg, QtMultimedia, sistema de archivos
  workers/               # trabajos cancelables y señales de progreso
  i18n/                  # catálogos de idioma (es/en)
  utils/                 # Result, validación y errores
```

Patrón: **View → Controller → Service → Port → Adapter**. Inyección de dependencias manual en `app.py`.

## Formatos soportados

| Entrada | Salida |
|---------|--------|
| MP3, FLAC, WAV | WAV (44.1 kHz / 24-bit), MP3 (320 kbps) |

## Géneros y tipos de stem

**Géneros:** Pop, Rock, Hip Hop

| Tipo | Perfil |
|------|--------|
| Voz | Gain, paneo, EQ, compresión según género |
| Batería | Ganancia base, referencia de tempo |
| Bajo | Paneo alternado, HPF |
| Guitarra | Paneo alternado, EQ |
| Teclados | Paneo, EQ |
| Sintetizadores | Paneo, compresión |
| Drops | Ganancia, compresión |
| Efectos | Paneo, ganancia |
| Otro | Perfil neutro (sin procesamiento automático) |

## Licencia

GNU General Public License v2.0. Ver [LICENSE](LICENSE) para más detalles.

## Avisos de licencia

Este software incluye FFmpeg y códecs (LAME) bajo sus respectivas licencias. Ver [LICENSES.md](LICENSES.md) para los avisos completos.
