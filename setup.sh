#!/usr/bin/env bash
# AutoMixer - Instalador para Linux
set -e

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}    AutoMixer - Instalador para Linux${NC}"
echo -e "${GREEN}============================================${NC}"
echo

# --- Verificar Python ---
echo -e "${BOLD}[1/6] Verificando Python...${NC}"
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}[ERROR] Python3 no encontrado.${NC}"
    echo "Instala Python 3.10+:"
    echo "  Ubuntu/Debian:  sudo apt install python3 python3-venv python3-pip"
    echo "  Fedora:         sudo dnf install python3 python3-virtualenv"
    echo "  Arch:           sudo pacman -S python python-virtualenv"
    exit 1
fi
PY_VER=$(python3 --version 2>&1 | awk '{print $2}')
echo "        Python ${PY_VER} encontrado."

# --- Verificar FFmpeg ---
echo
echo -e "${BOLD}[2/6] Verificando FFmpeg...${NC}"
if command -v ffmpeg &>/dev/null; then
    echo "        FFmpeg encontrado."
else
    echo -e "${YELLOW}[AVISO] FFmpeg no encontrado.${NC}"
    echo "AutoMixer requiere FFmpeg para renderizar audio."
    echo
    echo "Instalar:"
    echo "  Ubuntu/Debian:  sudo apt install ffmpeg"
    echo "  Fedora:         sudo dnf install ffmpeg"
    echo "  Arch:           sudo pacman -S ffmpeg"
    echo
    read -p "Continuar sin FFmpeg? (s/N): " INSTALL_ANYWAY
    if [[ ! "$INSTALL_ANYWAY" =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

# --- Crear entorno virtual ---
echo
echo -e "${BOLD}[3/6] Creando entorno virtual...${NC}"
if [ -d "$SCRIPT_DIR/.venv" ]; then
    echo "        El entorno .venv ya existe. Reutilizando..."
else
    python3 -m venv "$SCRIPT_DIR/.venv"
    echo "        Entorno virtual creado."
fi

# --- Instalar dependencias ---
echo
echo -e "${BOLD}[4/6] Instalando dependencias...${NC}"
source "$SCRIPT_DIR/.venv/bin/activate"
pip install --upgrade pip -q
pip install -e "$SCRIPT_DIR" -q
echo "        Dependencias instaladas."

# --- Crear lanzador .desktop ---
echo
echo -e "${BOLD}[5/6] Creando lanzador de aplicacion...${NC}"
DESKTOP_FILE="$HOME/.local/share/applications/automixer.desktop"
mkdir -p "$HOME/.local/share/applications"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=AutoMixer
Comment=Mezcla local de stems de cancion
Exec=bash -c 'cd "$SCRIPT_DIR" && "$SCRIPT_DIR/.venv/bin/python" -m src.app'
Icon=audio-x-generic
Terminal=false
Type=Application
Categories=Audio;Music;
Keywords=audio;mix;stems;
EOF

echo "        Lanzador creado: $DESKTOP_FILE"

# --- Crear lanzador rapido ---
echo
echo -e "${BOLD}[6/6] Creando lanzador rapido...${NC}"
LAUNCHER="$SCRIPT_DIR/automixer.sh"
cat > "$LAUNCHER" << 'LAUNCHEREOF'
#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/.venv/bin/activate"
python -m src.app
LAUNCHEREOF
chmod +x "$LAUNCHER"
echo "        Lanzador rapido: $LAUNCHER"

# --- Completado ---
echo
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}    Instalacion completada!${NC}"
echo -e "${GREEN}============================================${NC}"
echo
echo "Para ejecutar AutoMixer:"
echo "  - Busca 'AutoMixer' en tu menu de aplicaciones"
echo "  - O ejecuta:  ./automixer.sh"
echo "  - O ejecuta:  python3 -m src.app"
echo
read -p "Desea ejecutar AutoMixer ahora? (S/N): " RUN
if [[ "$RUN" =~ ^[Ss]$ ]]; then
    echo
    echo "Iniciando AutoMixer..."
    python3 -m src.app
else
    echo
    echo "Puedes ejecutarlo despues con: ./automixer.sh"
fi
