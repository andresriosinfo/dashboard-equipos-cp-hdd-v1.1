#!/bin/bash

echo "========================================"
echo "CP Data Analysis v2 - Instalador"
echo "========================================"
echo

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 no está instalado"
    echo "Por favor instala Python 3.8 o superior"
    exit 1
fi

echo "Python encontrado:"
python3 --version
echo

# Verificar si pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 no está instalado"
    echo "Por favor instala pip3"
    exit 1
fi

# Crear directorio de logs si no existe
if [ ! -d "logs" ]; then
    echo "Creando directorio de logs..."
    mkdir -p logs
fi

# Crear directorio de reportes si no existe
if [ ! -d "reportes" ]; then
    echo "Creando directorio de reportes..."
    mkdir -p reportes
fi

# Instalar dependencias
echo "Instalando dependencias..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Error al instalar dependencias"
    exit 1
fi

# Dar permisos de ejecución a los scripts
chmod +x scripts/*.py
chmod +x tests/*.py

echo
echo "========================================"
echo "Instalación completada exitosamente"
echo "========================================"
echo
echo "Próximos pasos:"
echo "1. Configurar config.py con los parámetros de base de datos"
echo "2. Verificar config_v2.yaml según necesidades"
echo "3. Ejecutar: python3 main.py"
echo 