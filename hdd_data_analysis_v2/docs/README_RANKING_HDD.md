# HDD Data Analysis - Sistema de Ranking de Unidades de Disco Duro

## Descripción General

El sistema de ranking HDD es una extensión del análisis de datos de discos duros que incluye funcionalidad de ranking basada en tres métricas clave: **uso**, **inestabilidad** y **tasa de cambio**. Este sistema procesa datos históricos de unidades de disco duro desde la tabla `nv_hdd_history` y genera rankings completos para optimizar el rendimiento y mantenimiento de los equipos.

## Características Principales

### 🔍 Análisis de Datos HDD
- **Análisis Básico**: Máximo, mínimo, inestabilidad y tasa de cambio por unidad
- **Ranking de Unidades**: Posicionamiento basado en métricas de rendimiento
- **Análisis por Unidad**: Evaluación específica por unidades de disco duro
- **Tendencias Temporales**: Análisis de los últimos 7 días

### 📊 Métricas de Ranking HDD

#### 1. **Uso (Usage)**
- **Descripción**: Nivel de uso promedio de la unidad de disco duro
- **Cálculo**: Promedio de valores de uso en los últimos 7 días
- **Interpretación**: Mayor valor = mayor utilización del disco
- **Rango**: 0-100%

#### 2. **Inestabilidad (Instability)**
- **Descripción**: Variabilidad en el uso de la unidad de disco duro
- **Cálculo**: Desviación estándar × 1000
- **Interpretación**: Menor valor = uso más estable y predecible
- **Factor**: Multiplicador de 1000 para mejor visualización

#### 3. **Tasa de Cambio (Rate of Change)**
- **Descripción**: Velocidad de cambio en el uso del disco duro
- **Cálculo**: Desviación estándar de la tasa de cambio × 10,000
- **Interpretación**: Menor valor = cambios más predecibles en el uso
- **Factor**: Multiplicador de 10,000 para mejor visualización

## Estructura de Base de Datos

### Tabla de Entrada
- **nv_hdd_history**: Datos históricos de unidades de disco duro

### Tabla de Salida
- **nv_hdd_analisis_datos_v2**: Rankings completos de unidades HDD

### Estructura de la Tabla de Rankings

```sql
CREATE TABLE nv_hdd_analisis_datos_v2 (
    id INT IDENTITY(1,1) PRIMARY KEY,
    fecha_analisis DATETIME,
    unidad VARCHAR(50),
    tipo_ranking VARCHAR(20),
    posicion INT,
    valor_metrico DECIMAL(10,4),
    total_equipos INT,
    fecha_creacion DATETIME DEFAULT GETDATE()
)
```

## Archivos del Sistema

### Archivos Principales
- **hdd_ranking_functions.py**: Funciones de cálculo de rankings
- **hdd_db_manager.py**: Gestión de base de datos (actualizado con funcionalidad de rankings)
- **ejecutar_ranking_hdd_real.py**: Script para ejecutar análisis con datos reales
- **test_ranking_hdd.py**: Pruebas de las funciones de ranking
- **mostrar_resultados_ranking_hdd.py**: Visualización de resultados

### Funciones de Ranking

```python
from hdd_ranking_functions import (
    generar_ranking_uso,
    generar_ranking_inestabilidad,
    generar_ranking_tasa_cambio,
    generar_ranking_combinado,
    generar_rankings_completos
)

# Generar rankings individuales
ranking_uso = generar_ranking_uso(datos)
ranking_inestabilidad = generar_ranking_inestabilidad(datos)
ranking_tasa_cambio = generar_ranking_tasa_cambio(datos)

# Generar ranking combinado
ranking_combinado = generar_ranking_combinado(datos)

# Generar todos los rankings
rankings_completos = generar_rankings_completos(datos)
```

## Uso del Sistema

### 1. Ejecutar Pruebas
```bash
python test_ranking_hdd.py
```

### 2. Ejecutar Análisis con Datos Reales
```bash
python ejecutar_ranking_hdd_real.py
```

### 3. Mostrar Resultados
```bash
python mostrar_resultados_ranking_hdd.py
```

## Algoritmos de Ranking

### Ranking de Uso
```python
def generar_ranking_uso(datos):
    # 1. Filtrar últimos 7 días
    # 2. Agrupar por unidad
    # 3. Calcular promedio de uso
    # 4. Ordenar de mayor a menor
    # 5. Asignar posiciones
```

**Fórmula**: `valor_metrico = promedio(uso_unidad)`

### Ranking de Inestabilidad
```python
def generar_ranking_inestabilidad(datos):
    # 1. Filtrar últimos 7 días
    # 2. Agrupar por unidad
    # 3. Calcular desviación estándar
    # 4. Multiplicar por 1000
    # 5. Ordenar de menor a mayor
    # 6. Asignar posiciones
```

**Fórmula**: `valor_metrico = std(uso_unidad) × 1000`

### Ranking de Tasa de Cambio
```python
def generar_ranking_tasa_cambio(datos):
    # 1. Calcular tasa de cambio entre registros consecutivos
    # 2. Agrupar por unidad
    # 3. Calcular desviación estándar de tasas
    # 4. Multiplicar por 10000
    # 5. Ordenar de menor a mayor
    # 6. Asignar posiciones
```

**Fórmula**: `valor_metrico = std(tasas_cambio_unidad) × 10000`

### Ranking Combinado
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
puntuacion = (ranking_uso_norm × 0.4) + 
             (ranking_inestabilidad_norm × 0.3) + 
             (ranking_tasa_cambio_norm × 0.3)
```

## Configuración

### Parámetros de Análisis
- **Período de análisis**: 7 días por defecto
- **Mínimo de registros**: 5 registros por unidad para considerar válida
- **Factor de inestabilidad**: 1000
- **Factor de tasa de cambio**: 10000

### Pesos del Ranking Combinado
- **Uso**: 40% (0.4)
- **Inestabilidad**: 30% (0.3)
- **Tasa de cambio**: 30% (0.3)

## Interpretación de Resultados

### Valores de Uso
- **Alto uso (>80%)**: Unidades con alta utilización, posible necesidad de expansión
- **Uso medio (40-80%)**: Unidades con utilización equilibrada
- **Bajo uso (<40%)**: Unidades con baja utilización, posible optimización

### Valores de Inestabilidad
- **Baja inestabilidad (<5000)**: Uso muy estable y predecible
- **Inestabilidad media (5000-15000)**: Uso moderadamente variable
- **Alta inestabilidad (>15000)**: Uso muy variable, requiere atención

### Valores de Tasa de Cambio
- **Baja tasa (<50000)**: Cambios lentos y predecibles
- **Tasa media (50000-200000)**: Cambios moderados
- **Alta tasa (>200000)**: Cambios rápidos e impredecibles

### Puntuación Combinada
- **Alta puntuación (>0.7)**: Unidades con excelente rendimiento general
- **Puntuación media (0.4-0.7)**: Unidades con rendimiento aceptable
- **Baja puntuación (<0.4)**: Unidades que requieren atención

## Casos de Uso

### 1. **Mantenimiento Preventivo**
- Identificar unidades con alta inestabilidad
- Detectar patrones de uso anómalos
- Planificar reemplazos basados en tendencias

### 2. **Optimización de Recursos**
- Identificar unidades con bajo uso
- Redistribuir carga de trabajo
- Optimizar asignación de almacenamiento

### 3. **Monitoreo de Rendimiento**
- Seguimiento de tendencias de uso
- Detección temprana de problemas
- Evaluación de mejoras implementadas

### 4. **Planificación de Capacidad**
- Proyección de necesidades de almacenamiento
- Identificación de unidades críticas
- Planificación de expansiones

## Logs y Monitoreo

### Archivos de Log
- **logs/ranking_hdd_real.log**: Log principal del análisis de ranking
- **logs/hdd_data_analysis.log**: Log general del sistema HDD

### Niveles de Log
- **INFO**: Información general del proceso
- **WARNING**: Advertencias no críticas
- **ERROR**: Errores que requieren atención
- **DEBUG**: Información detallada para desarrollo

## Troubleshooting

### Problemas Comunes

1. **Datos insuficientes**
   - Verificar que existan datos en `nv_hdd_history`
   - Comprobar rango de fechas
   - Validar que las unidades tengan suficientes registros

2. **Errores de cálculo**
   - Verificar que los valores de uso sean numéricos
   - Comprobar que no haya valores nulos
   - Validar formato de fechas

3. **Errores de base de datos**
   - Verificar conexión a la base de datos
   - Comprobar permisos de escritura
   - Validar estructura de la tabla

### Comandos de Diagnóstico

```bash
# Verificar datos disponibles
python -c "from hdd_upload_data_deploy import upload_data_sql; print('Datos disponibles')"

# Ejecutar pruebas
python test_ranking_hdd.py

# Verificar rankings guardados
python mostrar_resultados_ranking_hdd.py
```

## Integración con Sistema Existente

### Compatibilidad
- Compatible con el sistema HDD existente
- No interfiere con análisis básicos actuales
- Mantiene todas las funcionalidades existentes

### Extensión
- Agrega funcionalidad de ranking sin modificar código existente
- Utiliza la misma infraestructura de base de datos
- Mantiene compatibilidad con configuraciones actuales

## Próximas Mejoras

### Funcionalidades Planificadas
1. **Rankings históricos**: Seguimiento de posiciones en el tiempo
2. **Alertas automáticas**: Notificaciones para unidades problemáticas
3. **Dashboard web**: Interfaz gráfica para visualización
4. **Reportes automáticos**: Generación de reportes periódicos
5. **Análisis predictivo**: Predicción de fallos basada en tendencias

### Optimizaciones Técnicas
1. **Procesamiento paralelo**: Mejora de rendimiento para grandes volúmenes
2. **Caché de resultados**: Almacenamiento temporal de cálculos
3. **Compresión de datos**: Optimización de almacenamiento
4. **Índices optimizados**: Mejora de consultas de base de datos

---

**Versión**: 1.0  
**Última actualización**: Julio 2025  
**Autor**: Sistema de Análisis HDD  
**Compatibilidad**: HDD Data Analysis v1.0+ 