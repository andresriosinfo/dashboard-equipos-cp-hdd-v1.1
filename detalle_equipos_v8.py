import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import ast

st.set_page_config(page_title="Análisis Detallado de Equipos - V8", layout="wide", page_icon="📊")

# Estilos CSS para colores de recomendaciones
st.markdown("""
<style>
    .recomendacion-verde {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
    }
    .recomendacion-amarilla {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
    }
    .recomendacion-roja {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
    }
    .puntaje-destacado {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        color: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin: 10px 0;
    }
    .indicador-verde {
        color: #28a745;
        font-weight: bold;
    }
    .indicador-amarillo {
        color: #ffc107;
        font-weight: bold;
    }
    .indicador-rojo {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- Cargar datos ---
@st.cache_data
def load_data():
    df_cp = pd.read_csv('ranking_cp_v2.csv')
    df_hdd = pd.read_csv('ranking_hdd_v2.csv')
    return df_cp, df_hdd

def obtener_color_recomendacion(recomendacion_texto):
    """Determinar color de recomendación basado en el texto"""
    if pd.isna(recomendacion_texto):
        return "amarilla"
    
    texto = recomendacion_texto.lower()
    if any(palabra in texto for palabra in ['mantener', 'excelente', 'bueno', 'óptimo']):
        return "verde"
    elif any(palabra in texto for palabra in ['optimizar', 'mejorar', 'revisar', 'monitorear']):
        return "amarilla"
    elif any(palabra in texto for palabra in ['crítico', 'urgente', 'inmediata', 'atención']):
        return "roja"
    else:
        return "amarilla"

def analizar_area_cp_automatico(area, row):
    # Obtener scores disponibles
    llenado_score = row.get('cp_llenado_score', 0)
    inestabilidad_score = row.get('cp_inestabilidad_score', 0)
    tasa_cambio_score = row.get('cp_tasa_cambio_score', 0)
    
    # Análisis basado en scores
    score_promedio = (llenado_score + inestabilidad_score + tasa_cambio_score) / 3
    
    if score_promedio >= 80:
        return {
            'estado': 'EXCELENTE',
            'color': 'verde',
            'problema': 'Rendimiento óptimo',
            'explicacion': f'Score promedio: {score_promedio:.1f}/100 - El área funciona de manera excepcional.',
            'accion': 'Mantener estándares actuales'
        }
    elif score_promedio >= 60:
        return {
            'estado': 'BUENO',
            'color': 'amarillo',
            'problema': 'Rendimiento aceptable',
            'explicacion': f'Score promedio: {score_promedio:.1f}/100 - El área funciona bien con margen de mejora.',
            'accion': 'Monitorear y optimizar gradualmente'
        }
    elif score_promedio >= 40:
        return {
            'estado': 'REGULAR',
            'color': 'amarillo',
            'problema': 'Rendimiento mejorable',
            'explicacion': f'Score promedio: {score_promedio:.1f}/100 - El área necesita optimización.',
            'accion': 'Implementar mejoras específicas'
        }
    else:
        return {
            'estado': 'CRÍTICO',
            'color': 'rojo',
            'problema': 'Rendimiento deficiente',
            'explicacion': f'Score promedio: {score_promedio:.1f}/100 - El área requiere atención inmediata.',
            'accion': 'Revisión urgente y corrección'
        }

def explicar_perfil_rendimiento_cp(row):
    explicacion = []
    
    # Usar los scores disponibles
    llenado_score = row.get('cp_llenado_score', 0)
    inestabilidad_score = row.get('cp_inestabilidad_score', 0)
    tasa_cambio_score = row.get('cp_tasa_cambio_score', 0)
    score_final = row.get('score_final', 0)
    
    # Explicar cada métrica
    if llenado_score >= 80:
        explicacion.append(f"**Llenado: {llenado_score:.1f}/100** - Excelente gestión de carga.")
    elif llenado_score >= 60:
        explicacion.append(f"**Llenado: {llenado_score:.1f}/100** - Buena gestión de carga.")
    else:
        explicacion.append(f"**Llenado: {llenado_score:.1f}/100** - Necesita optimización de carga.")
    
    if inestabilidad_score >= 80:
        explicacion.append(f"**Estabilidad: {inestabilidad_score:.1f}/100** - Muy estable.")
    elif inestabilidad_score >= 60:
        explicacion.append(f"**Estabilidad: {inestabilidad_score:.1f}/100** - Aceptablemente estable.")
    else:
        explicacion.append(f"**Estabilidad: {inestabilidad_score:.1f}/100** - Inestable, requiere atención.")
    
    if tasa_cambio_score >= 80:
        explicacion.append(f"**Predictibilidad: {tasa_cambio_score:.1f}/100** - Muy predecible.")
    elif tasa_cambio_score >= 60:
        explicacion.append(f"**Predictibilidad: {tasa_cambio_score:.1f}/100** - Aceptablemente predecible.")
    else:
        explicacion.append(f"**Predictibilidad: {tasa_cambio_score:.1f}/100** - Impredecible, requiere monitoreo.")
    
    # Explicación general
    if score_final >= 80:
        explicacion.append(f"**Score Final: {score_final:.1f}/100** - Rendimiento excepcional general.")
    elif score_final >= 60:
        explicacion.append(f"**Score Final: {score_final:.1f}/100** - Rendimiento bueno general.")
    elif score_final >= 40:
        explicacion.append(f"**Score Final: {score_final:.1f}/100** - Rendimiento regular que necesita mejora.")
    else:
        explicacion.append(f"**Score Final: {score_final:.1f}/100** - Rendimiento deficiente que requiere atención urgente.")
    
    return explicacion

def explicar_perfil_rendimiento_hdd(row):
    explicacion = []
    
    # Para HDD, usar score_final si existe
    score_final = row.get('score_final', 0)
    
    if score_final >= 80:
        explicacion.append(f"**Rendimiento HDD: {score_final:.1f}/100** - Almacenamiento funcionando excelentemente.")
    elif score_final >= 60:
        explicacion.append(f"**Rendimiento HDD: {score_final:.1f}/100** - Almacenamiento funcionando bien.")
    elif score_final >= 40:
        explicacion.append(f"**Rendimiento HDD: {score_final:.1f}/100** - Almacenamiento necesita optimización.")
    else:
        explicacion.append(f"**Rendimiento HDD: {score_final:.1f}/100** - Almacenamiento requiere atención urgente.")
    
    return explicacion

def crear_radar_cp(row):
    # Crear radar con los scores disponibles
    llenado_score = row.get('cp_llenado_score', 0)
    inestabilidad_score = row.get('cp_inestabilidad_score', 0)
    tasa_cambio_score = row.get('cp_tasa_cambio_score', 0)
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[llenado_score, inestabilidad_score, tasa_cambio_score],
        theta=['Llenado', 'Estabilidad', 'Predictibilidad'],
        fill='toself',
        name='CP',
        line_color='#1f77b4'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=300)
    return fig

def crear_radar_hdd(row):
    # Para HDD, usar score_final como único valor
    score_final = row.get('score_final', 0)
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[score_final, score_final, score_final],  # Mismo valor para las 3 dimensiones
        theta=['Eficiencia', 'Estabilidad', 'Predictibilidad'],
        fill='toself',
        name='HDD',
        line_color='#ff7f0e'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=300)
    return fig

def main():
    st.markdown('<h1 style="text-align:center; color:#1f77b4;">Análisis Detallado de Equipos - V8</h1>', unsafe_allow_html=True)
    df_cp, df_hdd = load_data()
    equipos = sorted(df_cp['equipo'].unique())
    equipo_sel = st.selectbox("Seleccione un equipo para analizar:", equipos)
    row_cp = df_cp[df_cp['equipo'] == equipo_sel].iloc[0]
    row_hdd = df_hdd[df_hdd['equipo'] == equipo_sel].iloc[0] if equipo_sel in df_hdd['equipo'].values else None

    # --- PRIMERA FILA: Información general, puntaje, posición, recomendaciones y perfil ---
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("### Información General del Equipo")
        st.metric("Equipo", equipo_sel)
        st.metric("Posición CP", f"{row_cp['posicion']} de {len(df_cp)}")
        if row_hdd is not None:
            st.metric("Posición HDD", f"{row_hdd['posicion']} de {len(df_hdd)}")
        st.markdown(f"**Categoría CP:** {row_cp['categoria']}")
        if row_hdd is not None:
            st.markdown(f"**Categoría HDD:** {row_hdd.get('categoria', 'Sin categoría')}")
    
    with col2:
        st.markdown("### Puntaje del Equipo")
        # Puntaje CP
        score_cp = row_cp.get('score_final', 0)
        st.markdown(f'<div class="puntaje-destacado">CP: {score_cp:.1f}/100</div>', unsafe_allow_html=True)
        
        # Puntaje HDD si existe
        if row_hdd is not None:
            score_hdd = row_hdd.get('score_final', 0)
            st.markdown(f'<div class="puntaje-destacado">HDD: {score_hdd:.1f}/100</div>', unsafe_allow_html=True)
        
        st.markdown("### Recomendaciones del Sistema")
        
        # Recomendaciones CP
        rec_cp = row_cp['recomendaciones'] if pd.notna(row_cp['recomendaciones']) else "Sin recomendaciones específicas"
        color_cp = obtener_color_recomendacion(rec_cp)
        st.markdown(f'<div class="recomendacion-{color_cp}"><strong>CP:</strong> {rec_cp}</div>', unsafe_allow_html=True)
        
        # Recomendaciones HDD si existe
        if row_hdd is not None:
            rec_hdd = row_hdd['recomendaciones'] if 'recomendaciones' in row_hdd and pd.notna(row_hdd['recomendaciones']) else "Sin recomendaciones específicas"
            color_hdd = obtener_color_recomendacion(rec_hdd)
            st.markdown(f'<div class="recomendacion-{color_hdd}"><strong>HDD:</strong> {rec_hdd}</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown("### Perfil de Rendimiento")
        
        # Mostrar perfil CP solo si tiene datos
        if pd.notna(row_cp.get('score_final', 0)) and row_cp.get('score_final', 0) > 0:
            st.markdown("#### Perfil CP")
            st.plotly_chart(crear_radar_cp(row_cp), use_container_width=True)
            for exp in explicar_perfil_rendimiento_cp(row_cp):
                st.markdown(f"- {exp}")
        else:
            st.info("No hay datos CP suficientes para este equipo.")
        
        # Mostrar perfil HDD solo si tiene datos
        if row_hdd is not None and pd.notna(row_hdd.get('score_final', 0)) and row_hdd.get('score_final', 0) > 0:
            st.markdown("#### Perfil HDD")
            st.plotly_chart(crear_radar_hdd(row_hdd), use_container_width=True)
            for exp in explicar_perfil_rendimiento_hdd(row_hdd):
                st.markdown(f"- {exp}")
        elif row_hdd is not None:
            st.info("No hay datos HDD suficientes para este equipo.")

    st.markdown("---")
    
    # --- SEGUNDA FILA: Análisis detallado por áreas CP ---
    st.markdown("### Análisis Detallado por Áreas CP")
    
    # Obtener áreas desde la columna areas_cp
    areas_cp_str = row_cp.get('areas_cp', '[]')
    try:
        areas_cp = ast.literal_eval(areas_cp_str) if isinstance(areas_cp_str, str) else areas_cp_str
    except:
        areas_cp = ['CUMOVR', 'IOLOAD', 'CPLOAD', 'totmem', 'OMLDAV', 'TLCONS', 'PP_NFD', 'MAXMEM', 'OMOVRN']
    
    for area in areas_cp:
        analisis = analizar_area_cp_automatico(area, row_cp)
        
        # Crear indicador de estado antes del expander
        if analisis['color'] == 'verde':
            indicador = f"✓ {analisis['estado']}"
            clase_indicador = "indicador-verde"
        elif analisis['color'] == 'amarillo':
            indicador = f"⚠ {analisis['estado']}"
            clase_indicador = "indicador-amarillo"
        else:
            indicador = f"✗ {analisis['estado']}"
            clase_indicador = "indicador-rojo"
        
        with st.expander(f"Área {area} - {indicador}", expanded=False):
            st.markdown(f'<span class="{clase_indicador}">Estado: {analisis["estado"]}</span>', unsafe_allow_html=True)
            st.markdown(f"**Problema:** {analisis['problema']}")
            st.markdown(f"**Explicación:** {analisis['explicacion']}")
            st.markdown(f"**Acción sugerida:** {analisis['accion']}")

if __name__ == "__main__":
    main() 