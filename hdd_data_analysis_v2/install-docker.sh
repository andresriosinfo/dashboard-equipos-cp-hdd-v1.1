#!/bin/bash

# Script de instalación completa para HDD Data Analysis con Docker

set -e

echo "=== INSTALACIÓN COMPLETA HDD DATA ANALYSIS CON DOCKER ==="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que Docker esté instalado
print_status "Verificando instalación de Docker..."
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado. Por favor, instale Docker Desktop primero."
    echo "Descargar desde: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Verificar que Docker esté ejecutándose
if ! docker info &> /dev/null; then
    print_error "Docker no está ejecutándose. Por favor, inicie Docker Desktop."
    exit 1
fi

print_success "Docker está instalado y ejecutándose"

# Verificar que Docker Compose esté disponible
print_status "Verificando Docker Compose..."
if ! docker-compose --version &> /dev/null; then
    print_warning "Docker Compose no está disponible. Algunas funciones pueden no funcionar."
else
    print_success "Docker Compose está disponible"
fi

# Crear directorio de logs si no existe
print_status "Creando directorio de logs..."
mkdir -p logs
chmod 755 logs
print_success "Directorio de logs creado"

# Configurar archivo de variables de entorno
print_status "Configurando variables de entorno..."
if [ ! -f .env ]; then
    if [ -f env.example ]; then
        cp env.example .env
        print_success "Archivo .env creado desde env.example"
        print_warning "Revisa y edita el archivo .env si necesitas cambiar la configuración de la base de datos"
    else
        print_warning "No se encontró env.example. Deberás crear el archivo .env manualmente."
    fi
else
    print_success "Archivo .env ya existe"
fi

# Hacer scripts ejecutables
print_status "Configurando scripts de ejecución..."
chmod +x scripts/*.sh 2>/dev/null || true
print_success "Scripts configurados"

# Construir imagen Docker
print_status "Construyendo imagen Docker..."
if docker build -t hdd-data-analysis:latest .; then
    print_success "Imagen Docker construida exitosamente"
else
    print_error "Error al construir la imagen Docker"
    exit 1
fi

# Verificar que la imagen se construyó correctamente
print_status "Verificando imagen construida..."
if docker images | grep -q hdd-data-analysis; then
    print_success "Imagen verificada correctamente"
else
    print_error "La imagen no se construyó correctamente"
    exit 1
fi

echo ""
echo "=== INSTALACIÓN COMPLETADA ==="
print_success "HDD Data Analysis está listo para usar con Docker"
echo ""
echo "📋 Comandos disponibles:"
echo "  • Ejecutar análisis una vez:"
echo "    ./scripts/docker-run.sh once"
echo ""
echo "  • Ejecutar análisis programado:"
echo "    ./scripts/docker-run.sh scheduled"
echo ""
echo "  • Ver logs:"
echo "    ./scripts/docker-run.sh logs"
echo ""
echo "  • Detener contenedor:"
echo "    ./scripts/docker-run.sh stop"
echo ""
echo "📖 Para más información, consulta:"
echo "  • QUICK_START.md - Guía de inicio rápido"
echo "  • DOCKER_README.md - Documentación completa"
echo ""
print_success "¡Instalación completada exitosamente!" 