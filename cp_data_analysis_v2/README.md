# CP Data Analysis v2 - Sistema de Análisis de Datos con Ranking

## Descripción General

CP Data Analysis v2 es un sistema avanzado de análisis de datos de equipos que incluye funcionalidad de ranking basada en tres métricas clave: **llenado**, **inestabilidad** y **tasa de cambio**. Este sistema procesa datos históricos de equipos desde una base de datos SQL Server y genera rankings completos para optimizar el rendimiento operacional.

## Características Principales

### 🔍 Análisis de Datos
- **Análisis Básico**: Máximo, mínimo, inestabilidad y tasa de cambio por equipo
- **Ranking de Equipos**: Posicionamiento basado en métricas de rendimiento
- **Análisis por Área**: Evaluación específica por zonas operacionales
- **Tendencias Temporales**: Análisis de los últimos 7 días

### 📊 Métricas de Ranking

#### 1. **Llenado (Fullness)**
- **Descripción**: Nivel de ocupación promedio del equipo
- **Cálculo**: Promedio de valores de llenado en los últimos 7 días
- **Interpretación**: Mayor valor = mejor rendimiento

#### 2. **Inestabilidad (Instability)**
- **Descripción**: Variabilidad en el rendimiento del equipo
- **Cálculo**: Desviación estándar × 1000
- **Interpretación**: Menor valor = mayor estabilidad

#### 3. **Tasa de Cambio (Rate of Change)**
- **Descripción**: Velocidad de cambio en el rendimiento
- **Cálculo**: Desviación estándar de la tasa de cambio × 10,000
- **Interpretación**: Menor valor = cambios más predecibles

## Estructura del Proyecto

```
cp_data_analysis_v2/
├── main.py                 # Punto de entrada principal
├── requirements.txt        # Dependencias de Python
├── config_params.yaml      # Configuración del sistema
├── src/                    # Código fuente principal
│   ├── cp_ranking_functions.py    # Funciones de ranking
│   ├── cp_upload_data_deploy.py   # Carga de datos
│   ├── cp_db_manager.py           # Gestión de base de datos
│   ├── cp_config_manager.py       # Gestión de configuración
│   ├── cp_log_manager.py          # Sistema de logging
│   └── config.py                  # Configuración de conexión
├── tests/                  # Pruebas unitarias
│   └── test_ranking.py     # Pruebas de funciones de ranking
├── scripts/                # Scripts de utilidad
│   ├── ejecutar_ranking_real.py      # Ejecución con datos reales
│   ├── mostrar_resultados_ranking.py # Visualización de resultados
│   └── mostrar_valores_metricos.py   # Análisis de valores métricos
└── docs/                   # Documentación
    └── README_RANKING.md   # Documentación detallada de ranking
```

## Instalación y Configuración

### Prerrequisitos
- Python 3.8 o superior
- SQL Server con acceso a la base de datos
- Conexión de red a la base de datos

### Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   cd cp_data_analysis_v2
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar la base de datos**
   - Editar `config.py` con los parámetros de conexión
   - Verificar acceso a la tabla `nv_cp_history`

4. **Configurar parámetros**
   - Editar `config_params.yaml` según necesidades

## Uso del Sistema

### Ejecución Principal

```bash
python main.py
```

### Scripts de Utilidad

#### 1. Ejecutar Ranking con Datos Reales
```bash
python scripts/ejecutar_ranking_real.py
```

#### 2. Mostrar Resultados de Ranking
```bash
python scripts/mostrar_resultados_ranking.py
```

#### 3. Analizar Valores Métricos
```bash
python scripts/mostrar_valores_metricos.py
```

#### 4. Ejecutar Pruebas
```bash
python tests/test_ranking.py
```

## Base de Datos

### Tablas de Entrada
- **nv_cp_history**: Datos históricos de equipos

### Tablas de Salida
- **an_resultados**: Resultados básicos de análisis
- **an_resultados_promedios**: Promedios por área
- **nv_cp_analisis_datos_v2**: Rankings completos de equipos

### Estructura de la Tabla de Rankings

```sql
CREATE TABLE nv_cp_analisis_datos_v2 (
    id INT IDENTITY(1,1) PRIMARY KEY,
    fecha_analisis DATETIME,
    equipo VARCHAR(50),
    area VARCHAR(50),
    tipo_ranking VARCHAR(20),
    posicion INT,
    valor_metrico DECIMAL(10,4),
    total_equipos INT,
    fecha_creacion DATETIME DEFAULT GETDATE()
)
```

## Configuración

### Archivo config.py
```python
# Configuración de base de datos
DB_CONFIG = {
    'server': 'tu_servidor',
    'database': 'tu_base_datos',
    'username': 'tu_usuario',
    'password': 'tu_password',
    'driver': 'ODBC Driver 17 for SQL Server'
}
```

### Archivo config_params.yaml
```yaml
# Parámetros de análisis
analisis:
  dias_historicos: 7
  areas_analisis: ["AREA1", "AREA2", "AREA3"]
  
# Configuración de logging
logging:
  nivel: "INFO"
  archivo: "logs/cp_data_analysis_v2.log"
```

## Funciones Principales

### Generación de Rankings

```python
from src.cp_ranking_functions import (
    generar_ranking_llenado,
    generar_ranking_inestabilidad,
    generar_ranking_tasa_cambio,
    generar_ranking_combinado
)

# Generar rankings individuales
ranking_llenado = generar_ranking_llenado(datos)
ranking_inestabilidad = generar_ranking_inestabilidad(datos)
ranking_tasa_cambio = generar_ranking_tasa_cambio(datos)

# Generar ranking combinado
ranking_combinado = generar_ranking_combinado(datos)
```

### Gestión de Base de Datos

```python
from src.cp_db_manager import DatabaseManager

db_manager = DatabaseManager()

# Guardar rankings
db_manager.guardar_rankings(
    ranking_llenado=ranking_llenado,
    ranking_inestabilidad=ranking_inestabilidad,
    ranking_tasa_cambio=ranking_tasa_cambio,
    ranking_combinado=ranking_combinado
)
```

## Logs y Monitoreo

El sistema genera logs detallados en:
- `logs/cp_data_analysis_v2.log`: Log principal del sistema
- `logs/db_fallback_YYYYMMDD.log`: Logs de fallback de base de datos

### Niveles de Log
- **INFO**: Información general del proceso
- **WARNING**: Advertencias no críticas
- **ERROR**: Errores que requieren atención
- **DEBUG**: Información detallada para desarrollo

## Troubleshooting

### Problemas Comunes

1. **Error de conexión a base de datos**
   - Verificar configuración en `config.py`
   - Comprobar conectividad de red
   - Validar credenciales

2. **Datos insuficientes**
   - Verificar que existan datos en `nv_cp_history`
   - Comprobar rango de fechas

3. **Errores de memoria**
   - Reducir el rango de fechas de análisis
   - Optimizar consultas de base de datos

### Comandos de Diagnóstico

```bash
# Verificar conexión a base de datos
python -c "from src.cp_db_manager import DatabaseManager; db = DatabaseManager(); print('Conexión OK')"

# Verificar datos disponibles
python scripts/mostrar_valores_metricos.py

# Ejecutar pruebas
python tests/test_ranking.py
```

## Contribución

Para contribuir al proyecto:

1. Crear una rama para tu feature
2. Implementar cambios
3. Ejecutar pruebas
4. Crear pull request

## Licencia

Este proyecto es propiedad de InfoDesign Colombia.

## Contacto

Para soporte técnico o consultas:
- Email: soporte@infodesign.com.co
- Teléfono: +57 1 XXX XXXX

---

**Versión**: 2.0  
**Última actualización**: Julio 2025  
**Autor**: Sistema de Análisis CP 