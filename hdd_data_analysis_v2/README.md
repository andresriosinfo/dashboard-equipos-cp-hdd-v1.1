# HDD Data Analysis v2

## Descripción

HDD Data Analysis v2 es un sistema completo de análisis de datos para discos duros (HDD) que incluye funcionalidades de procesamiento de datos, análisis de métricas y sistema de ranking avanzado. Este proyecto está organizado de manera modular y profesional para facilitar su mantenimiento y escalabilidad.

## Características Principales

### 🔧 Funcionalidades Core
- **Procesamiento de datos HDD**: Análisis de métricas de rendimiento y salud de discos duros
- **Sistema de ranking avanzado**: Evaluación y clasificación de HDDs basada en múltiples criterios
- **Gestión de base de datos**: Operaciones CRUD optimizadas para datos de HDD
- **Logging avanzado**: Sistema de registro detallado para monitoreo y debugging
- **Configuración flexible**: Gestión de parámetros mediante archivos YAML

### 📊 Sistema de Ranking
- **Ranking por uso**: Evaluación basada en patrones de utilización
- **Ranking por inestabilidad**: Análisis de variabilidad en métricas
- **Ranking por tasa de cambio**: Evaluación de tendencias temporales
- **Ranking combinado**: Puntuación integral considerando todos los factores

### 🐳 Soporte Docker
- **Containerización completa**: Despliegue simplificado con Docker
- **Docker Compose**: Orquestación de servicios
- **Scripts de instalación**: Automatización para Windows y Linux

## Estructura del Proyecto

```
hdd_data_analysis_v2/
├── src/                          # Código fuente principal
│   ├── hdd_ranking_functions.py  # Funciones de ranking
│   ├── hdd_db_manager.py         # Gestión de base de datos
│   ├── hdd_config_manager.py     # Gestión de configuración
│   ├── hdd_log_manager.py        # Sistema de logging
│   ├── hdd_upload_data_deploy.py # Carga de datos
│   ├── hdd_write_data_deploy.py  # Escritura de datos
│   ├── hdd_functions_deploy.py   # Funciones de procesamiento
│   └── hdd_batch_processor.py    # Procesamiento por lotes
├── tests/                        # Pruebas unitarias
│   ├── test_ranking_hdd.py       # Pruebas del sistema de ranking
│   ├── test_hdd.py              # Pruebas generales
│   └── test_simple.py           # Pruebas básicas
├── scripts/                      # Scripts de ejecución
│   ├── ejecutar_ranking_hdd_real.py    # Ejecución con datos reales
│   ├── mostrar_resultados_ranking_hdd.py # Visualización de resultados
│   ├── run_once.bat             # Ejecución única (Windows)
│   └── run_scheduled.bat        # Ejecución programada (Windows)
├── docs/                         # Documentación
│   ├── README_RANKING_HDD.md    # Documentación del ranking
│   ├── RESUMEN_IMPLEMENTACION_RANKING.md # Resumen técnico
│   ├── README.md                # Documentación original
│   ├── QUICK_START.md           # Guía rápida
│   ├── DOCKER_README.md         # Documentación Docker
│   └── VERIFICATION_RESULTS.md  # Resultados de verificación
├── logs/                         # Archivos de log
├── main.py                       # Punto de entrada principal
├── config.py                     # Configuración base
├── hdd_config_params.yaml       # Parámetros de configuración
├── requirements.txt              # Dependencias Python
├── Dockerfile                    # Configuración Docker
├── docker-compose.yml           # Orquestación Docker
├── env.example                  # Variables de entorno
├── install-docker.bat           # Instalación Docker (Windows)
└── install-docker.sh            # Instalación Docker (Linux)
```

## Instalación

### Requisitos Previos
- Python 3.8+
- SQL Server (para base de datos)
- Docker (opcional, para despliegue containerizado)

### Instalación Local

1. **Clonar el repositorio**:
   ```bash
   git clone <repository-url>
   cd hdd_data_analysis_v2
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**:
   ```bash
   copy env.example .env
   # Editar .env con tus credenciales de base de datos
   ```

4. **Configurar parámetros**:
   - Editar `hdd_config_params.yaml` según tus necesidades
   - Ajustar `config.py` para tu entorno

### Instalación con Docker

#### Windows:
```bash
install-docker.bat
```

#### Linux:
```bash
./install-docker.sh
```

## Uso

### Ejecución Básica

1. **Ejecutar análisis completo**:
   ```bash
   python main.py
   ```

2. **Ejecutar solo el ranking**:
   ```bash
   python scripts/ejecutar_ranking_hdd_real.py
   ```

3. **Ver resultados del ranking**:
   ```bash
   python scripts/mostrar_resultados_ranking_hdd.py
   ```

### Ejecución con Docker

```bash
docker-compose up -d
```

### Scripts de Windows

- **Ejecución única**: `scripts\run_once.bat`
- **Ejecución programada**: `scripts\run_scheduled.bat`

## Sistema de Ranking

### Métricas Evaluadas

1. **Uso del Disco**:
   - Porcentaje de utilización
   - Patrones de acceso
   - Frecuencia de operaciones

2. **Inestabilidad**:
   - Variabilidad en métricas de rendimiento
   - Desviación estándar de latencias
   - Fluctuaciones en throughput

3. **Tasa de Cambio**:
   - Tendencia de degradación
   - Velocidad de cambio en métricas críticas
   - Predicción de fallos

### Algoritmos de Ranking

- **Ranking por Uso**: `calculate_usage_ranking()`
- **Ranking por Inestabilidad**: `calculate_instability_ranking()`
- **Ranking por Tasa de Cambio**: `calculate_rate_of_change_ranking()`
- **Ranking Combinado**: `calculate_combined_ranking()`

## Base de Datos

### Tablas Principales

- **nv_hdd_history**: Datos históricos de HDDs
- **nv_hdd_analisis_datos_v2**: Resultados del análisis y ranking

### Estructura de Rankings

```sql
CREATE TABLE nv_hdd_analisis_datos_v2 (
    id INT IDENTITY(1,1) PRIMARY KEY,
    hdd_id VARCHAR(50),
    fecha_analisis DATETIME,
    ranking_uso DECIMAL(10,2),
    ranking_inestabilidad DECIMAL(10,2),
    ranking_tasa_cambio DECIMAL(10,2),
    ranking_combinado DECIMAL(10,2),
    detalles_uso TEXT,
    detalles_inestabilidad TEXT,
    detalles_tasa_cambio TEXT,
    detalles_combinado TEXT,
    fecha_creacion DATETIME DEFAULT GETDATE()
);
```

## Pruebas

### Ejecutar Todas las Pruebas

```bash
python -m pytest tests/
```

### Pruebas Específicas

```bash
# Pruebas del sistema de ranking
python tests/test_ranking_hdd.py

# Pruebas generales
python tests/test_hdd.py

# Pruebas básicas
python tests/test_simple.py
```

## Configuración

### Archivo de Configuración Principal (`hdd_config_params.yaml`)

```yaml
database:
  server: "your_server"
  database: "your_database"
  username: "your_username"
  password: "your_password"

ranking:
  weights:
    usage: 0.4
    instability: 0.3
    rate_of_change: 0.3
  
  thresholds:
    usage_warning: 80
    instability_warning: 0.15
    rate_of_change_warning: 0.1

logging:
  level: "INFO"
  file: "logs/hdd_data_analysis.log"
  max_size: "10MB"
  backup_count: 5
```

## Monitoreo y Logs

### Ubicación de Logs
- **Logs principales**: `logs/hdd_data_analysis_YYYYMMDD.log`
- **Logs de ranking**: `logs/ranking_hdd_real.log`

### Niveles de Log
- **DEBUG**: Información detallada para debugging
- **INFO**: Información general del proceso
- **WARNING**: Advertencias no críticas
- **ERROR**: Errores que requieren atención
- **CRITICAL**: Errores críticos del sistema

## Troubleshooting

### Problemas Comunes

1. **Error de conexión a base de datos**:
   - Verificar credenciales en `.env`
   - Confirmar que SQL Server esté ejecutándose
   - Verificar firewall y permisos

2. **Error en ranking**:
   - Verificar que existan datos en `nv_hdd_history`
   - Revisar logs para errores específicos
   - Validar parámetros en `hdd_config_params.yaml`

3. **Problemas con Docker**:
   - Verificar que Docker esté instalado y ejecutándose
   - Revisar logs del contenedor: `docker-compose logs`

## Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Contacto

Para soporte técnico o preguntas sobre el proyecto, contactar al equipo de desarrollo.

---

**Versión**: 2.0  
**Última actualización**: Julio 2025  
**Estado**: Producción 