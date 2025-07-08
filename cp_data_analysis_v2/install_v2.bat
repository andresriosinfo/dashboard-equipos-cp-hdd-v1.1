@echo off
echo ========================================
echo CP Data Analysis v2 - Instalador
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instala Python 3.8 o superior
    pause
    exit /b 1
)

echo Python encontrado:
python --version
echo.

REM Crear directorio de logs si no existe
if not exist "logs" (
    echo Creando directorio de logs...
    mkdir logs
)

REM Crear directorio de reportes si no existe
if not exist "reportes" (
    echo Creando directorio de reportes...
    mkdir reportes
)

REM Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Error al instalar dependencias
    pause
    exit /b 1
)

echo.
echo ========================================
echo Instalación completada exitosamente
echo ========================================
echo.
echo Próximos pasos:
echo 1. Configurar config.py con los parámetros de base de datos
echo 2. Verificar config_v2.yaml según necesidades
echo 3. Ejecutar: python main.py
echo.
pause 