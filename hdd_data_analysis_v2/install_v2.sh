#!/bin/bash

echo "========================================"
echo "HDD Data Analysis v2 - Instalador"
echo "========================================"
echo

# Verificar si Python está instalado
echo "[1/6] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 no está instalado"
    echo "Por favor, instala Python 3.8+ usando tu gestor de paquetes"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi
echo "✓ Python encontrado: $(python3 --version)"

# Verificar si pip está disponible
echo "[2/6] Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 no está disponible"
    echo "Por favor, instala pip3 usando tu gestor de paquetes"
    exit 1
fi
echo "✓ pip encontrado: $(pip3 --version)"

# Crear entorno virtual
echo "[3/6] Creando entorno virtual..."
if [ -d "venv" ]; then
    echo "El entorno virtual ya existe, eliminando..."
    rm -rf venv
fi
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudo crear el entorno virtual"
    exit 1
fi
echo "✓ Entorno virtual creado"

# Activar entorno virtual e instalar dependencias
echo "[4/6] Instalando dependencias..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudieron instalar las dependencias"
    exit 1
fi
echo "✓ Dependencias instaladas"

# Crear archivo de configuración de entorno
echo "[5/6] Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    cp env.example .env
    echo "✓ Archivo .env creado desde env.example"
    echo
    echo "IMPORTANTE: Edita el archivo .env con tus credenciales de base de datos"
else
    echo "✓ Archivo .env ya existe"
fi

# Crear directorios necesarios
echo "[6/6] Creando directorios necesarios..."
mkdir -p logs reports backups templates
echo "✓ Directorios creados"

# Dar permisos de ejecución a los scripts
chmod +x scripts/*.sh 2>/dev/null || true

echo
echo "========================================"
echo "INSTALACION COMPLETADA EXITOSAMENTE"
echo "========================================"
echo
echo "Próximos pasos:"
echo "1. Edita el archivo .env con tus credenciales de base de datos"
echo "2. Edita config_v2.yaml según tus necesidades"
echo "3. Ejecuta las pruebas: python tests/test_ranking_hdd.py"
echo "4. Ejecuta el análisis: python main.py"
echo
echo "Para activar el entorno virtual en el futuro:"
echo "  source venv/bin/activate"
echo 