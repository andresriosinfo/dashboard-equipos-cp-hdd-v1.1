import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import ast

st.set_page_config(page_title="Detalle de Equipos V4 - CP & HDD", layout="wide", page_icon="🔍")

# --- Cargar datos ---
@st.cache_data
def load_data():
    df_cp = pd.read_csv('ranking_cp.csv')
    df_hdd = pd.read_csv('ranking_hdd.csv')
    
    # Convertir columnas de listas si existen
    if 'areas_cp' in df_cp.columns:
        df_cp['areas_cp'] = df_cp['areas_cp'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    if 'unidades_hdd' in df_hdd.columns:
        df_hdd['unidades_hdd'] = df_hdd['unidades_hdd'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    
    return df_cp, df_hdd

df_cp, df_hdd = load_data()

# --- Funciones para análisis automático por área CP ---
def analizar_area_cp_automatico(area, row):
    """Analiza automáticamente qué está pasando en cada área específica de CP"""
    
    # Obtener valores de las métricas
    llenado = row.get('cp_llenado', 0)
    inestabilidad = row.get('cp_inestabilidad', 0)
    tasa_cambio = row.get('cp_tasa_cambio', 0)
    
    # Análisis específico por área
    if area == 'PP_NFD':
        if llenado > 8000:
            return {
                'estado': '🔴 CRÍTICO',
                'problema': 'Sobrecarga de procesos por nodo',
                'explicacion': f'El equipo tiene {llenado:.0f} procesos por nodo, lo que indica una sobrecarga severa del sistema. Esto puede causar lentitud y bloqueos.',
                'accion': 'Reducir inmediatamente la carga de procesos o escalar recursos'
            }
        elif llenado > 5000:
            return {
                'estado': '🟡 ADVERTENCIA',
                'problema': 'Alta carga de procesos',
                'explicacion': f'Con {llenado:.0f} procesos por nodo, el sistema está trabajando al límite de su capacidad.',
                'accion': 'Optimizar procesos y monitorear rendimiento'
            }
        else:
            return {
                'estado': '🟢 NORMAL',
                'problema': 'Carga de procesos equilibrada',
                'explicacion': f'El equipo maneja {llenado:.0f} procesos por nodo de manera eficiente.',
                'accion': 'Mantener configuración actual'
            }
    
    elif area == 'IOLOAD':
        if inestabilidad > 200:
            return {
                'estado': '🔴 CRÍTICO',
                'problema': 'Cuellos de botella en entrada/salida',
                'explicacion': f'La variabilidad de {inestabilidad:.0f} indica problemas severos en operaciones de disco que están afectando el rendimiento.',
                'accion': 'Revisar discos, optimizar consultas y reducir operaciones I/O'
            }
        elif inestabilidad > 100:
            return {
                'estado': '🟡 ADVERTENCIA',
                'problema': 'Inestabilidad en operaciones I/O',
                'explicacion': f'Las operaciones de entrada/salida muestran variabilidad de {inestabilidad:.0f}, lo que puede causar lentitud.',
                'accion': 'Optimizar patrones de acceso a disco'
            }
        else:
            return {
                'estado': '🟢 NORMAL',
                'problema': 'Operaciones I/O estables',
                'explicacion': f'Las operaciones de entrada/salida son estables con variabilidad de {inestabilidad:.0f}.',
                'accion': 'Mantener configuración actual'
            }
    
    elif area == 'totmem':
        if llenado > 8000:
            return {
                'estado': '🔴 CRÍTICO',
                'problema': 'Uso excesivo de memoria',
                'explicacion': f'El equipo está usando {llenado:.0f}% de memoria, lo que indica posible saturación de RAM.',
                'accion': 'Liberar memoria, cerrar aplicaciones innecesarias o aumentar RAM'
            }
        elif llenado > 5000:
            return {
                'estado': '🟡 ADVERTENCIA',
                'problema': 'Alto uso de memoria',
                'explicacion': f'Con {llenado:.0f}% de uso de memoria, el sistema está cerca de su límite.',
                'accion': 'Optimizar uso de memoria y monitorear aplicaciones'
            }
        else:
            return {
                'estado': '🟢 NORMAL',
                'problema': 'Uso de memoria equilibrado',
                'explicacion': f'El equipo usa {llenado:.0f}% de memoria de manera eficiente.',
                'accion': 'Mantener configuración actual'
            }
    
    elif area == 'CUMOVR':
        if tasa_cambio > 20000:
            return {
                'estado': '🔴 CRÍTICO',
                'problema': 'Cambios bruscos en cobertura de memoria',
                'explicacion': f'La tasa de cambio de {tasa_cambio:.0f} indica fluctuaciones extremas en la gestión de memoria.',
                'accion': 'Revisar aplicaciones que consumen memoria de forma irregular'
            }
        elif tasa_cambio > 10000:
            return {
                'estado': '🟡 ADVERTENCIA',
                'problema': 'Inestabilidad en gestión de memoria',
                'explicacion': f'Los cambios en memoria son variables ({tasa_cambio:.0f}), lo que puede afectar el rendimiento.',
                'accion': 'Optimizar gestión de memoria de aplicaciones'
            }
        else:
            return {
                'estado': '🟢 NORMAL',
                'problema': 'Gestión de memoria estable',
                'explicacion': f'La gestión de memoria es estable con cambios de {tasa_cambio:.0f}.',
                'accion': 'Mantener configuración actual'
            }
    
    elif area == 'OMOVRN':
        if inestabilidad > 150:
            return {
                'estado': '🔴 CRÍTICO',
                'problema': 'Conflicto severo de memoria entre procesos',
                'explicacion': f'La variabilidad de {inestabilidad:.0f} indica conflictos graves entre procesos por memoria.',
                'accion': 'Revisar y optimizar asignación de memoria entre aplicaciones'
            }
        elif inestabilidad > 80:
            return {
                'estado': '🟡 ADVERTENCIA',
                'problema': 'Conflicto moderado de memoria',
                'explicacion': f'Hay conflictos de memoria con variabilidad de {inestabilidad:.0f}.',
                'accion': 'Optimizar distribución de memoria entre procesos'
            }
        else:
            return {
                'estado': '🟢 NORMAL',
                'problema': 'Gestión eficiente de memoria entre procesos',
                'explicacion': f'Los procesos comparten memoria eficientemente con variabilidad de {inestabilidad:.0f}.',
                'accion': 'Mantener configuración actual'
            }
    
    elif area == 'TLCONS':
        if llenado > 7000:
            return {
                'estado': '🔴 CRÍTICO',
                'problema': 'Consumo excesivo de tiempo de CPU',
                'explicacion': f'El equipo consume {llenado:.0f}% de tiempo de CPU, indicando procesos muy demandantes.',
                'accion': 'Identificar y optimizar procesos que consumen demasiado CPU'
            }
        elif llenado > 4000:
            return {
                'estado': '🟡 ADVERTENCIA',
                'problema': 'Alto consumo de tiempo de CPU',
                'explicacion': f'El consumo de {llenado:.0f}% de CPU está en el límite aceptable.',
                'accion': 'Monitorear procesos y optimizar los más demandantes'
            }
        else:
            return {
                'estado': '🟢 NORMAL',
                'problema': 'Consumo equilibrado de CPU',
                'explicacion': f'El equipo consume {llenado:.0f}% de CPU de manera eficiente.',
                'accion': 'Mantener configuración actual'
            }
    
    elif area == 'OMLDAV':
        if inestabilidad > 120:
            return {
                'estado': '🔴 CRÍTICO',
                'problema': 'Carga promedio muy inestable',
                'explicacion': f'La carga promedio varía {inestabilidad:.0f} puntos, indicando picos severos de actividad.',
                'accion': 'Estabilizar carga de trabajo y revisar procesos críticos'
            }
        elif inestabilidad > 60:
            return {
                'estado': '🟡 ADVERTENCIA',
                'problema': 'Carga promedio variable',
                'explicacion': f'La carga promedio muestra variabilidad de {inestabilidad:.0f} puntos.',
                'accion': 'Optimizar distribución de carga de trabajo'
            }
        else:
            return {
                'estado': '🟢 NORMAL',
                'problema': 'Carga promedio estable',
                'explicacion': f'La carga promedio es estable con variabilidad de {inestabilidad:.0f} puntos.',
                'accion': 'Mantener configuración actual'
            }
    
    elif area == 'CPLOAD':
        if llenado > 7500:
            return {
                'estado': '🔴 CRÍTICO',
                'problema': 'Carga del CPU al límite',
                'explicacion': f'El CPU está al {llenado:.0f}% de su capacidad, lo que puede causar lentitud general.',
                'accion': 'Reducir carga de trabajo o escalar recursos de CPU'
            }
        elif llenado > 5000:
            return {
                'estado': '🟡 ADVERTENCIA',
                'problema': 'Carga alta del CPU',
                'explicacion': f'El CPU está al {llenado:.0f}% de capacidad, cerca del límite recomendado.',
                'accion': 'Optimizar procesos y monitorear carga'
            }
        else:
            return {
                'estado': '🟢 NORMAL',
                'problema': 'Carga del CPU equilibrada',
                'explicacion': f'El CPU funciona al {llenado:.0f}% de capacidad de manera eficiente.',
                'accion': 'Mantener configuración actual'
            }
    
    elif area == 'MAXMEM':
        if tasa_cambio > 15000:
            return {
                'estado': '🔴 CRÍTICO',
                'problema': 'Cambios extremos en uso máximo de memoria',
                'explicacion': f'El uso máximo de memoria cambia {tasa_cambio:.0f} puntos, indicando picos peligrosos.',
                'accion': 'Revisar aplicaciones que consumen memoria de forma irregular'
            }
        elif tasa_cambio > 8000:
            return {
                'estado': '🟡 ADVERTENCIA',
                'problema': 'Cambios variables en memoria máxima',
                'explicacion': f'El uso máximo de memoria varía {tasa_cambio:.0f} puntos.',
                'accion': 'Optimizar gestión de memoria de aplicaciones'
            }
        else:
            return {
                'estado': '🟢 NORMAL',
                'problema': 'Uso máximo de memoria estable',
                'explicacion': f'El uso máximo de memoria es estable con cambios de {tasa_cambio:.0f} puntos.',
                'accion': 'Mantener configuración actual'
            }
    
    else:
        return {
            'estado': '⚪ SIN DATOS',
            'problema': 'Área no analizada',
            'explicacion': f'No hay datos suficientes para analizar el área {area}.',
            'accion': 'Recopilar más datos de esta área'
        }

def generar_recomendaciones_simples_cp(row):
    """Genera recomendaciones simples y directas para CP"""
    recomendaciones = []
    
    score_promedio = (row.get('cp_llenado_score', 0) + row.get('cp_inestabilidad_score', 0) + row.get('cp_tasa_cambio_score', 0)) / 3
    
    if score_promedio >= 80:
        recomendaciones.append("✅ **Todo está funcionando bien. Mantener la configuración actual.**")
    elif score_promedio >= 60:
        recomendaciones.append("⚠️ **Hay algunas mejoras posibles. Revisar las áreas problemáticas.**")
    elif score_promedio >= 40:
        recomendaciones.append("🔴 **Se necesitan mejoras importantes. Implementar las acciones sugeridas.**")
    else:
        recomendaciones.append("🚨 **Se requiere atención inmediata. Seguir todas las recomendaciones críticas.**")
    
    return recomendaciones

def generar_recomendaciones_simples_hdd(row):
    """Genera recomendaciones simples y directas para HDD"""
    recomendaciones = []
    
    score_hdd = row.get('score_final', 0)
    
    if score_hdd >= 80:
        recomendaciones.append("✅ **El almacenamiento funciona muy bien. Mantener las prácticas actuales.**")
    elif score_hdd >= 60:
        recomendaciones.append("⚠️ **El almacenamiento funciona bien con algunas mejoras posibles.**")
    elif score_hdd >= 40:
        recomendaciones.append("🔴 **El almacenamiento necesita optimización. Revisar gestión de archivos.**")
    else:
        recomendaciones.append("🚨 **El almacenamiento requiere atención urgente. Implementar limpieza y optimización.**")
    
    return recomendaciones

# --- Interfaz principal ---
st.title("🔍 Análisis de Equipo")
st.markdown("### Sistema de Evaluación Automática de Rendimiento")

# --- Selector de equipo ---
all_equipos = sorted(set(df_cp['equipo']).union(set(df_hdd['equipo'])), key=lambda x: str(x))
equipo_sel = st.selectbox("Selecciona un equipo:", all_equipos)

if equipo_sel:
    st.markdown("---")
    
    # --- INFORMACIÓN GENERAL Y PUNTAJES ---
    st.subheader("📊 Información General")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Equipo", equipo_sel)
    
    with col2:
        st.metric("Fecha de Análisis", datetime.now().strftime('%d/%m/%Y'))
    
    with col3:
        # Puntaje CP
        row_cp = df_cp[df_cp['equipo'] == equipo_sel]
        if not row_cp.empty:
            score_cp = row_cp.iloc[0]['score_final']
            st.metric("Puntaje CP", f"{score_cp:.1f}/100")
        else:
            st.metric("Puntaje CP", "N/A")
    
    with col4:
        # Puntaje HDD
        row_hdd = df_hdd[df_hdd['equipo'] == equipo_sel]
        if not row_hdd.empty:
            score_hdd = row_hdd.iloc[0]['score_final']
            st.metric("Puntaje HDD", f"{score_hdd:.1f}/100")
        else:
            st.metric("Puntaje HDD", "N/A")
    
    # --- TABLA DE RANKINGS ---
    st.markdown("#### 📈 Posición en Rankings")
    
    # Crear tabla de rankings
    ranking_data = []
    
    if not row_cp.empty:
        ranking_data.append({
            'Tipo': 'CP (Procesamiento)',
            'Posición': f"#{row_cp.iloc[0]['posicion']} de {len(df_cp)}",
            'Puntaje': f"{row_cp.iloc[0]['score_final']:.1f}/100",
            'Categoría': row_cp.iloc[0]['categoria']
        })
    
    if not row_hdd.empty:
        ranking_data.append({
            'Tipo': 'HDD (Almacenamiento)',
            'Posición': f"#{row_hdd.iloc[0]['posicion']} de {len(df_hdd)}",
            'Puntaje': f"{row_hdd.iloc[0]['score_final']:.1f}/100",
            'Categoría': row_hdd.iloc[0]['categoria']
        })
    
    if ranking_data:
        df_ranking = pd.DataFrame(ranking_data)
        st.dataframe(df_ranking, use_container_width=True, hide_index=True)
    
    # --- RECOMENDACIONES DEL SISTEMA ---
    st.markdown("---")
    st.subheader("💡 Recomendaciones del Sistema")
    
    if not row_cp.empty:
        st.markdown("#### 🔧 Procesamiento (CP)")
        recomendaciones_cp = generar_recomendaciones_simples_cp(row_cp.iloc[0])
        for rec in recomendaciones_cp:
            st.markdown(rec)
    
    if not row_hdd.empty:
        st.markdown("#### 💾 Almacenamiento (HDD)")
        recomendaciones_hdd = generar_recomendaciones_simples_hdd(row_hdd.iloc[0])
        for rec in recomendaciones_hdd:
            st.markdown(rec)
    
    # --- EXPLICACIÓN DEL PUNTAJE CP ---
    if not row_cp.empty:
        st.markdown("---")
        st.subheader("🖥️ Explicación del Puntaje - Procesamiento (CP)")
        
        # Perfil de rendimiento
        st.markdown("#### 📊 Perfil de Rendimiento")
        
        col5, col6 = st.columns(2)
        
        with col5:
            # Gráfico de radar
            if pd.notna(row_cp.iloc[0].get('cp_llenado_score')) and pd.notna(row_cp.iloc[0].get('cp_inestabilidad_score')) and pd.notna(row_cp.iloc[0].get('cp_tasa_cambio_score')):
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=[row_cp.iloc[0]['cp_llenado_score'], row_cp.iloc[0]['cp_inestabilidad_score'], row_cp.iloc[0]['cp_tasa_cambio_score']],
                    theta=['Eficiencia', 'Estabilidad', 'Predecibilidad'],
                    fill='toself',
                    name='Rendimiento CP',
                    line_color='#1f77b4',
                    fillcolor='rgba(31, 119, 180, 0.3)'
                ))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True, 
                            range=[0, 100],
                            ticktext=['0', '25', '50', '75', '100'],
                            tickvals=[0, 25, 50, 75, 100]
                        )
                    ),
                    showlegend=False,
                    title="Perfil de Rendimiento CP",
                    title_x=0.5,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col6:
            st.markdown("**Interpretación del gráfico:**")
            st.markdown("• **Eficiencia:** Qué tan bien usa el equipo sus recursos")
            st.markdown("• **Estabilidad:** Qué tan consistente es el rendimiento")
            st.markdown("• **Predecibilidad:** Qué tan predecibles son los cambios")
            st.markdown("")
            st.markdown("**Área más grande = Mejor rendimiento**")
            
            # Puntaje general CP
            score_cp = row_cp.iloc[0]['score_final']
            st.metric("Puntaje General CP", f"{score_cp:.1f}/100")
            
            if score_cp >= 80:
                st.success("🎉 **Excelente rendimiento**")
            elif score_cp >= 60:
                st.info("👍 **Buen rendimiento**")
            elif score_cp >= 40:
                st.warning("⚠️ **Rendimiento regular**")
            else:
                st.error("🚨 **Rendimiento bajo**")
        
        # Explicación del puntaje por área
        st.markdown("#### 🔍 Análisis por Área")
        areas_cp = row_cp.iloc[0].get('areas_cp', [])
        if isinstance(areas_cp, str):
            try:
                areas_cp = ast.literal_eval(areas_cp)
            except:
                areas_cp = [areas_cp]
        
        if areas_cp:
            for area in areas_cp:
                analisis = analizar_area_cp_automatico(area, row_cp.iloc[0])
                
                with st.expander(f"{analisis['estado']} {area}", expanded=True):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown(f"**Problema detectado:** {analisis['problema']}")
                        st.markdown(f"**Explicación:** {analisis['explicacion']}")
                    
                    with col_b:
                        st.markdown(f"**Acción recomendada:** {analisis['accion']}")
                        
                        # Mostrar valores relevantes
                        if area in ['PP_NFD', 'totmem', 'TLCONS', 'CPLOAD']:
                            valor = row_cp.iloc[0].get('cp_llenado', 0)
                            st.metric(f"Valor {area}", f"{valor:.0f}")
                        elif area in ['IOLOAD', 'OMOVRN', 'OMLDAV']:
                            valor = row_cp.iloc[0].get('cp_inestabilidad', 0)
                            st.metric(f"Variabilidad {area}", f"{valor:.0f}")
                        elif area in ['CUMOVR', 'MAXMEM']:
                            valor = row_cp.iloc[0].get('cp_tasa_cambio', 0)
                            st.metric(f"Cambios {area}", f"{valor:.0f}")
    
    # --- EXPLICACIÓN DEL PUNTAJE HDD ---
    if not row_hdd.empty:
        st.markdown("---")
        st.subheader("💾 Explicación del Puntaje - Almacenamiento (HDD)")
        
        col7, col8 = st.columns(2)
        
        with col7:
            # Gráfico de radar HDD
            if pd.notna(row_hdd.iloc[0].get('hdd_uso_score')) and pd.notna(row_hdd.iloc[0].get('hdd_inestabilidad_score')) and pd.notna(row_hdd.iloc[0].get('hdd_tasa_cambio_score')):
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=[row_hdd.iloc[0]['hdd_uso_score'], row_hdd.iloc[0]['hdd_inestabilidad_score'], row_hdd.iloc[0]['hdd_tasa_cambio_score']],
                    theta=['Uso Eficiente', 'Estabilidad', 'Cambios Controlados'],
                    fill='toself',
                    name='Rendimiento HDD',
                    line_color='#2ca02c',
                    fillcolor='rgba(44, 160, 44, 0.3)'
                ))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True, 
                            range=[0, 100],
                            ticktext=['0', '25', '50', '75', '100'],
                            tickvals=[0, 25, 50, 75, 100]
                        )
                    ),
                    showlegend=False,
                    title="Perfil de Rendimiento HDD",
                    title_x=0.5,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col8:
            st.markdown("**Interpretación del gráfico:**")
            st.markdown("• **Uso Eficiente:** Qué tan bien gestiona el espacio")
            st.markdown("• **Estabilidad:** Qué tan consistente es el rendimiento")
            st.markdown("• **Cambios Controlados:** Qué tan predecibles son los cambios")
            st.markdown("")
            st.markdown("**Área más grande = Mejor rendimiento**")
            
            # Puntaje general HDD
            score_hdd = row_hdd.iloc[0]['score_final']
            st.metric("Puntaje General HDD", f"{score_hdd:.1f}/100")
            
            if score_hdd >= 80:
                st.success("🎉 **Excelente rendimiento**")
            elif score_hdd >= 60:
                st.info("👍 **Buen rendimiento**")
            elif score_hdd >= 40:
                st.warning("⚠️ **Rendimiento regular**")
            else:
                st.error("🚨 **Rendimiento bajo**")
            
            # Unidades HDD
            unidades_hdd = row_hdd.iloc[0].get('unidades_hdd', [])
            if unidades_hdd:
                st.markdown(f"**💽 Unidades monitoreadas:** {', '.join(unidades_hdd)}")

st.markdown("---")
st.caption("Desarrollado por InfoDesign Colombia | Análisis Automático V4.0 | 2024") 