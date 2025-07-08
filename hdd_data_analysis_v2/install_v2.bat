@echo off
echo ========================================
echo HDD Data Analysis v2 - Instalador
echo ========================================
echo.

:: Verificar si Python está instalado
echo [1/6] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor, instala Python 3.8+ desde https://python.org
    pause
    exit /b 1
)
echo ✓ Python encontrado

:: Verificar si pip está disponible
echo [2/6] Verificando pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip no está disponible
    echo Por favor, reinstala Python con pip incluido
    pause
    exit /b 1
)
echo ✓ pip encontrado

:: Crear entorno virtual
echo [3/6] Creando entorno virtual...
if exist "venv" (
    echo El entorno virtual ya existe, eliminando...
    rmdir /s /q venv
)
python -m venv venv
if errorlevel 1 (
    echo ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)
echo ✓ Entorno virtual creado

:: Activar entorno virtual e instalar dependencias
echo [4/6] Instalando dependencias...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)
echo ✓ Dependencias instaladas

:: Crear archivo de configuración de entorno
echo [5/6] Configurando variables de entorno...
if not exist ".env" (
    copy env.example .env
    echo ✓ Archivo .env creado desde env.example
    echo.
    echo IMPORTANTE: Edita el archivo .env con tus credenciales de base de datos
) else (
    echo ✓ Archivo .env ya existe
)

:: Crear directorios necesarios
echo [6/6] Creando directorios necesarios...
if not exist "logs" mkdir logs
if not exist "reports" mkdir reports
if not exist "backups" mkdir backups
if not exist "templates" mkdir templates
echo ✓ Directorios creados

echo.
echo ========================================
echo INSTALACION COMPLETADA EXITOSAMENTE
echo ========================================
echo.
echo Próximos pasos:
echo 1. Edita el archivo .env con tus credenciales de base de datos
echo 2. Edita config_v2.yaml según tus necesidades
echo 3. Ejecuta las pruebas: python tests\test_ranking_hdd.py
echo 4. Ejecuta el análisis: python main.py
echo.
echo Para activar el entorno virtual en el futuro:
echo   venv\Scripts\activate.bat
echo.
pause 