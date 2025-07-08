# HDD Data Analysis v2 - Documentación Técnica

## Índice

1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Componentes Principales](#componentes-principales)
3. [Sistema de Ranking](#sistema-de-ranking)
4. [Gestión de Base de Datos](#gestión-de-base-de-datos)
5. [Configuración y Parámetros](#configuración-y-parámetros)
6. [Sistema de Logging](#sistema-de-logging)
7. [Procesamiento de Datos](#procesamiento-de-datos)
8. [Pruebas y Validación](#pruebas-y-validación)
9. [Despliegue](#despliegue)
10. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)

## Arquitectura del Sistema

### Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    HDD Data Analysis v2                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Scripts   │  │    Tests    │  │     Docs    │         │
│  │             │  │             │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                        src/                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Ranking   │  │     DB      │  │   Config    │         │
│  │ Functions   │  │  Manager    │  │  Manager    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │     Log     │  │   Upload    │  │   Write     │         │
│  │  Manager    │  │    Data     │  │    Data     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ┌─────────────┐  ┌─────────────┐                         │
│  │  Functions  │  │    Batch    │                         │
│  │   Deploy    │  │ Processor   │                         │
│  └─────────────┘  └─────────────┘                         │
├─────────────────────────────────────────────────────────────┤
│                    Base de Datos                            │
│  ┌─────────────┐  ┌─────────────┐                         │
│  │ nv_hdd_     │  │ nv_hdd_     │                         │
│  │ history     │  │ analisis_   │                         │
│  │             │  │ datos_v2    │                         │
│  └─────────────┘  └─────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### Principios de Diseño

1. **Modularidad**: Cada componente tiene responsabilidades específicas
2. **Escalabilidad**: Arquitectura preparada para crecimiento
3. **Mantenibilidad**: Código limpio y bien documentado
4. **Testabilidad**: Componentes independientes y testeables
5. **Configurabilidad**: Parámetros externos para flexibilidad

## Componentes Principales

### 1. Sistema de Ranking (`hdd_ranking_functions.py`)

#### Funciones Principales

```python
def calculate_usage_ranking(df: pd.DataFrame) -> pd.DataFrame
def calculate_instability_ranking(df: pd.DataFrame) -> pd.DataFrame
def calculate_rate_of_change_ranking(df: pd.DataFrame) -> pd.DataFrame
def calculate_combined_ranking(df: pd.DataFrame) -> pd.DataFrame
```

#### Algoritmos Implementados

**Ranking por Uso:**
- Análisis de porcentaje de utilización del disco
- Evaluación de patrones de acceso (lectura/escritura)
- Cálculo de frecuencia de operaciones I/O

**Ranking por Inestabilidad:**
- Cálculo de desviación estándar de métricas críticas
- Análisis de variabilidad en latencias
- Evaluación de fluctuaciones en throughput

**Ranking por Tasa de Cambio:**
- Análisis de tendencias temporales
- Cálculo de velocidad de degradación
- Predicción de fallos basada en tendencias

### 2. Gestor de Base de Datos (`hdd_db_manager.py`)

#### Clase Principal: `HDDDatabaseManager`

```python
class HDDDatabaseManager:
    def __init__(self, config: dict = None)
    def create_rankings_table(self) -> bool
    def save_rankings(self, rankings: pd.DataFrame) -> bool
    def get_rankings(self, limit: int = None) -> pd.DataFrame
    def get_hdd_data(self, hdd_id: str = None, days: int = 30) -> pd.DataFrame
```

#### Estructura de Tablas

**nv_hdd_history:**
```sql
CREATE TABLE nv_hdd_history (
    id INT IDENTITY(1,1) PRIMARY KEY,
    hdd_id VARCHAR(50),
    fecha DATETIME,
    disk_usage_percent DECIMAL(5,2),
    read_latency DECIMAL(10,2),
    write_latency DECIMAL(10,2),
    temperature DECIMAL(5,2),
    read_operations INT,
    write_operations INT,
    throughput DECIMAL(10,2),
    -- ... otras métricas
);
```

**nv_hdd_analisis_datos_v2:**
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

### 3. Gestor de Configuración (`hdd_config_manager.py`)

#### Clase Principal: `HDDConfigManager`

```python
class HDDConfigManager:
    def __init__(self, config_file: str = "hdd_config_params.yaml")
    def load_config(self) -> dict
    def get_database_config(self) -> dict
    def get_ranking_config(self) -> dict
    def get_logging_config(self) -> dict
    def validate_config(self) -> bool
```

### 4. Gestor de Logging (`hdd_log_manager.py`)

#### Clase Principal: `HDDLogManager`

```python
class HDDLogManager:
    def __init__(self, config: dict = None)
    def get_logger(self, name: str) -> logging.Logger
    def setup_file_handler(self, filename: str) -> logging.FileHandler
    def setup_rotation_handler(self, filename: str, max_size: str, backup_count: int)
```

## Sistema de Ranking

### Métricas Evaluadas

#### 1. Métricas de Uso
- `disk_usage_percent`: Porcentaje de utilización del disco
- `read_operations`: Número de operaciones de lectura
- `write_operations`: Número de operaciones de escritura
- `io_operations`: Total de operaciones I/O

#### 2. Métricas de Rendimiento
- `read_latency`: Latencia de lectura (ms)
- `write_latency`: Latencia de escritura (ms)
- `throughput`: Throughput del disco (MB/s)
- `queue_depth`: Profundidad de cola

#### 3. Métricas de Salud
- `temperature`: Temperatura del disco (°C)
- `power_on_hours`: Horas de funcionamiento
- `reallocated_sectors`: Sectores reasignados
- `pending_sectors`: Sectores pendientes
- `uncorrectable_sectors`: Sectores no corregibles

### Algoritmos de Cálculo

#### Ranking por Uso
```python
def calculate_usage_score(usage_data):
    # Normalización de métricas
    usage_score = normalize_usage_percent(usage_data['disk_usage_percent'])
    io_score = normalize_io_operations(usage_data['io_operations'])
    
    # Ponderación
    final_score = (usage_score * 0.6) + (io_score * 0.4)
    return final_score
```

#### Ranking por Inestabilidad
```python
def calculate_instability_score(metrics_data):
    # Cálculo de desviación estándar
    latency_std = np.std(metrics_data['read_latency'])
    throughput_std = np.std(metrics_data['throughput'])
    
    # Normalización y combinación
    instability_score = (latency_std * 0.5) + (throughput_std * 0.5)
    return instability_score
```

#### Ranking por Tasa de Cambio
```python
def calculate_rate_of_change_score(temporal_data):
    # Análisis de tendencias
    usage_trend = calculate_trend(temporal_data['disk_usage_percent'])
    health_trend = calculate_trend(temporal_data['health_metrics'])
    
    # Combinación de tendencias
    rate_score = (usage_trend * 0.4) + (health_trend * 0.6)
    return rate_score
```

## Gestión de Base de Datos

### Conexión y Pooling

```python
def create_connection_pool(self):
    """Crear pool de conexiones para optimizar rendimiento"""
    connection_string = (
        f"DRIVER={{{self.config['driver']}}};"
        f"SERVER={self.config['server']};"
        f"DATABASE={self.config['database']};"
        f"UID={self.config['username']};"
        f"PWD={self.config['password']};"
        f"Timeout={self.config['timeout']};"
    )
    
    return pyodbc.connect(connection_string)
```

### Optimización de Consultas

```sql
-- Índices recomendados para optimización
CREATE INDEX IX_nv_hdd_history_hdd_id_fecha 
ON nv_hdd_history (hdd_id, fecha);

CREATE INDEX IX_nv_hdd_analisis_datos_v2_hdd_id 
ON nv_hdd_analisis_datos_v2 (hdd_id);

CREATE INDEX IX_nv_hdd_analisis_datos_v2_fecha_analisis 
ON nv_hdd_analisis_datos_v2 (fecha_analisis);
```

## Configuración y Parámetros

### Archivo de Configuración Principal (`config_v2.yaml`)

#### Secciones Principales

1. **Database**: Configuración de conexión a base de datos
2. **Ranking**: Parámetros del sistema de ranking
3. **Logging**: Configuración del sistema de logs
4. **Processing**: Parámetros de procesamiento
5. **Alerts**: Configuración de alertas
6. **Reports**: Configuración de reportes

#### Ejemplo de Configuración

```yaml
ranking:
  weights:
    usage: 0.35
    instability: 0.35
    rate_of_change: 0.30
  
  thresholds:
    usage_warning: 85.0
    instability_warning: 0.20
    rate_of_change_warning: 0.15
  
  temporal:
    window_days: 30
    min_data_points: 10
    trend_periods: 7
```

## Sistema de Logging

### Estructura de Logs

```
logs/
├── hdd_data_analysis_v2.log      # Log principal
├── ranking_hdd_v2.log            # Log específico de ranking
├── errors_hdd_v2.log             # Log de errores
└── test_quick_v2.log             # Log de pruebas
```

### Niveles de Log

- **DEBUG**: Información detallada para debugging
- **INFO**: Información general del proceso
- **WARNING**: Advertencias no críticas
- **ERROR**: Errores que requieren atención
- **CRITICAL**: Errores críticos del sistema

### Rotación de Logs

```python
def setup_rotation_handler(self, filename, max_size="20MB", backup_count=10):
    """Configurar rotación automática de logs"""
    handler = RotatingFileHandler(
        filename,
        maxBytes=self._parse_size(max_size),
        backupCount=backup_count
    )
    return handler
```

## Procesamiento de Datos

### Flujo de Procesamiento

1. **Carga de Datos**: Lectura desde `nv_hdd_history`
2. **Preprocesamiento**: Limpieza y validación de datos
3. **Cálculo de Rankings**: Aplicación de algoritmos de ranking
4. **Postprocesamiento**: Normalización y combinación de resultados
5. **Persistencia**: Guardado en `nv_hdd_analisis_datos_v2`

### Optimización de Rendimiento

```python
def process_data_in_batches(self, data, batch_size=1000):
    """Procesar datos en lotes para optimizar memoria"""
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        yield self.process_batch(batch)
```

## Pruebas y Validación

### Tipos de Pruebas

1. **Pruebas Unitarias**: Validación de funciones individuales
2. **Pruebas de Integración**: Validación de interacción entre componentes
3. **Pruebas de Rendimiento**: Validación de tiempos de respuesta
4. **Pruebas de Datos**: Validación con datos reales

### Ejecución de Pruebas

```bash
# Ejecutar todas las pruebas
python -m pytest tests/

# Ejecutar pruebas específicas
python tests/test_ranking_hdd.py

# Ejecutar prueba rápida
python test_quick_v2.py
```

## Despliegue

### Opciones de Despliegue

1. **Local**: Instalación directa en el servidor
2. **Docker**: Containerización para portabilidad
3. **Servicio Windows**: Instalación como servicio del sistema

### Scripts de Instalación

- `install_v2.bat`: Instalación en Windows
- `install_v2.sh`: Instalación en Linux
- `install-docker.bat`: Instalación con Docker (Windows)
- `install-docker.sh`: Instalación con Docker (Linux)

### Variables de Entorno

```bash
# Configuración de base de datos
DB_SERVER=localhost
DB_NAME=OTMS
DB_USER=sa
DB_PASSWORD=your_password

# Configuración de logging
LOG_LEVEL=INFO
LOG_FILE=logs/hdd_data_analysis_v2.log
```

## Monitoreo y Mantenimiento

### Métricas de Monitoreo

1. **Rendimiento**: Tiempo de procesamiento, uso de memoria
2. **Disponibilidad**: Tiempo de actividad, errores
3. **Calidad de Datos**: Precisión de rankings, completitud
4. **Recursos**: Uso de CPU, memoria, disco

### Tareas de Mantenimiento

1. **Limpieza de Logs**: Rotación y archivo de logs antiguos
2. **Optimización de Base de Datos**: Reindexación, limpieza
3. **Backup**: Respaldo regular de datos y configuración
4. **Actualización**: Actualización de dependencias y código

### Alertas y Notificaciones

```python
def send_alert(self, message, level="INFO"):
    """Enviar alerta por email o sistema de notificación"""
    if self.config['alerts']['enabled']:
        # Implementar lógica de envío de alertas
        pass
```

---

**Versión**: 2.0  
**Última actualización**: Julio 2025  
**Autor**: Equipo de Desarrollo  
**Estado**: Documentación Técnica Completa 