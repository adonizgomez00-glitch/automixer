# AutoMixer

Aplicación de escritorio para mezclar stems de canciones de forma local y sencilla. Importa pistas individuales (voz, batería, bajo, guitarra, etc.), clasifícalas automáticamente desde el nombre del archivo, aplica un perfil de mezcla por género y exporta el resultado final.

## Características

- **Auto-detección de tipo** desde el nombre del archivo (`_drums` → Batería, `_vocals` → Voz, `_bass` → Bajo, etc.).
- **Importación** de stems en formato MP3, FLAC y WAV.
- **Perfiles de mezcla** para Pop (predeterminado), Rock e Hip Hop, con ganancia, paneo, HPF, EQ, compresión y normalización LUFS automáticos por género/tipo.
- **Control manual** de volumen por stem (−60 a +12 dB) y desfase manual en milisegundos.
- **Barra de progreso** durante Mezclar y Exportar con bloqueo de la interfaz.
- **Vista previa** con reproductor (reproducir/pausar/detener) usando WAV temporal.
- **Exportación** a WAV 44.1 kHz/24-bit o MP3 320 kbps.
- **Interfaz bilingüe** español/inglés con selector de idioma persistente.
- **Proyectos locales** guardados en formato `.automixer` (JSON versionado) — nunca modifica los archivos originales.

## Instalación automática (recomendada)

Los instaladores configuran todo automáticamente: Python, FFmpeg, dependencias y accesos directos.

### Windows

1. Descarga o clona el repositorio
2. Haz doble clic en **`setup.bat`**
3. El instalador hará todo solo:
   - Instala Python 3.12 si no lo encuentra (via winget)
   - Instala FFmpeg si no lo encuentra (via winget o descarga directa)
   - Crea entorno virtual e instala PySide6
   - Crea un acceso directo en el escritorio
4. Al terminar, ejecuta AutoMixer desde el escritorio o con `python -m src.app`

### Linux (Ubuntu, Fedora, Arch, openSUSE)

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd automixer

# Ejecutar el instalador
chmod +x setup.sh
./setup.sh
```

El instalador hará todo solo:
- Instala Python 3 si no lo encuentra (via apt/dnf/pacman)
- Instala FFmpeg si no lo encuentra
- Instala prerrequisitos de PySide6 (libgl1, mesa)
- Crea entorno virtual e instala dependencias
- Crea un lanzador en el menú de aplicaciones
- Al terminar, ejecuta AutoMixer desde el menú o con `./automixer.sh`

## Instalación manual

Si prefieres instalar paso a paso:

```bash
# Clonar
git clone <url-del-repositorio>
cd automixer

# Python 3.10+ y FFmpeg deben estar instalados

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Instalar dependencias
pip install -e .
```

## Ejecución

```bash
python -m src.app
```

O con el lanzador generado por el instalador:

- **Linux**: `./automixer.sh` o busca "AutoMixer" en el menú de aplicaciones
- **Windows**: doble clic en "AutoMixer" en el escritorio

## Empaquetado

Para generar un bundle distribuible con PyInstaller:

```bash
pip install pyinstaller
python scripts/build.py
```

El bundle se genera en `dist/automixer/` e incluye FFmpeg y `LICENSES.md`.

## Arquitectura

```
src/
  app.py                 # composición de dependencias
  models/                # MixProject, Stem, MixProfile
  views/                 # ventana, lista de stems, reproductor
  controllers/           # eventos de la UI
  services/              # proyecto, mezcla, exportación, i18n
  ports/                 # contratos de audio y persistencia
  adapters/              # FFmpeg, QtMultimedia
  workers/               # trabajos cancelables en segundo plano
  i18n/                  # catálogos de idioma (es/en)
  utils/                 # Result, validación, auto-detección
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
| Voz | HPF, EQ, compresión según género |
| Batería | Ganancia base, EQ, compresión, referencia de tempo |
| Bajo | HPF, EQ, compresión |
| Guitarra | Paneo alternado, HPF, EQ |
| Teclados | Paneo, HPF, EQ |
| Sintetizadores | Paneo, HPF, EQ |
| Drops | Ganancia, HPF, EQ |
| Efectos | Paneo, ganancia, HPF, EQ |
| Otro | Perfil neutro (sin procesamiento) |

## Licencia

GNU General Public License v2.0. Ver [LICENSE](LICENSE) para más detalles.

## Avisos de licencia

Este software incluye FFmpeg y códecs (LAME) bajo sus respectivas licencias. Ver [LICENSES.md](LICENSES.md) para los avisos completos.
