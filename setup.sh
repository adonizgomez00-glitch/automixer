#!/usr/bin/env bash
# AutoMixer - Instalador Automatico para Linux
# Instala todo automaticamente: Python, FFmpeg, dependencias
set -e

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
CYAN="\033[0;36m"
NC="\033[0m"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}    AutoMixer - Instalador Automatico${NC}"
echo -e "${GREEN}============================================${NC}"
echo

# --- Detectar gestor de paquetes ---
detect_pkg_manager() {
    if command -v apt-get &>/dev/null; then
        echo "apt"
    elif command -v dnf &>/dev/null; then
        echo "dnf"
    elif command -v pacman &>/dev/null; then
        echo "pacman"
    elif command -v zypper &>/dev/null; then
        echo "zypper"
    else
        echo "unknown"
    fi
}

PKG_MANAGER=$(detect_pkg_manager)

install_package() {
    local pkg="$1"
    case "$PKG_MANAGER" in
        apt)    sudo apt-get install -y "$pkg" ;;
        dnf)    sudo dnf install -y "$pkg" ;;
        pacman) sudo pacman -S --noconfirm "$pkg" ;;
        zypper) sudo zypper install -y "$pkg" ;;
    esac
}

# --- Verificar/Instalar Python ---
echo -e "${BOLD}[1/6] Verificando Python...${NC}"
PYTHON_CMD=""
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
fi

if [ -n "$PYTHON_CMD" ]; then
    PY_VER=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
    if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 10 ]; then
        echo "        Python ${PY_VER} encontrado."
    else
        echo "        Python ${PY_VER} es muy viejo (requiere 3.10+). Instalando..."
        PYTHON_CMD=""
    fi
else
    echo "        Python no encontrado. Instalando..."
fi

if [ -z "$PYTHON_CMD" ]; then
    case "$PKG_MANAGER" in
        apt)
            sudo apt-get update -qq
            sudo apt-get install -y python3 python3-venv python3-pip python3-tk
            ;;
        dnf)
            sudo dnf install -y python3 python3-virtualenv python3-pip python3-tkinter
            ;;
        pacman)
            sudo pacman -S --noconfirm python python-virtualenv python-pip tk
            ;;
        zypper)
            sudo zypper install -y python3 python3-virtualenv python3-pip python3-tk
            ;;
        *)
            echo -e "${RED}[ERROR] No se pudo detectar el gestor de paquetes.${NC}"
            echo "Instala Python 3.10+ manualmente."
            exit 1
            ;;
    esac
    PYTHON_CMD="python3"
    echo "        Python instalado."
fi

# --- Verificar/Instalar FFmpeg ---
echo
echo -e "${BOLD}[2/6] Verificando FFmpeg...${NC}"
if command -v ffmpeg &>/dev/null; then
    echo "        FFmpeg encontrado."
else
    echo "        FFmpeg no encontrado. Instalando..."
    case "$PKG_MANAGER" in
        apt)
            sudo apt-get update -qq
            sudo apt-get install -y ffmpeg
            ;;
        dnf)
            sudo dnf install -y ffmpeg || {
                echo "        Intentando con RPM Fusion..."
                sudo dnf install -y https://download1.rpmfusion.org/free/el/rpmfusion-free-release-$(rpm -E %rhel).noarch.rpm 2>/dev/null || true
                sudo dnf install -y ffmpeg
            }
            ;;
        pacman)
            sudo pacman -S --noconfirm ffmpeg
            ;;
        zypper)
            sudo zypper install -y ffmpeg || sudo zypper install -y ffmpeg-4
            ;;
    esac
    if command -v ffmpeg &>/dev/null; then
        echo "        FFmpeg instalado."
    else
        echo -e "${YELLOW}[AVISO] No se pudo instalar FFmpeg automaticamente.${NC}"
        echo "Instala manualmente: sudo apt install ffmpeg"
    fi
fi

# --- Verificar/Instalar PySide6 prerequisitos ---
echo
echo -e "${BOLD}[3/6] Verificando prerrequisitos de PySide6...${NC}"
if [ "$PKG_MANAGER" = "apt" ]; then
    # PySide6 necesita libgl1 y libegl1 en Ubuntu/Debian
    dpkg -l libgl1-mesa-glx &>/dev/null 2>&1 || dpkg -l libgl1 &>/dev/null 2>&1 || {
        echo "        Instalando librerias de OpenGL..."
        sudo apt-get install -y libgl1-mesa-glx libegl1 libxkbcommon0 libfontconfig1 2>/dev/null || true
    }
elif [ "$PKG_MANAGER" = "pacman" ]; then
    pacman -Q mesa &>/dev/null 2>&1 || sudo pacman -S --noconfirm mesa 2>/dev/null || true
elif [ "$PKG_MANAGER" = "dnf" ]; then
    rpm -q mesa-libGL &>/dev/null 2>&1 || sudo dnf install -y mesa-libGL 2>/dev/null || true
fi
echo "        Prerrequisitos listos."

# --- Crear entorno virtual ---
echo
echo -e "${BOLD}[4/6] Creando entorno virtual...${NC}"
if [ -d "$SCRIPT_DIR/.venv" ]; then
    echo "        .venv ya existe. Reutilizando..."
else
    $PYTHON_CMD -m venv "$SCRIPT_DIR/.venv"
    echo "        Entorno virtual creado."
fi

# --- Instalar dependencias ---
echo
echo -e "${BOLD}[5/6] Instalando dependencias de Python...${NC}"
source "$SCRIPT_DIR/.venv/bin/activate"
pip install --upgrade pip -q 2>/dev/null
pip install -e "$SCRIPT_DIR" -q
echo "        Dependencias instaladas (PySide6, etc.)."

# --- Crear lanzadores ---
echo
echo -e "${BOLD}[6/6] Creando lanzadores...${NC}"

# Lanzador .desktop
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
echo "        Lanzador de aplicacion: $DESKTOP_FILE"

# Lanzador rapido
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
echo "Todo instalado automaticamente."
echo
echo "Para ejecutar AutoMixer:"
echo "  - Busca 'AutoMixer' en tu menu de aplicaciones"
echo "  - O ejecuta:  ./automixer.sh"
echo "  - O ejecuta:  python3 -m src.app"
echo
read -p "Ejecutar AutoMixer ahora? (S/N): " RUN
if [[ "$RUN" =~ ^[Ss]$ ]]; then
    echo
    echo "Iniciando AutoMixer..."
    python3 -m src.app
fi
