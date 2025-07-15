import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import ast

st.set_page_config(page_title="Detalle de Equipos V3 - CP & HDD", layout="wide", page_icon="🔍")

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

def generar_explicacion_simple_cp(row):
    """Genera explicación simple y clara de las métricas CP"""
    explicacion = []
    
    # CP_LLENADO
    if pd.notna(row.get('cp_llenado')):
        llenado_score = row.get('cp_llenado_score', 0)
        llenado_valor = row['cp_llenado']
        
        if llenado_score >= 80:
            explicacion.append(f"✅ **El equipo está funcionando muy bien** ({llenado_score:.0f}pts)")
        elif llenado_score >= 60:
            explicacion.append(f"⚠️ **El equipo funciona bien pero puede mejorar** ({llenado_score:.0f}pts)")
        elif llenado_score >= 40:
            explicacion.append(f"🔴 **El equipo tiene problemas que necesitan atención** ({llenado_score:.0f}pts)")
        else:
            explicacion.append(f"🚨 **El equipo tiene problemas críticos** ({llenado_score:.0f}pts)")
    
    # CP_INESTABILIDAD
    if pd.notna(row.get('cp_inestabilidad')):
        inestabilidad_score = row.get('cp_inestabilidad_score', 0)
        
        if inestabilidad_score >= 80:
            explicacion.append(f"✅ **El rendimiento es muy estable** ({inestabilidad_score:.0f}pts)")
        elif inestabilidad_score >= 60:
            explicacion.append(f"⚠️ **El rendimiento es aceptable pero variable** ({inestabilidad_score:.0f}pts)")
        elif inestabilidad_score >= 40:
            explicacion.append(f"🔴 **El rendimiento es inestable** ({inestabilidad_score:.0f}pts)")
        else:
            explicacion.append(f"🚨 **El rendimiento es muy inestable** ({inestabilidad_score:.0f}pts)")
    
    # CP_TASA_CAMBIO
    if pd.notna(row.get('cp_tasa_cambio')):
        cambio_score = row.get('cp_tasa_cambio_score', 0)
        
        if cambio_score >= 80:
            explicacion.append(f"✅ **Los cambios son predecibles** ({cambio_score:.0f}pts)")
        elif cambio_score >= 60:
            explicacion.append(f"⚠️ **Los cambios son manejables** ({cambio_score:.0f}pts)")
        elif cambio_score >= 40:
            explicacion.append(f"🔴 **Los cambios son impredecibles** ({cambio_score:.0f}pts)")
        else:
            explicacion.append(f"🚨 **Los cambios son muy bruscos** ({cambio_score:.0f}pts)")
    
    return " ".join(explicacion)

def generar_recomendaciones_simples_cp(row):
    """Genera recomendaciones simples y directas"""
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

# --- Interfaz principal ---
st.title("🔍 Detalle Completo de Equipos V3")
st.markdown("### Análisis Automático por Área - Sin Interpretación Técnica")
st.markdown("El sistema analiza automáticamente cada área y te dice exactamente qué está pasando.")

# --- Selector de equipo ---
all_equipos = sorted(set(df_cp['equipo']).union(set(df_hdd['equipo'])), key=lambda x: str(x))
equipo_sel = st.selectbox("Selecciona un equipo para análisis automático:", all_equipos)

if equipo_sel:
    st.markdown("---")
    
    # --- Información del equipo ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📋 Información General")
        st.write(f"**Equipo:** {equipo_sel}")
        st.write(f"**Fecha de análisis:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        st.write(f"**Versión:** V3.0 - Análisis Automático")
    
    with col2:
        st.subheader("📊 Posición en Rankings")
        row_cp = df_cp[df_cp['equipo'] == equipo_sel]
        row_hdd = df_hdd[df_hdd['equipo'] == equipo_sel]
        
        if not row_cp.empty:
            st.metric("Ranking CP", f"#{row_cp.iloc[0]['posicion']} de {len(df_cp)}")
        else:
            st.metric("Ranking CP", "Sin datos")
            
        if not row_hdd.empty:
            st.metric("Ranking HDD", f"#{row_hdd.iloc[0]['posicion']} de {len(df_hdd)}")
        else:
            st.metric("Ranking HDD", "Sin datos")
    
    with col3:
        st.subheader("🎯 Categorías")
        if not row_cp.empty:
            categoria_cp = row_cp.iloc[0]['categoria']
            if categoria_cp == 'Excelente':
                st.success(f"**CP:** {categoria_cp}")
            elif categoria_cp == 'Muy Bueno':
                st.info(f"**CP:** {categoria_cp}")
            elif categoria_cp == 'Bueno':
                st.warning(f"**CP:** {categoria_cp}")
            else:
                st.error(f"**CP:** {categoria_cp}")
        else:
            st.write("**CP:** Sin datos")
            
        if not row_hdd.empty:
            categoria_hdd = row_hdd.iloc[0]['categoria']
            if categoria_hdd == 'Excelente':
                st.success(f"**HDD:** {categoria_hdd}")
            elif categoria_hdd == 'Muy Bueno':
                st.info(f"**HDD:** {categoria_hdd}")
            elif categoria_hdd == 'Bueno':
                st.warning(f"**HDD:** {categoria_hdd}")
            else:
                st.error(f"**HDD:** {categoria_hdd}")
        else:
            st.write("**HDD:** Sin datos")
    
    # --- Análisis CP Automático ---
    if not row_cp.empty:
        st.markdown("---")
        st.subheader("🖥️ Análisis Automático - CP (Procesamiento)")
        
        # Resumen simple
        st.markdown("#### 📝 Resumen General")
        explicacion_simple = generar_explicacion_simple_cp(row_cp.iloc[0])
        st.markdown(explicacion_simple)
        
        # Recomendaciones simples
        st.markdown("#### 💡 Recomendación General")
        recomendaciones_simples = generar_recomendaciones_simples_cp(row_cp.iloc[0])
        for rec in recomendaciones_simples:
            st.markdown(rec)
        
        # Análisis automático por área
        st.markdown("#### 🔍 Análisis Automático por Área")
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
        
        # Gráfico de radar simplificado
        st.markdown("#### 📊 Perfil de Rendimiento")
        col4, col5 = st.columns(2)
        
        with col4:
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
        
        with col5:
            st.markdown("**Interpretación del gráfico:**")
            st.markdown("• **Eficiencia:** Qué tan bien usa el equipo sus recursos")
            st.markdown("• **Estabilidad:** Qué tan consistente es el rendimiento")
            st.markdown("• **Predecibilidad:** Qué tan predecibles son los cambios")
            st.markdown("")
            st.markdown("**Área más grande = Mejor rendimiento**")
    
    # --- Análisis HDD (mantener similar pero simplificado) ---
    if not row_hdd.empty:
        st.markdown("---")
        st.subheader("💾 Análisis - HDD (Almacenamiento)")
        
        col6, col7 = st.columns(2)
        
        with col6:
            st.metric("Score HDD", f"{row_hdd.iloc[0]['score_final']:.2f}/100")
            
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
        
        with col7:
            st.markdown("#### 📝 Estado del Almacenamiento")
            score_hdd = row_hdd.iloc[0]['score_final']
            
            if score_hdd >= 80:
                st.success("✅ **El almacenamiento funciona muy bien**")
                st.markdown("El equipo gestiona eficientemente su espacio de disco.")
            elif score_hdd >= 60:
                st.info("⚠️ **El almacenamiento funciona bien**")
                st.markdown("Hay algunas oportunidades de mejora en la gestión de archivos.")
            elif score_hdd >= 40:
                st.warning("🔴 **El almacenamiento necesita atención**")
                st.markdown("Se requieren mejoras en la gestión de espacio y archivos.")
            else:
                st.error("🚨 **El almacenamiento tiene problemas críticos**")
                st.markdown("Se necesita intervención inmediata para optimizar el disco.")
            
            # Unidades HDD
            unidades_hdd = row_hdd.iloc[0].get('unidades_hdd', [])
            if unidades_hdd:
                st.markdown(f"**💽 Unidades monitoreadas:** {', '.join(unidades_hdd)}")
    
    # --- Resumen ejecutivo simplificado ---
    if not row_cp.empty or not row_hdd.empty:
        st.markdown("---")
        st.subheader("📋 Resumen Ejecutivo")
        
        if not row_cp.empty and not row_hdd.empty:
            score_cp = row_cp.iloc[0]['score_final']
            score_hdd = row_hdd.iloc[0]['score_final']
            score_promedio = (score_cp + score_hdd) / 2
            
            col8, col9, col10 = st.columns(3)
            
            with col8:
                st.metric("Score CP", f"{score_cp:.2f}/100")
            with col9:
                st.metric("Score HDD", f"{score_hdd:.2f}/100")
            with col10:
                st.metric("Score General", f"{score_promedio:.2f}/100")
            
            # Evaluación general simple
            if score_promedio >= 80:
                st.success("🎉 **El equipo funciona excelentemente**. No se requieren acciones inmediatas.")
            elif score_promedio >= 60:
                st.info("👍 **El equipo funciona bien**. Revisar las áreas con problemas menores.")
            elif score_promedio >= 40:
                st.warning("⚠️ **El equipo necesita mejoras**. Seguir las recomendaciones de las áreas problemáticas.")
            else:
                st.error("🚨 **El equipo requiere atención urgente**. Implementar todas las acciones recomendadas.")
        
        elif not row_cp.empty:
            st.info("📊 Solo se tienen datos de procesamiento para este equipo.")
        elif not row_hdd.empty:
            st.info("📊 Solo se tienen datos de almacenamiento para este equipo.")

st.markdown("---")
st.caption("Desarrollado por InfoDesign Colombia | Análisis Automático V3.0 | 2024") 