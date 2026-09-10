@echo off
title AutoMixer - Instalador
color 0A
cls

echo ============================================
echo    AutoMixer - Instalador para Windows
echo ============================================
echo.

:: --- Verificar Python ---
echo [1/5] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python no encontrado en el PATH.
    echo Descarga Python 3.10+ desde: https://www.python.org/downloads/
    echo Marca "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo        Python %PY_VER% encontrado.

:: --- Crear entorno virtual ---
echo.
echo [2/5] Creando entorno virtual...
if exist ".venv" (
    echo        El entorno .venv ya existe. Reutilizando...
) else (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo        Entorno virtual creado.
)

:: --- Instalar dependencias ---
echo.
echo [3/5] Instalando dependencias...
call .venv\Scripts\activate.bat
pip install --upgrade pip -q
pip install -e . -q
if %errorlevel% neq 0 (
    echo [ERROR] Fallo al instalar dependencias.
    pause
    exit /b 1
)
echo        Dependencias instaladas.

:: --- Verificar FFmpeg ---
echo.
echo [4/5] Verificando FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [AVISO] FFmpeg no encontrado en el PATH.
    echo AutoMixer requiere FFmpeg para renderizar audio.
    echo.
    echo Opciones:
    echo   1) Descarga de: https://www.gyan.dev/ffmpeg/builds/
    echo   2) Extrae y agrega la carpeta bin al PATH del sistema
    echo   3) O ejecuta: winget install Gyan.FFmpeg
    echo.
) else (
    echo        FFmpeg encontrado.
)

:: --- Crear acceso directo en el escritorio ---
echo.
echo [5/5] Creando acceso directo en el escritorio...
set SCRIPT_DIR=%~dp0
set SHORTCUT_PATH=%USERPROFILE%\Desktop\AutoMixer.bat
(
    echo @echo off
    echo cd /d "%SCRIPT_DIR%"
    echo call .venv\Scripts\activate.bat
    echo python -m src.app
    echo pause
) > "%SHORTCUT_PATH%"
echo        Acceso directo creado: %SHORTCUT_PATH%

:: --- Completado ---
echo.
echo ============================================
echo    Instalacion completada!
echo ============================================
echo.
echo Para ejecutar AutoMixer:
echo   - Haz doble clic en "AutoMixer" en el escritorio
echo   - O ejecuta:  python -m src.app
echo.
set /p RUN="Desea ejecutar AutoMixer ahora? (S/N): "
if /i "%RUN%"=="S" (
    echo.
    echo Iniciando AutoMixer...
    python -m src.app
) else (
    echo.
    echo Puedes ejecutarlo despues con: python -m src.app
)
echo.
pause
