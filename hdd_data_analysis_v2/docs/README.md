# HDD Data Analysis

## 📋 Descripción

HDD Data Analysis es una aplicación Python que analiza datos de discos duros (HDD) desde una base de datos SQL Server. La aplicación procesa datos de la tabla `nv_hdd_history` y genera métricas de análisis que se guardan en `nv_hdd_an_resultados`.

## 🚀 Inicio Rápido

### Con Docker (Recomendado)

1. **Instalación automática:**
   ```bash
   # Linux/Mac
   chmod +x install-docker.sh
   ./install-docker.sh
   
   # Windows
   install-docker.bat
   ```

2. **Ejecutar análisis:**
   ```bash
   # Una sola vez
   ./scripts/docker-run.sh once
   
   # Programado (cada 24 horas)
   ./scripts/docker-run.sh scheduled
   ```

### Sin Docker

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar base de datos:**
   ```bash
   cp env.example .env
   # Editar .env con tus configuraciones
   ```

3. **Ejecutar:**
   ```bash
   python main.py --run-once
   ```

## 📁 Estructura del Proyecto

```
hdd_data_analysis/
├── Dockerfile                 # Configuración Docker
├── docker-compose.yml         # Orquestación de servicios
├── .dockerignore             # Archivos a ignorar en Docker
├── env.example               # Variables de entorno de ejemplo
├── hdd_config_params.yaml    # Configuración de análisis
├── main.py                   # Punto de entrada principal
├── requirements.txt          # Dependencias de Python
├── scripts/                  # Scripts de automatización
│   ├── docker-build.sh      # Construir imagen (Linux/Mac)
│   ├── docker-run.sh        # Ejecutar con Docker (Linux/Mac)
│   └── docker-run.bat       # Ejecutar con Docker (Windows)
├── install-docker.sh         # Instalación automática (Linux/Mac)
├── install-docker.bat        # Instalación automática (Windows)
├── DOCKER_README.md          # Documentación Docker completa
├── QUICK_START.md            # Guía de inicio rápido
└── logs/                     # Directorio de logs
```

## 🗄️ Base de Datos

### Tablas Requeridas

- **Origen:** `nv_hdd_history` - Datos de uso de discos duros
- **Resultados:** `nv_hdd_an_resultados` - Resultados de análisis (se crea automáticamente)

### Configuración

```env
DB_HOST=10.147.17.185
DB_PORT=1433
DB_NAME=cmpc_20240925_093000
DB_USER=otms
DB_PASSWORD=Password1
```

## 📊 Métricas Generadas

La aplicación genera las siguientes métricas:

1. **Máximo** - Equipo con mayor uso de disco
2. **Mínimo** - Equipo con menor uso de disco
3. **Inestabilidad** - Equipo con mayor variabilidad en uso
4. **Tasa de Cambio** - Equipo con mayor velocidad de cambio

Cada métrica se asocia a un equipo específico y una unidad de disco.

## 🔧 Configuración

### Parámetros de Análisis

Editar `hdd_config_params.yaml`:

```yaml
dias_analisis: 7                    # Días hacia atrás para análisis
umbral_maximo: 100.0               # Valor máximo aceptable
umbral_minimo: 0.0                 # Valor mínimo aceptable
tamano_lote: 1000                  # Registros por lote
max_hilos: 4                       # Hilos de procesamiento
```

## 📋 Comandos Disponibles

### Con Docker

| Comando | Descripción |
|---------|-------------|
| `./scripts/docker-run.sh once` | Ejecutar análisis una vez |
| `./scripts/docker-run.sh scheduled` | Ejecutar programado |
| `./scripts/docker-run.sh logs` | Ver logs en tiempo real |
| `./scripts/docker-run.sh stop` | Detener contenedor |
| `./scripts/docker-run.sh build` | Reconstruir imagen |

### Sin Docker

| Comando | Descripción |
|---------|-------------|
| `python main.py --run-once` | Ejecutar análisis una vez |
| `python main.py --run-scheduled` | Ejecutar programado |

## 📊 Monitoreo

### Logs

- **Aplicación:** `logs/hdd_data_analysis_YYYYMMDD.log`
- **Docker:** `docker logs hdd-data-analysis-run`

### Verificar Resultados

```sql
SELECT TOP 10 * FROM nv_hdd_an_resultados 
ORDER BY fecha_ejecucion_del_codigo DESC
```

## 🔄 Automatización

### Cron Job (Linux/Mac)

```bash
# Ejecutar diariamente a las 2:00 AM
0 2 * * * cd /path/to/hdd_data_analysis && ./scripts/docker-run.sh once
```

### Task Scheduler (Windows)

1. Abrir "Programador de tareas"
2. Crear tarea básica
3. Programar para ejecutar diariamente a las 2:00 AM
4. Acción: Iniciar programa
5. Programa: `scripts\docker-run.bat`
6. Argumentos: `once`

## 🐳 Docker

### Ventajas

- ✅ Entorno aislado y reproducible
- ✅ Fácil despliegue en cualquier sistema
- ✅ Gestión automática de dependencias
- ✅ Scripts de automatización incluidos

### Comandos Docker

```bash
# Construir imagen
docker build -t hdd-data-analysis:latest .

# Ejecutar una vez
docker run --rm hdd-data-analysis:latest python main.py --run-once

# Ejecutar programado
docker run -d --restart unless-stopped hdd-data-analysis:latest python main.py --run-scheduled

# Con docker-compose
docker-compose up -d hdd-data-analysis
```

## 📖 Documentación

- **[QUICK_START.md](QUICK_START.md)** - Guía de inicio rápido
- **[DOCKER_README.md](DOCKER_README.md)** - Documentación Docker completa
- **[DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)** - Guía de despliegue general

## 🔍 Troubleshooting

### Problemas Comunes

1. **Error de conexión a BD:**
   - Verificar que la BD esté accesible
   - Revisar credenciales en `.env`

2. **Error de permisos:**
   ```bash
   mkdir -p logs
   chmod 755 logs  # Solo Linux/Mac
   ```

3. **Contenedor no inicia:**
   ```bash
   docker logs hdd-data-analysis-run
   ```

## 📞 Soporte

Para reportar problemas o solicitar ayuda:

1. Revisar la documentación
2. Verificar logs de la aplicación
3. Contactar al equipo de desarrollo

## 📝 Changelog

### v1.0.0
- Implementación inicial del análisis HDD
- Dockerización completa
- Scripts de automatización
- Documentación completa
- Métricas corregidas (una métrica por equipo) 