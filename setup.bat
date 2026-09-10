@echo off
title AutoMixer - Instalador Automatico
color 0A
cls

echo ============================================
echo    AutoMixer - Instalador Automatico
echo ============================================
echo.

:: --- Verificar/Instalar Python ---
echo [1/6] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo        Python no encontrado. Intentando instalar...
    where winget >nul 2>&1
    if %errorlevel% equ 0 (
        echo        Instalando Python via winget...
        winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements
        if %errorlevel% neq 0 (
            echo [ERROR] No se pudo instalar Python automaticamente.
            echo Descarga manualmente: https://www.python.org/downloads/
            pause
            exit /b 1
        )
        echo        Python instalado. Reiniciando script...
        set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
    ) else (
        echo [ERROR] winget no disponible. Instala Python manualmente:
        echo https://www.python.org/downloads/
        echo Marca "Add Python to PATH" durante la instalacion.
        pause
        exit /b 1
    )
)
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python instalado pero no se encuentra en PATH.
    echo Cierra y vuelve a abrir la terminal, o reinicia el PC.
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo        Python %PY_VER% listo.

:: --- Crear entorno virtual ---
echo.
echo [2/6] Creando entorno virtual...
if exist ".venv" (
    echo        .venv ya existe. Reutilizando...
) else (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo        Entorno virtual creado.
)

:: --- Activar entorno e instalar dependencias ---
echo.
echo [3/6] Instalando dependencias de Python...
call .venv\Scripts\activate.bat
pip install --upgrade pip -q 2>nul
pip install -e . -q
if %errorlevel% neq 0 (
    echo [ERROR] Fallo al instalar dependencias.
    pause
    exit /b 1
)
echo        Dependencias instaladas (PySide6, etc.).

:: --- Verificar/Instalar FFmpeg ---
echo.
echo [4/6] Verificando FFmpeg...
set FFMPEG_OK=0
ffmpeg -version >nul 2>&1
if %errorlevel% equ 0 (
    set FFMPEG_OK=1
    echo        FFmpeg encontrado en PATH.
)

if "%FFMPEG_OK%"=="0" (
    :: Verificar si ya esta descargado en la carpeta del proyecto
    if exist "%~dp0ffmpeg\bin\ffmpeg.exe" (
        set "PATH=%~dp0ffmpeg\bin;%PATH%"
        set FFMPEG_OK=1
        echo        FFmpeg encontrado en carpeta local.
    )
)

if "%FFMPEG_OK%"=="0" (
    echo        FFmpeg no encontrado. Intentando instalar...
    where winget >nul 2>&1
    if %errorlevel% equ 0 (
        echo        Instalando FFmpeg via winget...
        winget install Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
        if %errorlevel% equ 0 (
            set FFMPEG_OK=1
            echo        FFmpeg instalado.
        )
    )

    if "%FFMPEG_OK%"=="0" (
        :: Descargar ffmpeg manualmente
        echo        Descargando FFmpeg...
        set FFMPEG_DIR=%~dp0ffmpeg
        if not exist "%FFMPEG_DIR%" mkdir "%FFMPEG_DIR%"
        powershell -Command "& {$url='https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'; $zip='%TEMP%\ffmpeg.zip'; $dest='%FFMPEG_DIR%'; Write-Host 'Descargando...'; Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing; Write-Host 'Extrayendo...'; Expand-Archive -Path $zip -DestinationPath $dest -Force; $found=Get-ChildItem -Path $dest -Recurse -Filter 'ffmpeg.exe' | Select-Object -First 1; if($found){$bin=$found.DirectoryName; Copy-Item \"$bin\*\" \"$dest\bin\" -Force}; Remove-Item $zip -Force; Write-Host 'Listo.'}"
        if exist "%FFMPEG_DIR%\bin\ffmpeg.exe" (
            set "PATH=%FFMPEG_DIR%\bin;%PATH%"
            set FFMPEG_OK=1
            echo        FFmpeg descargado y configurado.
        ) else (
            echo.
            echo [AVISO] No se pudo instalar FFmpeg automaticamente.
            echo Instala manualmente: https://www.gyan.dev/ffmpeg/builds/
            echo O ejecuta: winget install Gyan.FFmpeg
            echo.
        )
    )
)

:: --- Crear acceso directo en el escritorio ---
echo.
echo [5/6] Creando acceso directo en el escritorio...
set SCRIPT_DIR=%~dp0
set SHORTCUT_PATH=%USERPROFILE%\Desktop\AutoMixer.bat
(
    echo @echo off
    echo cd /d "%SCRIPT_DIR%"
    echo call .venv\Scripts\activate.bat
    echo.
    :: Agregar FFmpeg al PATH si esta en la carpeta local
    echo if exist "%SCRIPT_DIR%ffmpeg\bin" set "PATH=%SCRIPT_DIR%ffmpeg\bin;%%PATH%%"
    echo python -m src.app
    echo pause
) > "%SHORTCUT_PATH%"
echo        Acceso directo: %SHORTCUT_PATH%

:: --- Crear lanzador .bat en la carpeta ---
set LAUNCHER=%SCRIPT_DIR%automixer.bat
(
    echo @echo off
    echo cd /d "%SCRIPT_DIR%"
    echo call .venv\Scripts\activate.bat
    echo if exist "%SCRIPT_DIR%ffmpeg\bin" set "PATH=%SCRIPT_DIR%ffmpeg\bin;%%PATH%%"
    echo python -m src.app
) > "%LAUNCHER%"
echo        Lanzador: %LAUNCHER%

:: --- Completado ---
echo.
echo ============================================
echo    Instalacion completada!
echo ============================================
echo.
echo AutoMixer esta listo para usar.
echo.
echo Para ejecutar:
echo   - Doble clic en "AutoMixer" en el escritorio
echo   - O ejecuta:  automixer.bat
echo   - O ejecuta:  python -m src.app
echo.
set /p RUN="Ejecutar AutoMixer ahora? (S/N): "
if /i "%RUN%"=="S" (
    echo.
    echo Iniciando AutoMixer...
    python -m src.app
)
echo.
