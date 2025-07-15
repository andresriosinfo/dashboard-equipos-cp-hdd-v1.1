import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import ast

# Configuración de la página
st.set_page_config(
    page_title="Análisis Detallado de Equipos - V9",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
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
    .recommendation-good {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 0.5rem;
        border-radius: 4px;
        margin: 0.25rem 0;
    }
    .recommendation-warning {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 0.5rem;
        border-radius: 4px;
        margin: 0.25rem 0;
    }
    .recommendation-critical {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 0.5rem;
        border-radius: 4px;
        margin: 0.25rem 0;
    }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-excellent { background-color: #28a745; }
    .status-good { background-color: #17a2b8; }
    .status-average { background-color: #ffc107; }
    .status-poor { background-color: #dc3545; }
    .status-critical { background-color: #6c757d; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Cargar datos de ranking"""
    try:
        # Cargar rankings
        ranking_cp = pd.read_csv('ranking_cp_v2.csv')
        ranking_hdd = pd.read_csv('ranking_hdd_v2.csv')
        
        # Los archivos de datos procesados no existen, usar solo rankings
        return ranking_cp, ranking_hdd, None, None
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None, None, None, None

def get_status_color(score):
    """Obtener color de estado basado en el score"""
    if score >= 80:
        return "excellent"
    elif score >= 60:
        return "good"
    elif score >= 40:
        return "average"
    elif score >= 20:
        return "poor"
    else:
        return "critical"

def get_recommendation_color(recommendation):
    """Obtener color de recomendación basado en el texto"""
    if any(word in recommendation.lower() for word in ['excelente', 'bueno', 'mejorar', 'optimizar']):
        return "good"
    elif any(word in recommendation.lower() for word in ['atención', 'revisar', 'monitorear']):
        return "warning"
    else:
        return "critical"

def create_radar_chart(team_data, team_name, data_type):
    """Crear gráfico de radar para CP o HDD"""
    if data_type == "CP":
        # Componentes del score CP
        categories = ['Eficiencia', 'Estabilidad', 'Predictibilidad']
        values = [
            team_data.get('score_eficiencia', 0),
            team_data.get('score_estabilidad', 0),
            team_data.get('score_predictibilidad', 0)
        ]
    else:  # HDD
        # Componentes del score HDD
        categories = ['Eficiencia', 'Estabilidad', 'Predictibilidad']
        values = [
            team_data.get('score_eficiencia', 0),
            team_data.get('score_estabilidad', 0),
            team_data.get('score_predictibilidad', 0)
        ]
    
    # Crear gráfico de radar
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=f'Perfil {data_type}',
        line_color='#1f77b4',
        fillcolor='rgba(31, 119, 180, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title=f"Perfil de Rendimiento {data_type}",
        height=300
    )
    
    return fig

def get_performance_interpretation(team_data, data_type):
    """Obtener interpretación del perfil de rendimiento"""
    if data_type == "CP":
        eficiencia = team_data.get('score_eficiencia', 0)
        estabilidad = team_data.get('score_estabilidad', 0)
        predictibilidad = team_data.get('score_predictibilidad', 0)
    else:
        eficiencia = team_data.get('score_eficiencia', 0)
        estabilidad = team_data.get('score_estabilidad', 0)
        predictibilidad = team_data.get('score_predictibilidad', 0)
    
    # Interpretación cualitativa
    def get_quality(score):
        if score >= 80: return "Excelente"
        elif score >= 60: return "Buena"
        elif score >= 40: return "Regular"
        elif score >= 20: return "Baja"
        else: return "Crítica"
    
    return {
        'eficiencia': {'valor': eficiencia, 'calidad': get_quality(eficiencia)},
        'estabilidad': {'valor': estabilidad, 'calidad': get_quality(estabilidad)},
        'predictibilidad': {'valor': predictibilidad, 'calidad': get_quality(predictibilidad)}
    }

def analyze_cp_areas(team_name, cp_data):
    """Análisis detallado por áreas CP"""
    team_cp = cp_data[cp_data['equipo'] == team_name]
    
    if team_cp.empty:
        return None
    
    areas_analysis = {}
    
    # Áreas CP disponibles
    cp_areas = ['CP_LLENADO', 'CP_EMPAQUE', 'CP_PALETIZADO', 'CP_DESPACHO']
    
    for area in cp_areas:
        area_data = team_cp[team_cp['area'] == area]
        
        if not area_data.empty:
            # Calcular métricas por área
            metricas = {}
            for col in ['eficiencia', 'estabilidad', 'predictibilidad']:
                if col in area_data.columns:
                    metricas[col] = area_data[col].mean()
            
            # Determinar estado del área
            if 'eficiencia' in metricas:
                if metricas['eficiencia'] >= 80:
                    estado = "Excelente"
                    color = "excellent"
                elif metricas['eficiencia'] >= 60:
                    estado = "Buena"
                    color = "good"
                elif metricas['eficiencia'] >= 40:
                    estado = "Regular"
                    color = "average"
                elif metricas['eficiencia'] >= 20:
                    estado = "Baja"
                    color = "poor"
                else:
                    estado = "Crítica"
                    color = "critical"
            else:
                estado = "Sin datos"
                color = "critical"
            
            areas_analysis[area] = {
                'metricas': metricas,
                'estado': estado,
                'color': color,
                'datos_disponibles': len(area_data)
            }
    
    return areas_analysis

def main():
    st.markdown('<div class="main-header"><h1>📊 Análisis Detallado de Equipos - V9</h1></div>', unsafe_allow_html=True)
    
    # Cargar datos
    ranking_cp, ranking_hdd, cp_data, hdd_data = load_data()
    
    if ranking_cp is None or ranking_hdd is None:
        st.error("No se pudieron cargar los datos. Verifica que los archivos de ranking existan.")
        return
    
    # Selector de equipo
    equipos_cp = ranking_cp['equipo'].unique()
    equipos_hdd = ranking_hdd['equipo'].unique()
    equipos_todos = sorted(list(set(equipos_cp) | set(equipos_hdd)))
    
    equipo_seleccionado = st.selectbox(
        "Selecciona un equipo para analizar:",
        equipos_todos,
        index=0
    )
    
    if not equipo_seleccionado:
        st.warning("Por favor selecciona un equipo.")
        return
    
    # Obtener datos del equipo
    equipo_cp = ranking_cp[ranking_cp['equipo'] == equipo_seleccionado]
    equipo_hdd = ranking_hdd[ranking_hdd['equipo'] == equipo_seleccionado]
    
    # Primera fila: Información general, score, posición y recomendaciones
    col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
    
    with col1:
        st.subheader("📋 Información General")
        st.write(f"**Equipo:** {equipo_seleccionado}")
        
        # Información CP
        if not equipo_cp.empty:
            st.write(f"**Score CP:** {equipo_cp.iloc[0]['score_final']:.1f}")
            st.write(f"**Posición CP:** {equipo_cp.iloc[0]['posicion']} de {len(ranking_cp)}")
        else:
            st.write("**Score CP:** Sin datos")
        
        # Información HDD
        if not equipo_hdd.empty:
            st.write(f"**Score HDD:** {equipo_hdd.iloc[0]['score_final']:.1f}")
            st.write(f"**Posición HDD:** {equipo_hdd.iloc[0]['posicion']} de {len(ranking_hdd)}")
        else:
            st.write("**Score HDD:** Sin datos")
    
    with col2:
        st.subheader("🏆 Score General")
        if not equipo_cp.empty and not equipo_hdd.empty:
            score_cp = equipo_cp.iloc[0]['score_final']
            score_hdd = equipo_hdd.iloc[0]['score_final']
            score_general = (score_cp + score_hdd) / 2
            st.metric("Score General", f"{score_general:.1f}")
        elif not equipo_cp.empty:
            st.metric("Score General", f"{equipo_cp.iloc[0]['score_final']:.1f}")
        elif not equipo_hdd.empty:
            st.metric("Score General", f"{equipo_hdd.iloc[0]['score_final']:.1f}")
        else:
            st.metric("Score General", "Sin datos")
    
    with col3:
        st.subheader("📊 Posición Global")
        if not equipo_cp.empty and not equipo_hdd.empty:
            pos_cp = equipo_cp.iloc[0]['posicion']
            pos_hdd = equipo_hdd.iloc[0]['posicion']
            pos_general = (pos_cp + pos_hdd) / 2
            st.metric("Posición", f"{pos_general:.0f}")
        elif not equipo_cp.empty:
            st.metric("Posición", f"{equipo_cp.iloc[0]['posicion']}")
        elif not equipo_hdd.empty:
            st.metric("Posición", f"{equipo_hdd.iloc[0]['posicion']}")
        else:
            st.metric("Posición", "Sin datos")
    
    with col4:
        st.subheader("💡 Recomendaciones Principales")
        recomendaciones = []
        
        if not equipo_cp.empty:
            rec_cp = equipo_cp.iloc[0].get('recomendaciones', '')
            if rec_cp:
                recomendaciones.append(f"**CP:** {rec_cp}")
        
        if not equipo_hdd.empty:
            rec_hdd = equipo_hdd.iloc[0].get('recomendaciones', '')
            if rec_hdd:
                recomendaciones.append(f"**HDD:** {rec_hdd}")
        
        if recomendaciones:
            for rec in recomendaciones:
                color_class = get_recommendation_color(rec)
                st.markdown(f'<div class="recommendation-{color_class}">{rec}</div>', unsafe_allow_html=True)
        else:
            st.write("Sin recomendaciones disponibles")
    
    # Segunda fila: Perfiles de rendimiento CP y HDD
    st.subheader("📈 Perfiles de Rendimiento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not equipo_cp.empty:
            st.write("**Perfil CP**")
            cp_col1, cp_col2 = st.columns([1, 1])
            
            with cp_col1:
                # Gráfico de radar CP
                fig_cp = create_radar_chart(equipo_cp.iloc[0], equipo_seleccionado, "CP")
                st.plotly_chart(fig_cp, use_container_width=True)
            
            with cp_col2:
                # Interpretación CP
                interpretation_cp = get_performance_interpretation(equipo_cp.iloc[0], "CP")
                st.write("**Interpretación:**")
                for metric, data in interpretation_cp.items():
                    st.write(f"• **{metric.title()}:** {data['valor']:.1f} ({data['calidad']})")
        else:
            st.write("**Perfil CP** - Sin datos disponibles")
    
    with col2:
        if not equipo_hdd.empty:
            st.write("**Perfil HDD**")
            hdd_col1, hdd_col2 = st.columns([1, 1])
            
            with hdd_col1:
                # Gráfico de radar HDD
                fig_hdd = create_radar_chart(equipo_hdd.iloc[0], equipo_seleccionado, "HDD")
                st.plotly_chart(fig_hdd, use_container_width=True)
            
            with hdd_col2:
                # Interpretación HDD
                interpretation_hdd = get_performance_interpretation(equipo_hdd.iloc[0], "HDD")
                st.write("**Interpretación:**")
                for metric, data in interpretation_hdd.items():
                    st.write(f"• **{metric.title()}:** {data['valor']:.1f} ({data['calidad']})")
        else:
            st.write("**Perfil HDD** - Sin datos disponibles")
    
    # Tercera fila: Análisis detallado de áreas CP
    if not equipo_cp.empty:
        st.subheader("🔍 Análisis Detallado por Áreas CP")
        
        # Mostrar información del score CP por componentes
        st.write("**Componentes del Score CP:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            eficiencia = equipo_cp.iloc[0].get('score_eficiencia', 0)
            st.metric("Eficiencia", f"{eficiencia:.1f}")
            if eficiencia >= 80:
                st.markdown('<div class="recommendation-good">Excelente</div>', unsafe_allow_html=True)
            elif eficiencia >= 60:
                st.markdown('<div class="recommendation-good">Buena</div>', unsafe_allow_html=True)
            elif eficiencia >= 40:
                st.markdown('<div class="recommendation-warning">Regular</div>', unsafe_allow_html=True)
            elif eficiencia >= 20:
                st.markdown('<div class="recommendation-critical">Baja</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="recommendation-critical">Crítica</div>', unsafe_allow_html=True)
        
        with col2:
            estabilidad = equipo_cp.iloc[0].get('score_estabilidad', 0)
            st.metric("Estabilidad", f"{estabilidad:.1f}")
            if estabilidad >= 80:
                st.markdown('<div class="recommendation-good">Excelente</div>', unsafe_allow_html=True)
            elif estabilidad >= 60:
                st.markdown('<div class="recommendation-good">Buena</div>', unsafe_allow_html=True)
            elif estabilidad >= 40:
                st.markdown('<div class="recommendation-warning">Regular</div>', unsafe_allow_html=True)
            elif estabilidad >= 20:
                st.markdown('<div class="recommendation-critical">Baja</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="recommendation-critical">Crítica</div>', unsafe_allow_html=True)
        
        with col3:
            predictibilidad = equipo_cp.iloc[0].get('score_predictibilidad', 0)
            st.metric("Predictibilidad", f"{predictibilidad:.1f}")
            if predictibilidad >= 80:
                st.markdown('<div class="recommendation-good">Excelente</div>', unsafe_allow_html=True)
            elif predictibilidad >= 60:
                st.markdown('<div class="recommendation-good">Buena</div>', unsafe_allow_html=True)
            elif predictibilidad >= 40:
                st.markdown('<div class="recommendation-warning">Regular</div>', unsafe_allow_html=True)
            elif predictibilidad >= 20:
                st.markdown('<div class="recommendation-critical">Baja</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="recommendation-critical">Crítica</div>', unsafe_allow_html=True)
        
        # Mostrar explicaciones detalladas si están disponibles
        if 'explicaciones_detalladas' in equipo_cp.columns:
            st.write("**Explicaciones Detalladas:**")
            explicaciones = equipo_cp.iloc[0]['explicaciones_detalladas']
            if pd.notna(explicaciones):
                try:
                    # Intentar parsear si es una lista
                    if isinstance(explicaciones, str):
                        explicaciones_list = ast.literal_eval(explicaciones)
                        for exp in explicaciones_list:
                            st.write(f"• {exp}")
                except:
                    st.write(explicaciones)
    
    # Cuarta fila: Explicaciones del sistema de puntuación
    with st.expander("ℹ️ Explicación del Sistema de Puntuación"):
        st.write("""
        **Sistema de Puntuación:**
        
        **CP (Procesamiento):**
        - **Eficiencia:** Mide qué tan bien el equipo utiliza sus recursos
        - **Estabilidad:** Consistencia en el rendimiento a lo largo del tiempo
        - **Predictibilidad:** Capacidad de mantener un rendimiento constante
        
        **HDD (Almacenamiento):**
        - **Eficiencia:** Optimización del uso del espacio de almacenamiento
        - **Estabilidad:** Consistencia en las operaciones de almacenamiento
        - **Predictibilidad:** Capacidad de mantener patrones de almacenamiento estables
        
        **Escala de Puntuación:**
        - **80-100:** Excelente
        - **60-79:** Buena
        - **40-59:** Regular
        - **20-39:** Baja
        - **0-19:** Crítica
        """)

if __name__ == "__main__":
    main() 