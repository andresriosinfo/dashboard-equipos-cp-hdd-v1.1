# Sistema de Puntuación Unificado - CP y HDD Data Analysis

## Descripción

Este sistema implementa un método de puntuación basado en percentiles que combina los datos de **CP (Control Process)** y **HDD (Hard Disk Drive)** para generar una puntuación única de **0-100** para cada equipo. El sistema es altamente explicable y proporciona recomendaciones detalladas para cada equipo.

## Características Principales

### 🎯 Sistema de Puntuación Basado en Percentiles
- **Puntuación de 0-100**: Cada equipo recibe una puntuación clara y comparable
- **Basado en percentiles**: Refleja la posición relativa del equipo vs otros
- **Muy explicable**: Cada componente tiene un peso claro y justificación

### 📊 Métricas Integradas

#### Variables CP (Control Process)
- **CP Llenado** (15%): Mayor valor = mejor rendimiento
- **CP Inestabilidad** (15%): Menor valor = mejor rendimiento (más estable)
- **CP Tasa de Cambio** (15%): Menor valor = mejor rendimiento (cambios predecibles)

#### Variables HDD (Hard Disk Drive)
- **HDD Uso** (20%): Menor valor = mejor rendimiento (menos ocupación)
- **HDD Inestabilidad** (20%): Menor valor = mejor rendimiento (uso estable)
- **HDD Tasa de Cambio** (15%): Menor valor = mejor rendimiento (cambios predecibles)

### 🏆 Categorización Automática
- **90-100**: Excelente
- **75-89**: Muy Bueno
- **50-74**: Bueno
- **25-49**: Regular
- **0-24**: Necesita Mejora

## Estructura de Archivos

```
puntajes/
├── unified_scoring_system.py    # Sistema principal de puntuación
├── show_unified_results.py      # Visualizador de resultados
├── README_UNIFIED_SCORING.md    # Esta documentación
└── logs/                        # Archivos de log
    └── unified_scoring.log
```

## Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- Acceso a las bases de datos CP y HDD
- Dependencias de ambos proyectos instaladas

### Configuración de Base de Datos
El sistema utiliza las configuraciones existentes de ambos proyectos:
- **CP**: `cp_data_analysis_v2/src/config.py`
- **HDD**: `hdd_data_analysis_v2/src/config.py`

## Uso del Sistema

### 1. Ejecutar Análisis Completo

```bash
python unified_scoring_system.py
```

**Salida esperada:**
```
🚀 INICIANDO ANÁLISIS DE PUNTUACIÓN UNIFICADA
============================================================
📊 PASO 1: Obteniendo datos CP...
📊 PASO 2: Obteniendo datos HDD...
🔧 PASO 3: Calculando métricas CP...
🔧 PASO 4: Calculando métricas HDD...
🎯 PASO 5: Calculando puntuaciones unificadas...
📝 PASO 6: Generando explicaciones...
💾 PASO 7: Guardando resultados...

📊 RESUMEN DE RESULTADOS:
   - Total equipos analizados: 150
   - Equipos con datos CP: 120
   - Equipos con datos HDD: 100
   - Puntuación promedio: 65.23
   - Mejor puntuación: 94.67
   - Peor puntuación: 12.34

🏆 TOP 10 EQUIPOS - PUNTUACIÓN UNIFICADA
============================================================
🥇 Posición  1: Equipo_A1
   📊 Puntuación: 94.67pts (Excelente)
   🏭 Área CP: AREA_1
   💾 Unidades HDD: 2
   📈 Puntuaciones: CP Llenado: 95.2pts | CP Estabilidad: 88.1pts | CP Cambios: 92.3pts | HDD Uso: 96.7pts | HDD Estabilidad: 89.4pts | HDD Cambios: 91.2pts
   💡 Recomendación: Mantener rendimiento actual
```

### 2. Visualizar Resultados

```bash
python show_unified_results.py
```

**Funcionalidades del visualizador:**
- 📊 Estadísticas generales
- 🏆 Top 10 mejores equipos
- ⚠️ Top 5 equipos con menor puntuación
- 🏭 Análisis por área
- 🔍 Búsqueda de equipo específico

## Estructura de la Base de Datos

### Tabla: `nv_unified_scoring`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | VARCHAR(36) | Identificador único (UUID) |
| `equipo` | VARCHAR(100) | Nombre del equipo |
| `area_cp` | VARCHAR(100) | Área del equipo en CP |
| `unidades_hdd` | TEXT | Lista de unidades HDD del equipo |
| `puntuacion_final` | DECIMAL(5,2) | Puntuación final (0-100) |
| `posicion_ranking` | INT | Posición en el ranking |
| `categoria_final` | VARCHAR(20) | Categoría (Excelente/Muy Bueno/etc.) |
| `cp_llenado` | DECIMAL(10,4) | Valor de llenado CP |
| `cp_llenado_score` | DECIMAL(5,2) | Puntuación de llenado CP |
| `cp_inestabilidad` | DECIMAL(10,4) | Valor de inestabilidad CP |
| `cp_inestabilidad_score` | DECIMAL(5,2) | Puntuación de inestabilidad CP |
| `cp_tasa_cambio` | DECIMAL(10,4) | Valor de tasa de cambio CP |
| `cp_tasa_cambio_score` | DECIMAL(5,2) | Puntuación de tasa de cambio CP |
| `hdd_uso` | DECIMAL(10,4) | Valor de uso HDD (%) |
| `hdd_uso_score` | DECIMAL(5,2) | Puntuación de uso HDD |
| `hdd_inestabilidad` | DECIMAL(10,4) | Valor de inestabilidad HDD |
| `hdd_inestabilidad_score` | DECIMAL(5,2) | Puntuación de inestabilidad HDD |
| `hdd_tasa_cambio` | DECIMAL(10,4) | Valor de tasa de cambio HDD |
| `hdd_tasa_cambio_score` | DECIMAL(5,2) | Puntuación de tasa de cambio HDD |
| `explicacion_detallada` | TEXT | Explicación detallada de la puntuación |
| `recomendaciones` | TEXT | Recomendaciones específicas |
| `registros_cp` | INT | Número de registros CP disponibles |
| `registros_hdd` | INT | Número de registros HDD disponibles |
| `fecha_ejecucion` | DATETIME | Fecha de ejecución del análisis |
| `fecha_creacion` | DATETIME | Fecha de creación del registro |

## Algoritmo de Puntuación

### 1. Cálculo de Percentiles
```python
def calculate_percentile_score(value, all_values, direction='higher_better'):
    percentile = (sum(1 for x in all_values if x < value) / len(all_values)) * 100
    
    if direction == 'lower_better':
        percentile = 100 - percentile
    
    return percentile
```

### 2. Puntuación Final Ponderada
```python
puntuacion_final = (
    cp_llenado_score × 0.15 +
    cp_inestabilidad_score × 0.15 +
    cp_tasa_cambio_score × 0.15 +
    hdd_uso_score × 0.20 +
    hdd_inestabilidad_score × 0.20 +
    hdd_tasa_cambio_score × 0.15
)
```

### 3. Contexto de las Variables

#### Variables CP (Control Process)
- **Llenado**: Mayor ocupación = mejor rendimiento operacional
- **Inestabilidad**: Menor variabilidad = operación más estable
- **Tasa de Cambio**: Menor velocidad de cambio = operación más predecible

#### Variables HDD (Hard Disk Drive)
- **Uso**: Menor ocupación = mejor rendimiento del disco
- **Inestabilidad**: Menor variabilidad = uso más estable
- **Tasa de Cambio**: Menor velocidad de cambio = uso más predecible

## Consultas SQL Útiles

### Top 10 Equipos por Puntuación
```sql
SELECT TOP 10 
    equipo, area_cp, puntuacion_final, posicion_ranking, categoria_final,
    explicacion_detallada, recomendaciones
FROM nv_unified_scoring 
WHERE fecha_ejecucion = (SELECT MAX(fecha_ejecucion) FROM nv_unified_scoring)
ORDER BY posicion_ranking;
```

### Equipos que Necesitan Mejora
```sql
SELECT 
    equipo, area_cp, puntuacion_final, recomendaciones
FROM nv_unified_scoring 
WHERE fecha_ejecucion = (SELECT MAX(fecha_ejecucion) FROM nv_unified_scoring)
  AND categoria_final IN ('Regular', 'Necesita Mejora')
ORDER BY puntuacion_final;
```

### Análisis por Área
```sql
SELECT 
    area_cp,
    COUNT(*) as total_equipos,
    AVG(puntuacion_final) as puntuacion_promedio,
    MIN(puntuacion_final) as puntuacion_minima,
    MAX(puntuacion_final) as puntuacion_maxima
FROM nv_unified_scoring 
WHERE fecha_ejecucion = (SELECT MAX(fecha_ejecucion) FROM nv_unified_scoring)
  AND area_cp IS NOT NULL
GROUP BY area_cp
ORDER BY puntuacion_promedio DESC;
```

### Equipos con Datos Incompletos
```sql
SELECT 
    equipo, area_cp, registros_cp, registros_hdd,
    CASE 
        WHEN registros_cp = 0 THEN 'Solo HDD'
        WHEN registros_hdd = 0 THEN 'Solo CP'
        ELSE 'Completo'
    END as tipo_datos
FROM nv_unified_scoring 
WHERE fecha_ejecucion = (SELECT MAX(fecha_ejecucion) FROM nv_unified_scoring)
ORDER BY registros_cp + registros_hdd;
```

## Interpretación de Resultados

### Puntuaciones por Categoría

#### Excelente (90-100 pts)
- Equipos con rendimiento excepcional
- Consistencia en múltiples métricas
- Recomendación: Mantener estándares actuales

#### Muy Bueno (75-89 pts)
- Equipos con buen rendimiento
- Algunas áreas de oportunidad menores
- Recomendación: Optimizaciones menores

#### Bueno (50-74 pts)
- Rendimiento aceptable
- Oportunidades de mejora identificadas
- Recomendación: Implementar mejoras específicas

#### Regular (25-49 pts)
- Rendimiento por debajo del promedio
- Múltiples áreas requieren atención
- Recomendación: Plan de mejora prioritario

#### Necesita Mejora (0-24 pts)
- Rendimiento crítico
- Intervención inmediata requerida
- Recomendación: Revisión completa del equipo

### Explicación de Recomendaciones

El sistema genera recomendaciones automáticas basadas en:
- Puntuaciones bajas en métricas específicas
- Patrones de rendimiento identificados
- Comparación con equipos similares

**Ejemplos de recomendaciones:**
- "Mejorar ocupación CP" → Equipo con bajo llenado CP
- "Reducir variabilidad CP" → Equipo con alta inestabilidad CP
- "Optimizar uso HDD" → Equipo con alto uso de disco
- "Estabilizar cambios HDD" → Equipo con alta tasa de cambio HDD

## Configuración Avanzada

### Modificar Pesos de Métricas
Editar `unified_scoring_system.py` en la sección `metric_configs`:

```python
self.metric_configs = {
    'cp_llenado': {
        'direction': 'higher_better',
        'weight': 0.20,  # Cambiar de 0.15 a 0.20
        'description': 'Nivel de ocupación promedio del equipo CP'
    },
    # ... otras métricas
}
```

### Ajustar Categorías
Modificar la función `categorize_score` en `show_unified_results.py`:

```python
def categorize_score(score):
    if score >= 85:  # Cambiar de 90 a 85
        return "Excelente"
    elif score >= 70:  # Cambiar de 75 a 70
        return "Muy Bueno"
    # ... resto de categorías
```

## Troubleshooting

### Problemas Comunes

#### 1. Error de Conexión a Base de Datos
```
Error obteniendo datos CP: [Errno 10061] No connection could be made
```
**Solución**: Verificar configuración de base de datos en `config.py`

#### 2. No se Encuentran Datos
```
No se pudieron obtener datos CP
```
**Solución**: Verificar que las tablas `nv_cp_history` y `nv_hdd_history` contengan datos

#### 3. Error de Importación
```
ModuleNotFoundError: No module named 'cp_upload_data_deploy'
```
**Solución**: Verificar que los paths de importación sean correctos

#### 4. Puntuaciones Inesperadas
```
Puntuación promedio: 50.00
```
**Solución**: Verificar que haya suficientes datos para calcular percentiles

### Logs y Monitoreo

El sistema genera logs detallados en:
- `logs/unified_scoring.log` - Log principal del sistema
- `logs/cp_data_analysis_v2.log` - Logs del sistema CP
- `logs/hdd_data_analysis_v2.log` - Logs del sistema HDD

### Comandos de Diagnóstico

```bash
# Verificar estructura de la tabla
python -c "from unified_scoring_system import UnifiedScoringSystem; s = UnifiedScoringSystem(); print('Sistema inicializado correctamente')"

# Verificar conexión a base de datos
python -c "import sys; sys.path.append('cp_data_analysis_v2/src'); from cp_db_manager import get_db_manager; db = get_db_manager(); print('Conexión exitosa' if db.is_connected else 'Error de conexión')"

# Verificar datos disponibles
python -c "from unified_scoring_system import UnifiedScoringSystem; s = UnifiedScoringSystem(); cp_data = s.get_cp_data(); print(f'DataFrames CP: {len(cp_data)}')"
```

## Contribución y Mejoras

### Posibles Mejoras Futuras
1. **Métricas adicionales**: Incluir más variables de rendimiento
2. **Análisis temporal**: Comparar puntuaciones a lo largo del tiempo
3. **Alertas automáticas**: Notificaciones para equipos críticos
4. **Dashboard web**: Interfaz gráfica para visualización
5. **Machine Learning**: Predicción de tendencias de rendimiento

### Estructura del Código
El sistema está diseñado de manera modular para facilitar:
- Adición de nuevas métricas
- Modificación de algoritmos de puntuación
- Integración con otros sistemas
- Personalización de reportes

## Contacto y Soporte

Para preguntas o soporte técnico:
- Revisar logs en `logs/unified_scoring.log`
- Verificar configuración de base de datos
- Consultar documentación de CP y HDD Data Analysis

---

**Versión**: 1.0  
**Fecha**: Julio 2025  
**Autor**: Sistema de Análisis Unificado 