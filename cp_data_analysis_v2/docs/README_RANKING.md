# Sistema de Ranking de Equipos - CP Data Analysis

## Descripción

Este módulo extiende el sistema CP Data Analysis para generar rankings completos de equipos basados en tres métricas clave:

1. **Llenado** - Equipos con mayor nivel de ocupación/valores
2. **Inestabilidad** - Equipos con mayor variabilidad en sus valores
3. **Tasa de Cambio** - Equipos con mayor velocidad de cambio

## Características Principales

### ✅ Ranking Completo
- **Posiciones para todos los equipos** (no solo el primero)
- **Ranking individual por cada métrica**
- **Datos históricos de los últimos 7 días**
- **Valores métricos calculados**

### ✅ Nueva Tabla de Base de Datos
- **Tabla:** `nv_cp_analisis_datos_v2`
- **Estructura optimizada** para rankings
- **Compatibilidad** con el sistema existente

### ✅ Integración Automática
- **Ejecución automática** con el análisis diario
- **Procesamiento paralelo** para mejor rendimiento
- **Logging completo** de todas las operaciones

## Estructura de la Nueva Tabla

### Tabla: `nv_cp_analisis_datos_v2`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | String(36) | Identificador único (UUID) |
| `area` | String(100) | Área del equipo |
| `equipo` | String(100) | Nombre del equipo |
| `fecha_ejecucion_del_codigo` | DateTime | Fecha y hora de ejecución |
| `metrica` | String(50) | Tipo de métrica ('llenado', 'inestabilidad', 'tasa_cambio') |
| `posicion` | Integer | Posición en el ranking (1 = mejor) |
| `valor_metrico` | Integer | Valor calculado de la métrica |
| `valor_1` a `valor_7` | Integer | Últimos 7 valores del equipo |

## Métricas Calculadas

### 1. Llenado (llenado)
- **Cálculo:** Promedio de valores en los últimos 7 días
- **Ranking:** Mayor a menor (posición 1 = mayor llenado)
- **Uso:** Identificar equipos con mayor ocupación

### 2. Inestabilidad (inestabilidad)
- **Cálculo:** Desviación estándar de valores en los últimos 7 días
- **Ranking:** Mayor a menor (posición 1 = más inestable)
- **Uso:** Identificar equipos con mayor variabilidad

### 3. Tasa de Cambio (tasa_cambio)
- **Cálculo:** Desviación estándar de la tasa de cambio porcentual
- **Ranking:** Mayor a menor (posición 1 = mayor tasa de cambio)
- **Uso:** Identificar equipos con cambios más rápidos

## Archivos Modificados/Creados

### Nuevos Archivos
- `cp_ranking_functions.py` - Funciones de cálculo de rankings
- `test_ranking.py` - Script de pruebas
- `README_RANKING.md` - Esta documentación

### Archivos Modificados
- `main.py` - Integración del ranking en el flujo principal
- `cp_db_manager.py` - Definición de la nueva tabla y métodos de guardado

## Uso

### Ejecución Automática
El ranking se ejecuta automáticamente con el análisis diario:

```bash
python main.py --schedule
```

### Ejecución Manual
Para ejecutar solo el ranking:

```python
from cp_ranking_functions import generar_ranking_completo
from cp_upload_data_deploy import upload_data_sql

# Obtener datos
df_dict = upload_data_sql()

# Generar ranking
df_ranking = generar_ranking_completo(df_dict)

# Guardar en base de datos
from cp_db_manager import get_db_manager
db_manager = get_db_manager()
db_manager.save_results(df_ranking, 'ranking_completo')
```

### Pruebas
Para verificar que todo funciona correctamente:

```bash
python test_ranking.py
```

## Consultas SQL de Ejemplo

### Top 10 Equipos por Llenado
```sql
SELECT TOP 10 
    area, equipo, posicion, valor_metrico,
    valor_1, valor_2, valor_3, valor_4, valor_5, valor_6, valor_7
FROM nv_cp_analisis_datos_v2 
WHERE metrica = 'llenado' 
ORDER BY posicion;
```

### Top 10 Equipos por Inestabilidad
```sql
SELECT TOP 10 
    area, equipo, posicion, valor_metrico,
    valor_1, valor_2, valor_3, valor_4, valor_5, valor_6, valor_7
FROM nv_cp_analisis_datos_v2 
WHERE metrica = 'inestabilidad' 
ORDER BY posicion;
```

### Top 10 Equipos por Tasa de Cambio
```sql
SELECT TOP 10 
    area, equipo, posicion, valor_metrico,
    valor_1, valor_2, valor_3, valor_4, valor_5, valor_6, valor_7
FROM nv_cp_analisis_datos_v2 
WHERE metrica = 'tasa_cambio' 
ORDER BY posicion;
```

### Ranking Completo de un Equipo Específico
```sql
SELECT 
    metrica, posicion, valor_metrico,
    valor_1, valor_2, valor_3, valor_4, valor_5, valor_6, valor_7
FROM nv_cp_analisis_datos_v2 
WHERE equipo = 'NOMBRE_DEL_EQUIPO'
ORDER BY metrica;
```

## Configuración

### Parámetros de Configuración
Los siguientes parámetros se pueden configurar en la base de datos:

- `dias_analisis` - Días a analizar (default: 7)
- `umbral_maximo` - Valor máximo permitido (default: 1000)
- `umbral_minimo` - Valor mínimo permitido (default: 0)

### Comportamiento de Guardado
- **Modo append:** Agrega nuevos registros (default)
- **Modo replace:** Reemplaza todos los registros existentes

## Logs y Monitoreo

### Logs Generados
- Creación de rankings por métrica
- Número de equipos procesados
- Errores y advertencias
- Tiempo de ejecución

### Métricas de Rendimiento
- Tiempo de procesamiento por métrica
- Número de registros generados
- Uso de memoria durante el procesamiento

## Solución de Problemas

### Problemas Comunes

1. **No se generan rankings**
   - Verificar que hay datos en los últimos 7 días
   - Revisar logs para errores de procesamiento

2. **Errores de base de datos**
   - Verificar conexión a SQL Server
   - Comprobar permisos de escritura en la tabla

3. **Valores faltantes**
   - Verificar integridad de datos de entrada
   - Revisar conversiones de tipos de datos

### Comandos de Diagnóstico

```bash
# Verificar estructura de la tabla
python -c "from cp_db_manager import get_db_manager; db = get_db_manager(); print(db.check_and_create_tables())"

# Probar funciones de ranking
python test_ranking.py

# Verificar logs
tail -f logs/cp_data_analysis_$(date +%Y%m%d).log
```

## Compatibilidad

### Versiones Soportadas
- Python 3.7+
- SQL Server 2016+
- pandas 1.3+
- numpy 1.20+

### Dependencias
- Todas las dependencias del sistema principal
- No requiere dependencias adicionales

## Contribución

Para contribuir al desarrollo:

1. Crear una rama para la nueva funcionalidad
2. Implementar cambios con pruebas
3. Verificar que pasa todas las pruebas
4. Crear pull request con documentación

## Contacto

Para soporte técnico o preguntas sobre el sistema de ranking:
- Revisar logs del sistema
- Ejecutar script de pruebas
- Contactar al equipo de desarrollo 