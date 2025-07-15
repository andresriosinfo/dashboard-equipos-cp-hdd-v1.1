import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import ast

# Configuración de la página
st.set_page_config(
    page_title="Análisis Detallado de Equipos - V7",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .recommendation-card {
        background: #e8f4fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ff7f0e;
        margin: 0.5rem 0;
    }
    .area-button {
        background: #f0f0f0;
        border: 2px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .area-button:hover {
        background: #e0e0e0;
        border-color: #1f77b4;
    }
    .performance-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stExpander > div > div {
        background: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Cargar datos de rankings"""
    try:
        ranking_cp = pd.read_csv('ranking_cp_v2.csv')
        ranking_hdd = pd.read_csv('ranking_hdd_v2.csv')
        return ranking_cp, ranking_hdd
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None, None

def parse_list_column(column):
    """Parsear columnas que contienen listas como strings"""
    if column.dtype == 'object':
        try:
            return column.apply(lambda x: ast.literal_eval(x) if pd.notna(x) and x != '[]' else [])
        except:
            return column
    return column

def create_radar_chart(metrics, title, color='blue'):
    """Crear gráfico de radar para métricas de rendimiento"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=metrics,
        theta=['Eficiencia', 'Estabilidad', 'Predictibilidad'],
        fill='toself',
        fillcolor=f'rgba({color}, 0.3)',
        line_color=f'rgb({color})',
        name=title
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title=title,
        height=300
    )
    
    return fig

def get_performance_explanation(efficiency, stability, predictability):
    """Generar explicación detallada del perfil de rendimiento"""
    explanations = []
    
    # Eficiencia
    if efficiency >= 80:
        efficiency_text = f"**Eficiencia Alta ({efficiency:.1f}%)**: El equipo mantiene un rendimiento óptimo en sus operaciones principales."
    elif efficiency >= 60:
        efficiency_text = f"**Eficiencia Moderada ({efficiency:.1f}%)**: El equipo tiene un rendimiento aceptable pero con margen de mejora."
    else:
        efficiency_text = f"**Eficiencia Baja ({efficiency:.1f}%)**: El equipo presenta deficiencias significativas en su rendimiento operativo."
    
    # Estabilidad
    if stability >= 80:
        stability_text = f"**Estabilidad Alta ({stability:.1f}%)**: El equipo mantiene un rendimiento consistente y predecible."
    elif stability >= 60:
        stability_text = f"**Estabilidad Moderada ({stability:.1f}%)**: El equipo muestra variabilidad en su rendimiento pero dentro de rangos aceptables."
    else:
        stability_text = f"**Estabilidad Baja ({stability:.1f}%)**: El equipo presenta alta variabilidad e inconsistencia en su rendimiento."
    
    # Predictibilidad
    if predictability >= 80:
        predictability_text = f"**Predictibilidad Alta ({predictability:.1f}%)**: Es fácil prever el comportamiento futuro del equipo."
    elif predictability >= 60:
        predictability_text = f"**Predictibilidad Moderada ({predictability:.1f}%)**: El comportamiento del equipo es parcialmente predecible."
    else:
        predictability_text = f"**Predictibilidad Baja ({predictability:.1f}%)**: El comportamiento del equipo es impredecible y requiere monitoreo constante."
    
    return efficiency_text, stability_text, predictability_text

def main():
    st.markdown('<div class="main-header"><h1>📊 Análisis Detallado de Equipos - V7</h1></div>', unsafe_allow_html=True)
    
    # Cargar datos
    ranking_cp, ranking_hdd = load_data()
    
    if ranking_cp is None:
        st.error("No se pudieron cargar los datos. Verifique que los archivos de ranking existan.")
        return
    
    # Parsear columnas de listas
    ranking_cp['explicaciones_por_area'] = parse_list_column(ranking_cp['explicaciones_por_area'])
    ranking_cp['recomendaciones_por_area'] = parse_list_column(ranking_cp['recomendaciones_por_area'])
    ranking_hdd['explicaciones_por_area'] = parse_list_column(ranking_hdd['explicaciones_por_area'])
    ranking_hdd['recomendaciones_por_area'] = parse_list_column(ranking_hdd['recomendaciones_por_area'])
    
    # Selector de equipo
    equipos_disponibles = sorted(ranking_cp['equipo'].unique())
    equipo_seleccionado = st.selectbox(
        "Seleccione un equipo para analizar:",
        equipos_disponibles,
        index=0
    )
    
    # Obtener datos del equipo seleccionado
    equipo_cp = ranking_cp[ranking_cp['equipo'] == equipo_seleccionado].iloc[0]
    equipo_hdd = ranking_hdd[ranking_hdd['equipo'] == equipo_seleccionado]
    
    # Verificar si el equipo tiene datos HDD
    tiene_hdd = not equipo_hdd.empty
    if tiene_hdd:
        equipo_hdd = equipo_hdd.iloc[0]
    
    st.markdown("---")
    
    # SECCIÓN 1: INFORMACIÓN GENERAL Y RECOMENDACIONES
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 Información General del Equipo")
        
        # Información básica
        info_col1, info_col2, info_col3 = st.columns(3)
        
        with info_col1:
            st.metric("Equipo", equipo_seleccionado)
        
        with info_col2:
            st.metric("Posición CP", f"{equipo_cp['posicion']} de {len(ranking_cp)}")
        
        with info_col3:
            if tiene_hdd:
                st.metric("Posición HDD", f"{equipo_hdd['posicion']} de {len(ranking_hdd)}")
            else:
                st.metric("Posición HDD", "Sin datos")
        
        # Evaluación general
        st.markdown("#### Evaluación General")
        evaluacion_cp = equipo_cp['evaluacion_general']
        evaluacion_hdd = equipo_hdd['evaluacion_general'] if tiene_hdd else "Sin datos HDD"
        
        eval_col1, eval_col2 = st.columns(2)
        with eval_col1:
            st.markdown(f'<div class="metric-card"><strong>CP:</strong> {evaluacion_cp}</div>', unsafe_allow_html=True)
        with eval_col2:
            if tiene_hdd:
                st.markdown(f'<div class="metric-card"><strong>HDD:</strong> {evaluacion_hdd}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="metric-card"><strong>HDD:</strong> Sin datos disponibles</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🎯 Recomendaciones del Sistema")
        
        # Recomendaciones CP
        st.markdown("#### Recomendaciones CP")
        recomendaciones_cp = equipo_cp['recomendaciones_generales']
        if isinstance(recomendaciones_cp, list):
            for rec in recomendaciones_cp:
                st.markdown(f'<div class="recommendation-card">• {rec}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="recommendation-card">{recomendaciones_cp}</div>', unsafe_allow_html=True)
        
        # Recomendaciones HDD
        if tiene_hdd:
            st.markdown("#### Recomendaciones HDD")
            recomendaciones_hdd = equipo_hdd['recomendaciones_generales']
            if isinstance(recomendaciones_hdd, list):
                for rec in recomendaciones_hdd:
                    st.markdown(f'<div class="recommendation-card">• {rec}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="recommendation-card">{recomendaciones_hdd}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # SECCIÓN 2: PERFILES DE RENDIMIENTO
    st.markdown("### 📈 Perfiles de Rendimiento")
    
    perf_col1, perf_col2 = st.columns(2)
    
    with perf_col1:
        st.markdown("#### Perfil CP")
        # Métricas CP
        eficiencia_cp = equipo_cp['eficiencia']
        estabilidad_cp = equipo_cp['estabilidad']
        predictibilidad_cp = equipo_cp['predictibilidad']
        
        # Gráfico radar CP
        fig_cp = create_radar_chart([eficiencia_cp, estabilidad_cp, predictibilidad_cp], "Perfil CP", "31, 119, 180")
        st.plotly_chart(fig_cp, use_container_width=True)
        
        # Explicación CP
        eff_cp, stab_cp, pred_cp = get_performance_explanation(eficiencia_cp, estabilidad_cp, predictibilidad_cp)
        st.markdown(f"**Análisis CP:**")
        st.markdown(f"• {eff_cp}")
        st.markdown(f"• {stab_cp}")
        st.markdown(f"• {pred_cp}")
    
    with perf_col2:
        if tiene_hdd:
            st.markdown("#### Perfil HDD")
            # Métricas HDD
            eficiencia_hdd = equipo_hdd['eficiencia']
            estabilidad_hdd = equipo_hdd['estabilidad']
            predictibilidad_hdd = equipo_hdd['predictibilidad']
            
            # Gráfico radar HDD
            fig_hdd = create_radar_chart([eficiencia_hdd, estabilidad_hdd, predictibilidad_hdd], "Perfil HDD", "255, 127, 14")
            st.plotly_chart(fig_hdd, use_container_width=True)
            
            # Explicación HDD
            eff_hdd, stab_hdd, pred_hdd = get_performance_explanation(eficiencia_hdd, estabilidad_hdd, predictibilidad_hdd)
            st.markdown(f"**Análisis HDD:**")
            st.markdown(f"• {eff_hdd}")
            st.markdown(f"• {stab_hdd}")
            st.markdown(f"• {pred_hdd}")
        else:
            st.markdown("#### Perfil HDD")
            st.info("No hay datos HDD disponibles para este equipo")
    
    st.markdown("---")
    
    # SECCIÓN 3: ANÁLISIS DETALLADO POR ÁREAS CP
    st.markdown("### 🔍 Análisis Detallado por Áreas CP")
    st.markdown("Haga clic en cada área para ver el análisis detallado:")
    
    # Obtener áreas disponibles
    areas_cp = ['CP_LLENADO', 'CP_EMPAQUE', 'CP_PALETIZADO', 'CP_DESPACHO']
    
    # Crear columnas dinámicas para los botones
    num_areas = len(areas_cp)
    cols = st.columns(num_areas)
    
    for i, area in enumerate(areas_cp):
        with cols[i]:
            # Verificar si el equipo tiene datos para esta área
            tiene_area = False
            if area in equipo_cp['areas_con_datos']:
                tiene_area = True
            
            # Crear botón expandible
            with st.expander(f"📦 {area.replace('CP_', '')}", expanded=False):
                if tiene_area:
                    # Obtener explicaciones y recomendaciones para esta área
                    explicaciones = equipo_cp['explicaciones_por_area']
                    recomendaciones = equipo_cp['recomendaciones_por_area']
                    
                    # Encontrar el índice de esta área
                    area_index = None
                    for j, area_data in enumerate(explicaciones):
                        if area_data.get('area') == area:
                            area_index = j
                            break
                    
                    if area_index is not None:
                        area_explicacion = explicaciones[area_index]
                        area_recomendacion = recomendaciones[area_index] if area_index < len(recomendaciones) else None
                        
                        # Mostrar métricas de la área
                        st.markdown("#### Métricas de la Área")
                        
                        # Obtener datos específicos de la área
                        area_data = pd.read_csv('cp_data_analysis_v2/data/processed/cp_processed_data.csv') # Assuming this file contains all data
                        area_data = area_data[(area_data['equipo'] == equipo_seleccionado) & 
                                          (area_data['area'] == area)]
                        
                        if not area_data.empty:
                            # Mostrar métricas principales
                            metric_cols = st.columns(3)
                            
                            with metric_cols[0]:
                                if 'CP_LLENADO' in area_data.columns:
                                    valor_llenado = area_data['CP_LLENADO'].iloc[0]
                                    st.metric("Llenado", f"{valor_llenado:.2f}")
                            
                            with metric_cols[1]:
                                if 'CP_EMPAQUE' in area_data.columns:
                                    valor_empaque = area_data['CP_EMPAQUE'].iloc[0]
                                    st.metric("Empaque", f"{valor_empaque:.2f}")
                            
                            with metric_cols[2]:
                                if 'CP_PALETIZADO' in area_data.columns:
                                    valor_paletizado = area_data['CP_PALETIZADO'].iloc[0]
                                    st.metric("Paletizado", f"{valor_paletizado:.2f}")
                        
                        # Mostrar explicación
                        st.markdown("#### Análisis de la Área")
                        if 'explicacion' in area_explicacion:
                            st.markdown(f"**Explicación:** {area_explicacion['explicacion']}")
                        
                        if 'puntuacion' in area_explicacion:
                            puntuacion = area_explicacion['puntuacion']
                            st.metric("Puntuación", f"{puntuacion:.1f}/100")
                        
                        # Mostrar recomendación
                        if area_recomendacion and 'recomendacion' in area_recomendacion:
                            st.markdown("#### Recomendación Específica")
                            st.markdown(f"**Acción sugerida:** {area_recomendacion['recomendacion']}")
                            
                            if 'prioridad' in area_recomendacion:
                                prioridad = area_recomendacion['prioridad']
                                st.markdown(f"**Prioridad:** {prioridad}")
                        
                        # Mostrar comparación con otros equipos
                        st.markdown("#### Comparación con Otros Equipos")
                        
                        # Obtener datos de todos los equipos para esta área
                        todos_equipos_area = pd.read_csv('cp_data_analysis_v2/data/processed/cp_processed_data.csv') # Assuming this file contains all data
                        todos_equipos_area = todos_equipos_area[todos_equipos_area['area'] == area]
                        
                        if not todos_equipos_area.empty:
                            # Calcular estadísticas
                            if 'CP_LLENADO' in todos_equipos_area.columns:
                                media_llenado = todos_equipos_area['CP_LLENADO'].mean()
                                st.markdown(f"**Promedio del área:** {media_llenado:.2f}")
                            
                            if 'CP_EMPAQUE' in todos_equipos_area.columns:
                                media_empaque = todos_equipos_area['CP_EMPAQUE'].mean()
                                st.markdown(f"**Promedio del área:** {media_empaque:.2f}")
                            
                            if 'CP_PALETIZADO' in todos_equipos_area.columns:
                                media_paletizado = todos_equipos_area['CP_PALETIZADO'].mean()
                                st.markdown(f"**Promedio del área:** {media_paletizado:.2f}")
                    else:
                        st.warning("No se encontró información detallada para esta área")
                else:
                    st.info(f"El equipo {equipo_seleccionado} no tiene datos para el área {area}")
    
    # SECCIÓN 4: ANÁLISIS HDD (si está disponible)
    if tiene_hdd:
        st.markdown("---")
        st.markdown("### 💾 Análisis HDD")
        
        with st.expander("📊 Detalles del Almacenamiento", expanded=False):
            # Métricas HDD
            hdd_cols = st.columns(3)
            
            with hdd_cols[0]:
                st.metric("Eficiencia HDD", f"{equipo_hdd['eficiencia']:.1f}%")
            
            with hdd_cols[1]:
                st.metric("Estabilidad HDD", f"{equipo_hdd['estabilidad']:.1f}%")
            
            with hdd_cols[2]:
                st.metric("Predictibilidad HDD", f"{equipo_hdd['predictibilidad']:.1f}%")
            
            # Explicaciones HDD
            if 'explicaciones_por_area' in equipo_hdd and isinstance(equipo_hdd['explicaciones_por_area'], list):
                st.markdown("#### Análisis Detallado HDD")
                for explicacion in equipo_hdd['explicaciones_por_area']:
                    if isinstance(explicacion, dict):
                        area = explicacion.get('area', 'HDD')
                        st.markdown(f"**{area}:** {explicacion.get('explicacion', 'Sin explicación disponible')}")
            
            # Recomendaciones HDD
            if 'recomendaciones_por_area' in equipo_hdd and isinstance(equipo_hdd['recomendaciones_por_area'], list):
                st.markdown("#### Recomendaciones HDD")
                for recomendacion in equipo_hdd['recomendaciones_por_area']:
                    if isinstance(recomendacion, dict):
                        st.markdown(f"• **{recomendacion.get('area', 'HDD')}:** {recomendacion.get('recomendacion', 'Sin recomendación disponible')}")

if __name__ == "__main__":
    main() 