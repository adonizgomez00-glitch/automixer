@echo off
:: AutoMixer - Lanzador Windows (equivalente a setup.exe)
:: Doble clic para instalar AutoMixer automaticamente.

echo.
echo ============================================
echo    AutoMixer - Instalador Automatico
echo ============================================
echo.

set SCRIPT_DIR=%~dp0
if exist "%SCRIPT_DIR%setup.bat" (
    call "%SCRIPT_DIR%setup.bat"
) else (
    echo [ERROR] No se encontro setup.bat.
    echo Asegurate de que todos los archivos esten en la misma carpeta.
    echo.
    pause
)
