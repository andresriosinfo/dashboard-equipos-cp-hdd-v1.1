import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import ast

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Equipos CP-HDD",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📊 Dashboard de Análisis de Equipos CP-HDD")
st.markdown("---")

# Función para cargar datos
@st.cache_data
def load_data():
    try:
        # Cargar rankings
        ranking_cp = pd.read_csv('ranking_cp.csv')
        ranking_hdd = pd.read_csv('ranking_hdd.csv')
        
        # Convertir columnas de listas si existen
        if 'areas_cp' in ranking_cp.columns:
            ranking_cp['areas_cp'] = ranking_cp['areas_cp'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        if 'unidades_hdd' in ranking_hdd.columns:
            ranking_hdd['unidades_hdd'] = ranking_hdd['unidades_hdd'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        
        return ranking_cp, ranking_hdd
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None, None

# Cargar datos
ranking_cp, ranking_hdd = load_data()

if ranking_cp is None or ranking_hdd is None:
    st.error("No se pudieron cargar los datos. Verifica que los archivos ranking_cp.csv y ranking_hdd.csv estén disponibles.")
    st.stop()

# Sidebar para navegación
st.sidebar.title("🎯 Navegación")
page = st.sidebar.selectbox(
    "Selecciona la vista:",
    ["📈 Vista Global", "🔍 Análisis por Equipo", "📊 Comparativas", "📋 Explicaciones Detalladas"]
)

if page == "📈 Vista Global":
    st.header("📈 Vista Global - Estadísticas Generales")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Equipos CP",
            value=len(ranking_cp),
            delta=f"Puntaje promedio: {ranking_cp['score_final'].mean():.1f}"
        )
    
    with col2:
        st.metric(
            label="Total Equipos HDD",
            value=len(ranking_hdd),
            delta=f"Puntaje promedio: {ranking_hdd['score_final'].mean():.1f}"
        )
    
    with col3:
        mejor_cp = ranking_cp.loc[ranking_cp['score_final'].idxmax()]
        st.metric(
            label="Mejor Equipo CP",
            value=mejor_cp['equipo'],
            delta=f"Puntaje: {mejor_cp['score_final']:.1f}"
        )
    
    with col4:
        mejor_hdd = ranking_hdd.loc[ranking_hdd['score_final'].idxmax()]
        st.metric(
            label="Mejor Equipo HDD",
            value=mejor_hdd['equipo'],
            delta=f"Puntaje: {mejor_hdd['score_final']:.1f}"
        )
    
    # Gráficos de distribución
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribución de Puntajes CP")
        fig_cp = px.histogram(
            ranking_cp, 
            x='score_final',
            nbins=20,
            title="Distribución de Puntajes CP",
            labels={'score_final': 'Puntaje Final', 'count': 'Cantidad de Equipos'}
        )
        fig_cp.update_layout(showlegend=False)
        st.plotly_chart(fig_cp, use_container_width=True)
    
    with col2:
        st.subheader("📊 Distribución de Puntajes HDD")
        fig_hdd = px.histogram(
            ranking_hdd, 
            x='score_final',
            nbins=20,
            title="Distribución de Puntajes HDD",
            labels={'score_final': 'Puntaje Final', 'count': 'Cantidad de Equipos'}
        )
        fig_hdd.update_layout(showlegend=False)
        st.plotly_chart(fig_hdd, use_container_width=True)
    
    # Top 10 equipos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top 10 Equipos CP")
        top_cp = ranking_cp.nlargest(10, 'score_final')[['equipo', 'score_final']]
        fig_top_cp = px.bar(
            top_cp,
            x='score_final',
            y='equipo',
            orientation='h',
            title="Top 10 Equipos CP",
            labels={'score_final': 'Puntaje Final', 'equipo': 'Equipo'}
        )
        st.plotly_chart(fig_top_cp, use_container_width=True)
    
    with col2:
        st.subheader("🏆 Top 10 Equipos HDD")
        top_hdd = ranking_hdd.nlargest(10, 'score_final')[['equipo', 'score_final']]
        fig_top_hdd = px.bar(
            top_hdd,
            x='score_final',
            y='equipo',
            orientation='h',
            title="Top 10 Equipos HDD",
            labels={'score_final': 'Puntaje Final', 'equipo': 'Equipo'}
        )
        st.plotly_chart(fig_top_hdd, use_container_width=True)

elif page == "🔍 Análisis por Equipo":
    st.header("🔍 Análisis Detallado por Equipo")
    
    # Selector de equipo
    equipos_cp = ranking_cp['equipo'].tolist()
    equipos_hdd = ranking_hdd['equipo'].tolist()
    todos_equipos = sorted(list(set(equipos_cp + equipos_hdd)))
    
    equipo_seleccionado = st.selectbox(
        "Selecciona un equipo:",
        todos_equipos
    )
    
    # Información del equipo
    st.subheader(f"📋 Información del Equipo: {equipo_seleccionado}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if equipo_seleccionado in equipos_cp:
            datos_cp = ranking_cp[ranking_cp['equipo'] == equipo_seleccionado].iloc[0]
            st.info("📊 **Datos CP:**")
            st.write(f"**Puntaje Final:** {datos_cp['score_final']:.2f}")
            st.write(f"**Posición:** {datos_cp['posicion']}")
            st.write(f"**Categoría:** {datos_cp['categoria']}")
            
            # Mostrar métricas individuales
            st.write("**Métricas CP:**")
            st.write(f"• Llenado: {datos_cp['cp_llenado_score']:.1f} pts")
            st.write(f"• Estabilidad: {datos_cp['cp_inestabilidad_score']:.1f} pts")
            st.write(f"• Tasa de Cambio: {datos_cp['cp_tasa_cambio_score']:.1f} pts")
            
            if 'areas_cp' in datos_cp and datos_cp['areas_cp']:
                st.write(f"**Áreas CP:** {', '.join(datos_cp['areas_cp'])}")
            
            if 'explicacion' in datos_cp:
                st.write(f"**Explicación:** {datos_cp['explicacion']}")
            
            if 'recomendaciones' in datos_cp:
                st.write(f"**Recomendaciones:** {datos_cp['recomendaciones']}")
        else:
            st.warning("❌ Este equipo no tiene datos CP")
    
    with col2:
        if equipo_seleccionado in equipos_hdd:
            datos_hdd = ranking_hdd[ranking_hdd['equipo'] == equipo_seleccionado].iloc[0]
            st.info("💾 **Datos HDD:**")
            st.write(f"**Puntaje Final:** {datos_hdd['score_final']:.2f}")
            st.write(f"**Posición:** {datos_hdd['posicion']}")
            st.write(f"**Categoría:** {datos_hdd['categoria']}")
            
            # Mostrar métricas individuales
            st.write("**Métricas HDD:**")
            st.write(f"• Uso: {datos_hdd['hdd_uso_score']:.1f} pts")
            st.write(f"• Estabilidad: {datos_hdd['hdd_inestabilidad_score']:.1f} pts")
            st.write(f"• Tasa de Cambio: {datos_hdd['hdd_tasa_cambio_score']:.1f} pts")
            
            if 'unidades_hdd' in datos_hdd and datos_hdd['unidades_hdd']:
                st.write(f"**Unidades HDD:** {', '.join(datos_hdd['unidades_hdd'])}")
            
            if 'explicacion' in datos_hdd:
                st.write(f"**Explicación:** {datos_hdd['explicacion']}")
            
            if 'recomendaciones' in datos_hdd:
                st.write(f"**Recomendaciones:** {datos_hdd['recomendaciones']}")
        else:
            st.warning("❌ Este equipo no tiene datos HDD")
    
    # Comparación si el equipo está en ambos rankings
    if equipo_seleccionado in equipos_cp and equipo_seleccionado in equipos_hdd:
        st.subheader("📊 Comparación CP vs HDD")
        
        datos_cp = ranking_cp[ranking_cp['equipo'] == equipo_seleccionado].iloc[0]
        datos_hdd = ranking_hdd[ranking_hdd['equipo'] == equipo_seleccionado].iloc[0]
        
        # Gráfico de radar
        categorias = ['Puntaje CP', 'Puntaje HDD']
        valores = [datos_cp['score_final'], datos_hdd['score_final']]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=valores,
            theta=categorias,
            fill='toself',
            name=equipo_seleccionado
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=False,
            title=f"Perfil de Rendimiento - {equipo_seleccionado}"
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Análisis comparativo
        diferencia = abs(datos_cp['score_final'] - datos_hdd['score_final'])
        if diferencia < 10:
            st.success("✅ **Equilibrio:** El equipo tiene un rendimiento equilibrado en CP y HDD")
        elif datos_cp['score_final'] > datos_hdd['score_final']:
            st.info("⚡ **Fuerte en CP:** El equipo destaca más en procesamiento")
        else:
            st.info("💾 **Fuerte en HDD:** El equipo destaca más en almacenamiento")

elif page == "📊 Comparativas":
    st.header("📊 Comparativas y Análisis")
    
    # Estadísticas comparativas
    st.subheader("📈 Estadísticas Comparativas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Promedio CP",
            value=f"{ranking_cp['score_final'].mean():.1f}",
            delta=f"Max: {ranking_cp['score_final'].max():.1f}"
        )
    
    with col2:
        st.metric(
            label="Promedio HDD",
            value=f"{ranking_hdd['score_final'].mean():.1f}",
            delta=f"Max: {ranking_hdd['score_final'].max():.1f}"
        )
    
    with col3:
        diff_avg = ranking_cp['score_final'].mean() - ranking_hdd['score_final'].mean()
        st.metric(
            label="Diferencia Promedio",
            value=f"{abs(diff_avg):.1f}",
            delta="CP vs HDD"
        )
    
    # Box plot comparativo
    st.subheader("📊 Comparación de Distribuciones")
    
    # Preparar datos para box plot
    cp_data = ranking_cp['score_final'].rename('CP')
    hdd_data = ranking_hdd['score_final'].rename('HDD')
    
    fig_box = go.Figure()
    fig_box.add_trace(go.Box(y=cp_data, name='CP', boxpoints='outliers'))
    fig_box.add_trace(go.Box(y=hdd_data, name='HDD', boxpoints='outliers'))
    
    fig_box.update_layout(
        title="Distribución de Puntajes CP vs HDD",
        yaxis_title="Puntaje Final",
        showlegend=True
    )
    
    st.plotly_chart(fig_box, use_container_width=True)
    
    # Análisis de correlación si hay equipos comunes
    equipos_comunes = set(equipos_cp) & set(equipos_hdd)
    
    if len(equipos_comunes) > 1:
        st.subheader("🔗 Análisis de Correlación")
        
        # Crear DataFrame con equipos comunes
        datos_comunes = []
        for equipo in equipos_comunes:
            puntaje_cp = ranking_cp[ranking_cp['equipo'] == equipo]['score_final'].iloc[0]
            puntaje_hdd = ranking_hdd[ranking_hdd['equipo'] == equipo]['score_final'].iloc[0]
            datos_comunes.append({
                'equipo': equipo,
                'puntaje_cp': puntaje_cp,
                'puntaje_hdd': puntaje_hdd
            })
        
        df_comunes = pd.DataFrame(datos_comunes)
        
        # Gráfico de dispersión
        fig_scatter = px.scatter(
            df_comunes,
            x='puntaje_cp',
            y='puntaje_hdd',
            text='equipo',
            title="Correlación CP vs HDD",
            labels={'puntaje_cp': 'Puntaje CP', 'puntaje_hdd': 'Puntaje HDD'}
        )
        
        fig_scatter.update_traces(textposition="top center")
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Calcular correlación
        correlacion = df_comunes['puntaje_cp'].corr(df_comunes['puntaje_hdd'])
        st.info(f"📊 **Coeficiente de correlación:** {correlacion:.3f}")
        
        if correlacion > 0.7:
            st.success("✅ **Alta correlación:** Los equipos que rinden bien en CP también rinden bien en HDD")
        elif correlacion > 0.3:
            st.info("📈 **Correlación moderada:** Hay cierta relación entre el rendimiento CP y HDD")
        else:
            st.warning("⚠️ **Baja correlación:** El rendimiento en CP y HDD son independientes")

elif page == "📋 Explicaciones Detalladas":
    st.header("📋 Explicaciones Detalladas del Sistema de Puntuación")
    
    # Explicación del sistema CP
    st.subheader("⚡ Sistema de Puntuación CP (Procesamiento)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**Métricas CP:**")
        st.write("""
        **1. CP_LLENADO (Ocupación del CPU)**
        - **Objetivo:** Menor ocupación = Mejor rendimiento
        - **Rango típico:** 0-100%
        - **Evaluación:** Menor valor = Mayor puntaje
        
        **2. CP_INESTABILIDAD (Variabilidad del CPU)**
        - **Objetivo:** Menor variabilidad = Mayor estabilidad
        - **Rango típico:** 0-1000+
        - **Evaluación:** Menor valor = Mayor puntaje
        
        **3. CP_TASA_CAMBIO (Cambios en el CPU)**
        - **Objetivo:** Menor tasa de cambio = Mayor estabilidad
        - **Rango típico:** 0-10000+
        - **Evaluación:** Menor valor = Mayor puntaje
        """)
    
    with col2:
        st.info("**Áreas CP Monitoreadas:**")
        st.write("""
        • **PP_NFD:** Procesos por nodo
        • **IOLOAD:** Carga de entrada/salida
        • **totmem:** Memoria total utilizada
        • **CUMOVR:** Cobertura de memoria
        • **OMOVRN:** Overlap de memoria
        • **TLCONS:** Consumo de tiempo
        • **OMLDAV:** Carga promedio
        • **CPLOAD:** Carga del CPU
        • **MAXMEM:** Memoria máxima
        """)
    
    # Explicación del sistema HDD
    st.subheader("💾 Sistema de Puntuación HDD (Almacenamiento)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**Métricas HDD:**")
        st.write("""
        **1. HDD_USO (Uso del disco)**
        - **Objetivo:** Menor uso = Mejor rendimiento
        - **Rango típico:** 0-100%
        - **Evaluación:** Menor valor = Mayor puntaje
        
        **2. HDD_INESTABILIDAD (Variabilidad del disco)**
        - **Objetivo:** Menor variabilidad = Mayor estabilidad
        - **Rango típico:** 0-10+
        - **Evaluación:** Menor valor = Mayor puntaje
        
        **3. HDD_TASA_CAMBIO (Cambios en el disco)**
        - **Objetivo:** Menor tasa de cambio = Mayor estabilidad
        - **Rango típico:** 0-1000+
        - **Evaluación:** Menor valor = Mayor puntaje
        """)
    
    with col2:
        st.info("**Unidades HDD Monitoreadas:**")
        st.write("""
        • **C:, D:, E:, F:, G:, H:, I:, J:, K:, L:, Z:**
        • **avg:** Promedio de todas las unidades
        • **Sistema:** Monitorea múltiples unidades por equipo
        """)
    
    # Categorías de rendimiento
    st.subheader("🏆 Categorías de Rendimiento")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.success("**Excelente (90-100 pts)**")
        st.write("Rendimiento óptimo en todas las métricas")
    
    with col2:
        st.info("**Muy Bueno (75-89 pts)**")
        st.write("Rendimiento muy bueno con mínimas mejoras")
    
    with col3:
        st.warning("**Bueno (50-74 pts)**")
        st.write("Rendimiento aceptable con oportunidades de mejora")
    
    with col4:
        st.error("**Regular/Necesita Mejora (<50 pts)**")
        st.write("Requiere atención inmediata y mejoras significativas")
    
    # Ejemplos de explicaciones
    st.subheader("📝 Ejemplos de Explicaciones")
    
    # Mostrar algunos ejemplos del ranking CP
    st.write("**Ejemplos CP:**")
    ejemplos_cp = ranking_cp.head(3)
    for _, ejemplo in ejemplos_cp.iterrows():
        with st.expander(f"Equipo {ejemplo['equipo']} - Puntaje: {ejemplo['score_final']:.1f}"):
            st.write(f"**Explicación:** {ejemplo['explicacion']}")
            st.write(f"**Recomendaciones:** {ejemplo['recomendaciones']}")
            st.write(f"**Categoría:** {ejemplo['categoria']}")
    
    # Mostrar algunos ejemplos del ranking HDD
    st.write("**Ejemplos HDD:**")
    ejemplos_hdd = ranking_hdd.head(3)
    for _, ejemplo in ejemplos_hdd.iterrows():
        with st.expander(f"Equipo {ejemplo['equipo']} - Puntaje: {ejemplo['score_final']:.1f}"):
            st.write(f"**Explicación:** {ejemplo['explicacion']}")
            st.write(f"**Recomendaciones:** {ejemplo['recomendaciones']}")
            st.write(f"**Categoría:** {ejemplo['categoria']}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>📊 Dashboard de Análisis de Equipos CP-HDD | Desarrollado con Streamlit</p>
        <p>🔄 Sistema de Puntuación Actualizado v2.0</p>
    </div>
    """,
    unsafe_allow_html=True
) 