# Dashboard de Equipos - CP & HDD

Sistema de análisis y puntuación de equipos basado en métricas de procesamiento (CP) y almacenamiento (HDD).

## 📊 Aplicaciones

### 1. Dashboard Global (`dashboard_equipos.py`)
- Vista general de estadísticas
- Gráficos de distribución
- Comparación CP vs HDD
- Top y peores equipos

### 2. Detalle de Equipos (`detalle_equipos.py`)
- Análisis detallado por equipo
- Explicaciones humanas y sustanciales
- Recomendaciones específicas
- Gráficos de radar de métricas

## 🚀 Instalación Local

```bash
pip install -r requirements.txt
streamlit run dashboard_equipos.py
```

## 📁 Estructura del Proyecto

```
├── dashboard_equipos.py      # Dashboard global
├── detalle_equipos.py        # Análisis detallado
├── ranking_cp.csv           # Datos de ranking CP
├── ranking_hdd.csv          # Datos de ranking HDD
├── requirements.txt         # Dependencias
└── README.md               # Este archivo
```

## 🎯 Características

- **Puntuación basada en percentiles** (0-100)
- **Categorización automática**: Excelente, Muy Bueno, Bueno, Regular, Necesita Mejora
- **Explicaciones humanas** con contexto técnico
- **Recomendaciones específicas** con acciones concretas
- **Visualizaciones interactivas** con Plotly
- **Interfaz responsive** y moderna

## 📈 Métricas Analizadas

### CP (Procesamiento)
- Ocupación de CPU
- Estabilidad del rendimiento
- Tasa de cambio

### HDD (Almacenamiento)
- Uso de disco
- Estabilidad del almacenamiento
- Tasa de cambio

## 🔧 Tecnologías

- **Streamlit**: Interfaz web
- **Pandas**: Procesamiento de datos
- **Plotly**: Visualizaciones interactivas
- **NumPy**: Cálculos matemáticos

## 📞 Soporte

Desarrollado por InfoDesign Colombia 