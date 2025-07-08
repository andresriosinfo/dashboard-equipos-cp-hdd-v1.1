# Documentación Técnica - CP Data Analysis v2

## Arquitectura del Sistema

### Componentes Principales

#### 1. **CPDataAnalysisV2** (main.py)
- **Responsabilidad**: Orquestador principal del sistema
- **Funciones**:
  - Coordinar el flujo de análisis completo
  - Gestionar la carga de datos históricos
  - Ejecutar análisis básico y rankings
  - Manejar errores y logging

#### 2. **ConfigManager** (cp_config_manager.py)
- **Responsabilidad**: Gestión centralizada de configuración
- **Funciones**:
  - Cargar parámetros desde archivos YAML
  - Proporcionar acceso a configuración global
  - Validar parámetros de configuración

#### 3. **LogManager** (cp_log_manager.py)
- **Responsabilidad**: Sistema de logging unificado
- **Funciones**:
  - Configurar loggers por módulo
  - Rotación automática de archivos de log
  - Diferentes niveles de logging

#### 4. **DatabaseManager** (cp_db_manager.py)
- **Responsabilidad**: Gestión de conexiones y operaciones de BD
- **Funciones**:
  - Conexión a SQL Server
  - Creación de tablas de ranking
  - Guardado de resultados
  - Manejo de transacciones

#### 5. **DataUploader** (cp_upload_data_deploy.py)
- **Responsabilidad**: Carga de datos desde fuentes externas
- **Funciones**:
  - Consulta a tabla `nv_cp_history`
  - Filtrado por fechas y áreas
  - Preprocesamiento de datos

#### 6. **RankingFunctions** (cp_ranking_functions.py)
- **Responsabilidad**: Cálculo de rankings y métricas
- **Funciones**:
  - Generación de rankings individuales
  - Cálculo de ranking combinado
  - Normalización de valores

## Flujo de Datos

### 1. Carga de Datos
```
nv_cp_history → DataUploader → DataFrame procesado
```

### 2. Análisis Básico
```
DataFrame → Funciones de análisis → Resultados básicos
```

### 3. Generación de Rankings
```
DataFrame → RankingFunctions → Rankings individuales + combinado
```

### 4. Persistencia
```
Rankings → DatabaseManager → nv_cp_analisis_datos_v2
```

## Algoritmos de Ranking

### 1. Ranking de Llenado

```python
def generar_ranking_llenado(datos):
    # 1. Agrupar por equipo y área
    # 2. Calcular promedio de valores
    # 3. Ordenar de mayor a menor
    # 4. Asignar posiciones
```

**Fórmula**: `valor_metrico = promedio(valores_equipo)`

### 2. Ranking de Inestabilidad

```python
def generar_ranking_inestabilidad(datos):
    # 1. Agrupar por equipo y área
    # 2. Calcular desviación estándar
    # 3. Multiplicar por factor (1000)
    # 4. Ordenar de menor a mayor
    # 5. Asignar posiciones
```

**Fórmula**: `valor_metrico = std(valores_equipo) × 1000`

### 3. Ranking de Tasa de Cambio

```python
def generar_ranking_tasa_cambio(datos):
    # 1. Calcular tasa de cambio entre registros consecutivos
    # 2. Agrupar por equipo y área
    # 3. Calcular desviación estándar de tasas
    # 4. Multiplicar por factor (10000)
    # 5. Ordenar de menor a mayor
    # 6. Asignar posiciones
```

**Fórmula**: `valor_metrico = std(tasas_cambio_equipo) × 10000`

### 4. Ranking Combinado

```python
def generar_ranking_combinado(datos):
    # 1. Generar rankings individuales
    # 2. Normalizar valores (0-1)
    # 3. Aplicar pesos configurados
    # 4. Calcular puntuación combinada
    # 5. Ordenar y asignar posiciones
```

**Fórmula**: 
```
puntuacion = (ranking_llenado_norm × 0.4) + 
             (ranking_inestabilidad_norm × 0.3) + 
             (ranking_tasa_cambio_norm × 0.3)
```

## Estructura de Base de Datos

### Tabla de Rankings: `nv_cp_analisis_datos_v2`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INT | Identificador único (auto-increment) |
| `fecha_analisis` | DATETIME | Fecha y hora del análisis |
| `equipo` | VARCHAR(50) | Código del equipo |
| `area` | VARCHAR(50) | Área operacional |
| `tipo_ranking` | VARCHAR(20) | Tipo de ranking (llenado/inestabilidad/tasa_cambio/combinado) |
| `posicion` | INT | Posición en el ranking (1 = mejor) |
| `valor_metrico` | DECIMAL(10,4) | Valor numérico de la métrica |
| `total_equipos` | INT | Total de equipos en el ranking |
| `fecha_creacion` | DATETIME | Fecha de creación del registro |

### Índices Recomendados

```sql
-- Índice principal para consultas de ranking
CREATE INDEX IX_nv_cp_analisis_datos_v2_ranking 
ON nv_cp_analisis_datos_v2 (fecha_analisis, tipo_ranking, area, posicion);

-- Índice para consultas por equipo
CREATE INDEX IX_nv_cp_analisis_datos_v2_equipo 
ON nv_cp_analisis_datos_v2 (equipo, fecha_analisis, tipo_ranking);
```

## Configuración del Sistema

### Parámetros Clave

#### Análisis
- `dias_historicos`: Período de análisis (default: 7)
- `areas_analisis`: Lista de áreas específicas (vacío = todas)
- `min_registros_equipo`: Mínimo de registros para considerar equipo válido

#### Métricas
- `factor_inestabilidad`: Multiplicador para valores de inestabilidad
- `factor_tasa_cambio`: Multiplicador para valores de tasa de cambio
- `umbral_llenado_minimo`: Valor mínimo para considerar llenado válido

#### Ranking Combinado
- `peso_llenado`: Peso para métrica de llenado (0.4)
- `peso_inestabilidad`: Peso para métrica de inestabilidad (0.3)
- `peso_tasa_cambio`: Peso para métrica de tasa de cambio (0.3)

## Manejo de Errores

### Tipos de Errores

1. **Errores de Conexión**
   - Timeout de conexión
   - Credenciales inválidas
   - Servidor no disponible

2. **Errores de Datos**
   - Datos insuficientes
   - Valores nulos o inválidos
   - Formato de datos incorrecto

3. **Errores de Procesamiento**
   - Memoria insuficiente
   - Cálculos matemáticos inválidos
   - Timeout de procesamiento

### Estrategias de Recuperación

```python
# Reintentos automáticos para conexiones
max_reintentos = 3
tiempo_espera = 5  # segundos

# Fallback para datos insuficientes
if len(datos) < min_registros:
    logger.warning(f"Datos insuficientes para {equipo}")
    return None

# Validación de valores antes de guardar
if not pd.isna(valor_metrico) and valor_metrico >= 0:
    # Guardar valor
    pass
```

## Optimización de Rendimiento

### 1. Procesamiento de Datos

```python
# Usar chunks para grandes volúmenes
chunk_size = 5000
for chunk in pd.read_sql(query, connection, chunksize=chunk_size):
    procesar_chunk(chunk)

# Vectorización de operaciones
valores_promedio = datos.groupby(['equipo', 'area'])['valor'].mean()
```

### 2. Consultas de Base de Datos

```sql
-- Usar índices apropiados
-- Limitar resultados con WHERE
-- Usar TOP para rankings
SELECT TOP 10 * FROM nv_cp_analisis_datos_v2 
WHERE fecha_analisis = @fecha AND tipo_ranking = @tipo
ORDER BY posicion
```

### 3. Gestión de Memoria

```python
# Liberar memoria después de procesar
del datos_grandes
gc.collect()

# Usar tipos de datos apropiados
datos['fecha'] = pd.to_datetime(datos['fecha'])
datos['valor'] = pd.to_numeric(datos['valor'], errors='coerce')
```

## Monitoreo y Logging

### Niveles de Log

- **DEBUG**: Información detallada para desarrollo
- **INFO**: Información general del proceso
- **WARNING**: Advertencias no críticas
- **ERROR**: Errores que requieren atención
- **CRITICAL**: Errores críticos del sistema

### Métricas de Rendimiento

```python
# Tiempo de ejecución
tiempo_inicio = time.time()
# ... procesamiento ...
tiempo_total = time.time() - tiempo_inicio
logger.info(f"Procesamiento completado en {tiempo_total:.2f} segundos")

# Uso de memoria
memoria_uso = psutil.Process().memory_info().rss / 1024 / 1024  # MB
logger.info(f"Uso de memoria: {memoria_uso:.2f} MB")
```

## Seguridad

### Protección de Datos

1. **Encriptación de Logs**
   - Logs sensibles encriptados
   - Rotación automática de archivos

2. **Validación de Entrada**
   - Sanitización de parámetros
   - Validación de tipos de datos

3. **Control de Acceso**
   - Credenciales de BD seguras
   - Permisos mínimos necesarios

### Auditoría

```python
# Log de auditoría
logger.info(f"Usuario: {usuario}, Acción: {accion}, Fecha: {datetime.now()}")
```

## Pruebas

### Tipos de Pruebas

1. **Pruebas Unitarias**
   - Funciones individuales
   - Casos límite
   - Manejo de errores

2. **Pruebas de Integración**
   - Flujo completo del sistema
   - Interacción entre módulos

3. **Pruebas de Rendimiento**
   - Tiempo de respuesta
   - Uso de memoria
   - Escalabilidad

### Ejecución de Pruebas

```bash
# Pruebas unitarias
python -m pytest tests/

# Prueba rápida del sistema
python test_quick.py

# Pruebas de rendimiento
python -m pytest tests/test_performance.py
```

## Mantenimiento

### Tareas Periódicas

1. **Limpieza de Logs**
   - Rotación automática
   - Compresión de archivos antiguos

2. **Optimización de BD**
   - Reconstrucción de índices
   - Limpieza de datos antiguos

3. **Actualización de Configuración**
   - Revisión de parámetros
   - Ajuste de pesos de ranking

### Backup y Recuperación

```sql
-- Backup de tabla de rankings
BACKUP TABLE nv_cp_analisis_datos_v2 TO 'backup_rankings.bak'

-- Restauración
RESTORE TABLE nv_cp_analisis_datos_v2 FROM 'backup_rankings.bak'
```

---

**Versión**: 2.0  
**Última actualización**: Julio 2025  
**Autor**: Sistema de Análisis CP 