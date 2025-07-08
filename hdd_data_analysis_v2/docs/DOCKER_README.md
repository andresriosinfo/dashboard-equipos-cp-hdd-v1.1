# HDD Data Analysis - Docker Deployment Guide

## 📋 Descripción

HDD Data Analysis es una aplicación Python que analiza datos de discos duros (HDD) desde una base de datos SQL Server. La aplicación procesa datos de la tabla `nv_hdd_history` y genera métricas de análisis que se guardan en `nv_hdd_an_resultados`.

## 🐳 Dockerización

Este proyecto está completamente dockerizado para facilitar su despliegue y ejecución en cualquier entorno.

## 📁 Estructura del Proyecto

```
hdd_data_analysis/
├── Dockerfile                 # Configuración de la imagen Docker
├── docker-compose.yml         # Orquestación de servicios
├── .dockerignore             # Archivos a ignorar en el build
├── env.example               # Variables de entorno de ejemplo
├── hdd_config_params.yaml    # Configuración de la aplicación
├── main.py                   # Punto de entrada principal
├── requirements.txt          # Dependencias de Python
├── scripts/                  # Scripts de automatización
│   ├── docker-build.sh      # Script de construcción (Linux/Mac)
│   ├── docker-run.sh        # Script de ejecución (Linux/Mac)
│   └── docker-run.bat       # Script de ejecución (Windows)
└── logs/                     # Directorio de logs (se monta como volumen)
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- Docker Desktop instalado y ejecutándose
- Docker Compose (incluido en Docker Desktop)
- Acceso a la base de datos SQL Server

### 1. Clonar el Proyecto

```bash
git clone <repository-url>
cd hdd_data_analysis
```

### 2. Configurar Variables de Entorno

Copiar el archivo de ejemplo y configurar las variables:

```bash
cp env.example .env
```

Editar `.env` con tus configuraciones:

```env
# Configuración de Base de Datos SQL Server
DB_HOST=10.147.17.185
DB_PORT=1433
DB_NAME=cmpc_20240925_093000
DB_USER=otms
DB_PASSWORD=Password1

# Configuración de la Aplicación
LOG_LEVEL=INFO
```

### 3. Construir la Imagen Docker

#### Opción A: Usando Script (Recomendado)

**Linux/Mac:**
```bash
chmod +x scripts/docker-build.sh
./scripts/docker-build.sh
```

**Windows:**
```cmd
scripts\docker-build.bat build
```

#### Opción B: Comando Directo

```bash
docker build -t hdd-data-analysis:latest .
```

## 🏃‍♂️ Ejecución

### Ejecución Manual (Una Sola Vez)

#### Opción A: Usando Script (Recomendado)

**Linux/Mac:**
```bash
./scripts/docker-run.sh once
```

**Windows:**
```cmd
scripts\docker-run.bat once
```

#### Opción B: Comando Directo

```bash
docker run --rm \
  -v "$(pwd)/logs:/app/logs" \
  -v "$(pwd)/hdd_config_params.yaml:/app/hdd_config_params.yaml:ro" \
  hdd-data-analysis:latest \
  python main.py --run-once
```

#### Opción C: Docker Compose

```bash
docker-compose --profile manual up hdd-data-analysis-once
```

### Ejecución Programada (Cada 24 Horas)

#### Opción A: Usando Script (Recomendado)

**Linux/Mac:**
```bash
./scripts/docker-run.sh scheduled
```

**Windows:**
```cmd
scripts\docker-run.bat scheduled
```

#### Opción B: Docker Compose

```bash
docker-compose up -d hdd-data-analysis
```

### Gestión del Contenedor

#### Ver Logs

**Linux/Mac:**
```bash
./scripts/docker-run.sh logs
```

**Windows:**
```cmd
scripts\docker-run.bat logs
```

#### Detener Contenedor

**Linux/Mac:**
```bash
./scripts/docker-run.sh stop
```

**Windows:**
```cmd
scripts\docker-run.bat stop
```

#### Docker Compose

```bash
# Ver logs
docker-compose logs -f hdd-data-analysis

# Detener servicios
docker-compose down
```

## 📊 Monitoreo y Logs

### Ubicación de Logs

Los logs se guardan en el directorio `logs/` del proyecto:

- `hdd_data_analysis_YYYYMMDD.log` - Logs diarios de la aplicación
- Logs del contenedor Docker

### Ver Logs en Tiempo Real

```bash
# Logs de la aplicación
tail -f logs/hdd_data_analysis_$(date +%Y%m%d).log

# Logs del contenedor
docker logs -f hdd-data-analysis-run
```

## 🔧 Configuración Avanzada

### Variables de Entorno Disponibles

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `DB_HOST` | Host de la base de datos | `10.147.17.185` |
| `DB_PORT` | Puerto de la base de datos | `1433` |
| `DB_NAME` | Nombre de la base de datos | `cmpc_20240925_093000` |
| `DB_USER` | Usuario de la base de datos | `otms` |
| `DB_PASSWORD` | Contraseña de la base de datos | `Password1` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |

### Configuración de Análisis

Editar `hdd_config_params.yaml` para modificar parámetros de análisis:

```yaml
dias_analisis: 7                    # Días hacia atrás para análisis
umbral_maximo: 100.0               # Valor máximo aceptable
umbral_minimo: 0.0                 # Valor mínimo aceptable
tamano_lote: 1000                  # Registros por lote
max_hilos: 4                       # Hilos de procesamiento
```

## 🗄️ Base de Datos

### Tablas Requeridas

#### Tabla de Origen
- `nv_hdd_history` - Datos de uso de discos duros

#### Tabla de Resultados
- `nv_hdd_an_resultados` - Resultados de análisis (se crea automáticamente)

### Estructura de la Tabla de Resultados

```sql
CREATE TABLE dbo.nv_hdd_an_resultados (
    id VARCHAR(50) PRIMARY KEY,
    unidad VARCHAR(100),
    equipo VARCHAR(100),
    fecha_ejecucion_del_codigo DATETIME,
    metrica VARCHAR(50),
    valor_1 FLOAT,
    valor_2 FLOAT,
    valor_3 FLOAT,
    valor_4 FLOAT,
    valor_5 FLOAT,
    valor_6 FLOAT,
    valor_7 FLOAT
);
```

## 🔍 Troubleshooting

### Problemas Comunes

#### 1. Error de Conexión a Base de Datos

**Síntoma:** `pyodbc.OperationalError: ('08001', '[08001] [unixODBC][Microsoft][ODBC Driver 18 for SQL Server]...')`

**Solución:**
- Verificar que la base de datos esté accesible desde el contenedor
- Confirmar credenciales en `.env`
- Verificar firewall y configuración de red

#### 2. Error de Permisos en Logs

**Síntoma:** `PermissionError: [Errno 13] Permission denied`

**Solución:**
```bash
# Crear directorio de logs con permisos correctos
mkdir -p logs
chmod 755 logs
```

#### 3. Contenedor No Inicia

**Síntoma:** `docker: Error response from daemon: ...`

**Solución:**
```bash
# Verificar logs del contenedor
docker logs hdd-data-analysis-run

# Reconstruir imagen
docker build --no-cache -t hdd-data-analysis:latest .
```

### Comandos de Diagnóstico

```bash
# Verificar estado del contenedor
docker ps -a

# Ver logs detallados
docker logs hdd-data-analysis-run

# Ejecutar contenedor en modo interactivo
docker run -it --rm hdd-data-analysis:latest /bin/bash

# Verificar conectividad de red
docker run --rm hdd-data-analysis:latest ping 10.147.17.185
```

## 📈 Métricas Generadas

La aplicación genera las siguientes métricas:

1. **Máximo** - Equipo con mayor uso de disco
2. **Mínimo** - Equipo con menor uso de disco
3. **Inestabilidad** - Equipo con mayor variabilidad en uso
4. **Tasa de Cambio** - Equipo con mayor velocidad de cambio

Cada métrica se asocia a un equipo específico y una unidad de disco.

## 🔄 Automatización

### Cron Job (Linux/Mac)

Para ejecutar automáticamente cada día a las 2:00 AM:

```bash
# Editar crontab
crontab -e

# Agregar línea
0 2 * * * cd /path/to/hdd_data_analysis && ./scripts/docker-run.sh once
```

### Task Scheduler (Windows)

1. Abrir "Programador de tareas"
2. Crear tarea básica
3. Programar para ejecutar diariamente a las 2:00 AM
4. Acción: Iniciar programa
5. Programa: `scripts\docker-run.bat`
6. Argumentos: `once`

## 📞 Soporte

Para reportar problemas o solicitar ayuda:

1. Revisar la sección de troubleshooting
2. Verificar logs de la aplicación
3. Contactar al equipo de desarrollo

## 📝 Changelog

### v1.0.0
- Implementación inicial del análisis HDD
- Dockerización completa
- Scripts de automatización
- Documentación completa 