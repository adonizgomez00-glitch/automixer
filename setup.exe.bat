@echo off
:: AutoMixer - Lanzador Windows
:: Este archivo permite ejecutar el instalador haciendo doble clic.
:: Equivalente a setup.bat - redirige al script de instalacion real.

echo ============================================
echo    AutoMixer - Instalador para Windows
echo ============================================
echo.
echo Ejecutando instalador...
echo.

:: Buscar setup.bat en la misma carpeta
set SCRIPT_DIR=%~dp0
if exist "%SCRIPT_DIR%setup.bat" (
    call "%SCRIPT_DIR%setup.bat"
) else (
    echo [ERROR] No se encontro setup.bat en esta carpeta.
    echo Asegurate de que setup.bat y setup.exe esten en la misma carpeta.
    echo.
    pause
)
