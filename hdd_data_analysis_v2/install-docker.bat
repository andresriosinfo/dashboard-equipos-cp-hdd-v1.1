@echo off
REM Script de instalación completa para HDD Data Analysis con Docker en Windows

echo === INSTALACIÓN COMPLETA HDD DATA ANALYSIS CON DOCKER ===
echo.

REM Verificar que Docker esté instalado
echo [INFO] Verificando instalación de Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no está instalado. Por favor, instale Docker Desktop primero.
    echo Descargar desde: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Verificar que Docker esté ejecutándose
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no está ejecutándose. Por favor, inicie Docker Desktop.
    pause
    exit /b 1
)

echo [SUCCESS] Docker está instalado y ejecutándose

REM Verificar que Docker Compose esté disponible
echo [INFO] Verificando Docker Compose...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Docker Compose no está disponible. Algunas funciones pueden no funcionar.
) else (
    echo [SUCCESS] Docker Compose está disponible
)

REM Crear directorio de logs si no existe
echo [INFO] Creando directorio de logs...
if not exist logs mkdir logs
echo [SUCCESS] Directorio de logs creado

REM Configurar archivo de variables de entorno
echo [INFO] Configurando variables de entorno...
if not exist .env (
    if exist env.example (
        copy env.example .env >nul
        echo [SUCCESS] Archivo .env creado desde env.example
        echo [WARNING] Revisa y edita el archivo .env si necesitas cambiar la configuración de la base de datos
    ) else (
        echo [WARNING] No se encontró env.example. Deberás crear el archivo .env manualmente.
    )
) else (
    echo [SUCCESS] Archivo .env ya existe
)

REM Construir imagen Docker
echo [INFO] Construyendo imagen Docker...
docker build -t hdd-data-analysis:latest .
if errorlevel 1 (
    echo [ERROR] Error al construir la imagen Docker
    pause
    exit /b 1
)
echo [SUCCESS] Imagen Docker construida exitosamente

REM Verificar que la imagen se construyó correctamente
echo [INFO] Verificando imagen construida...
docker images | findstr hdd-data-analysis >nul
if errorlevel 1 (
    echo [ERROR] La imagen no se construyó correctamente
    pause
    exit /b 1
)
echo [SUCCESS] Imagen verificada correctamente

echo.
echo === INSTALACIÓN COMPLETADA ===
echo [SUCCESS] HDD Data Analysis está listo para usar con Docker
echo.
echo 📋 Comandos disponibles:
echo   • Ejecutar análisis una vez:
echo     scripts\docker-run.bat once
echo.
echo   • Ejecutar análisis programado:
echo     scripts\docker-run.bat scheduled
echo.
echo   • Ver logs:
echo     scripts\docker-run.bat logs
echo.
echo   • Detener contenedor:
echo     scripts\docker-run.bat stop
echo.
echo 📖 Para más información, consulta:
echo   • QUICK_START.md - Guía de inicio rápido
echo   • DOCKER_README.md - Documentación completa
echo.
echo [SUCCESS] ¡Instalación completada exitosamente!
pause 