import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import ast

st.set_page_config(page_title="Dashboard Equipo V6", layout="wide", page_icon="🔍")

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

def explicar_perfil_rendimiento_cp(eficiencia, estabilidad, predecibilidad):
    """Explica el perfil de rendimiento CP con valores específicos"""
    explicacion = []
    
    # Explicar Eficiencia
    if eficiencia >= 80:
        explicacion.append(f"**Eficiencia: {eficiencia:.0f}/100** - El equipo usa sus recursos de manera muy eficiente. Está aprovechando al máximo su capacidad de procesamiento.")
    elif eficiencia >= 60:
        explicacion.append(f"**Eficiencia: {eficiencia:.0f}/100** - El equipo usa sus recursos de manera aceptable, aunque hay margen para optimización.")
    elif eficiencia >= 40:
        explicacion.append(f"**Eficiencia: {eficiencia:.0f}/100** - El equipo podría estar subutilizando sus recursos o tener problemas de configuración.")
    else:
        explicacion.append(f"**Eficiencia: {eficiencia:.0f}/100** - El equipo está significativamente subutilizado o tiene problemas graves de configuración.")
    
    # Explicar Estabilidad
    if estabilidad >= 80:
        explicacion.append(f"**Estabilidad: {estabilidad:.0f}/100** - El rendimiento es muy consistente y predecible. El equipo funciona de manera estable.")
    elif estabilidad >= 60:
        explicacion.append(f"**Estabilidad: {estabilidad:.0f}/100** - El rendimiento es relativamente estable, con algunas fluctuaciones menores.")
    elif estabilidad >= 40:
        explicacion.append(f"**Estabilidad: {estabilidad:.0f}/100** - El rendimiento muestra variabilidad que puede afectar la consistencia.")
    else:
        explicacion.append(f"**Estabilidad: {estabilidad:.0f}/100** - El rendimiento es muy inestable, lo que puede causar problemas de confiabilidad.")
    
    # Explicar Predecibilidad
    if predecibilidad >= 80:
        explicacion.append(f"**Predecibilidad: {predecibilidad:.0f}/100** - Los cambios en el rendimiento son muy predecibles, facilitando la planificación.")
    elif predecibilidad >= 60:
        explicacion.append(f"**Predecibilidad: {predecibilidad:.0f}/100** - Los cambios son manejables y no representan un riesgo significativo.")
    elif predecibilidad >= 40:
        explicacion.append(f"**Predecibilidad: {predecibilidad:.0f}/100** - Los cambios son variables y requieren monitoreo más frecuente.")
    else:
        explicacion.append(f"**Predecibilidad: {predecibilidad:.0f}/100** - Los cambios son muy impredecibles, lo que puede afectar la estabilidad del sistema.")
    
    # Explicación general
    score_promedio = (eficiencia + estabilidad + predecibilidad) / 3
    if score_promedio >= 80:
        explicacion.append("**En general:** El equipo tiene un perfil de rendimiento excelente, con alta eficiencia, estabilidad y predecibilidad.")
    elif score_promedio >= 60:
        explicacion.append("**En general:** El equipo tiene un perfil de rendimiento bueno, con algunas oportunidades de mejora.")
    elif score_promedio >= 40:
        explicacion.append("**En general:** El equipo tiene un perfil de rendimiento regular que requiere optimización en varias áreas.")
    else:
        explicacion.append("**En general:** El equipo tiene un perfil de rendimiento bajo que requiere atención inmediata y mejoras significativas.")
    
    return explicacion

def explicar_perfil_rendimiento_hdd(uso_eficiente, estabilidad, cambios_controlados):
    """Explica el perfil de rendimiento HDD con valores específicos"""
    explicacion = []
    
    # Explicar Uso Eficiente
    if uso_eficiente >= 80:
        explicacion.append(f"**Uso Eficiente: {uso_eficiente:.0f}/100** - El equipo gestiona su espacio de almacenamiento de manera muy eficiente, manteniendo un balance óptimo.")
    elif uso_eficiente >= 60:
        explicacion.append(f"**Uso Eficiente: {uso_eficiente:.0f}/100** - El equipo gestiona su almacenamiento de manera aceptable, con algunas oportunidades de optimización.")
    elif uso_eficiente >= 40:
        explicacion.append(f"**Uso Eficiente: {uso_eficiente:.0f}/100** - El equipo podría estar subutilizando su almacenamiento o tener problemas de gestión de archivos.")
    else:
        explicacion.append(f"**Uso Eficiente: {uso_eficiente:.0f}/100** - El equipo está significativamente subutilizando su almacenamiento o tiene problemas graves de gestión.")
    
    # Explicar Estabilidad
    if estabilidad >= 80:
        explicacion.append(f"**Estabilidad: {estabilidad:.0f}/100** - El rendimiento del disco es muy consistente y confiable.")
    elif estabilidad >= 60:
        explicacion.append(f"**Estabilidad: {estabilidad:.0f}/100** - El rendimiento del disco es relativamente estable, con algunas fluctuaciones menores.")
    elif estabilidad >= 40:
        explicacion.append(f"**Estabilidad: {estabilidad:.0f}/100** - El rendimiento del disco muestra variabilidad que puede afectar la velocidad de acceso.")
    else:
        explicacion.append(f"**Estabilidad: {estabilidad:.0f}/100** - El rendimiento del disco es muy inestable, lo que puede causar lentitud y errores.")
    
    # Explicar Cambios Controlados
    if cambios_controlados >= 80:
        explicacion.append(f"**Cambios Controlados: {cambios_controlados:.0f}/100** - Los cambios en el uso del disco son muy predecibles, facilitando la gestión de almacenamiento.")
    elif cambios_controlados >= 60:
        explicacion.append(f"**Cambios Controlados: {cambios_controlados:.0f}/100** - Los cambios en el almacenamiento son manejables y no representan riesgo significativo.")
    elif cambios_controlados >= 40:
        explicacion.append(f"**Cambios Controlados: {cambios_controlados:.0f}/100** - Los cambios en el almacenamiento son variables y requieren monitoreo más frecuente.")
    else:
        explicacion.append(f"**Cambios Controlados: {cambios_controlados:.0f}/100** - Los cambios en el almacenamiento son muy impredecibles, lo que puede causar problemas de gestión.")
    
    # Explicación general
    score_promedio = (uso_eficiente + estabilidad + cambios_controlados) / 3
    if score_promedio >= 80:
        explicacion.append("**En general:** El equipo tiene un perfil de almacenamiento excelente, con gestión eficiente, estabilidad y cambios controlados.")
    elif score_promedio >= 60:
        explicacion.append("**En general:** El equipo tiene un perfil de almacenamiento bueno, con algunas oportunidades de mejora.")
    elif score_promedio >= 40:
        explicacion.append("**En general:** El equipo tiene un perfil de almacenamiento regular que requiere optimización en varias áreas.")
    else:
        explicacion.append("**En general:** El equipo tiene un perfil de almacenamiento bajo que requiere atención inmediata y mejoras significativas.")
    
    return explicacion

# --- Interfaz principal ---
st.title("🔍 Dashboard de Análisis de Equipo")
st.markdown("### Sistema de Evaluación Automática de Rendimiento")

# --- Selector de equipo ---
all_equipos = sorted(set(df_cp['equipo']).union(set(df_hdd['equipo'])), key=lambda x: str(x))
equipo_sel = st.selectbox("Selecciona un equipo:", all_equipos)

if equipo_sel:
    # --- PRIMERA FILA: INFORMACIÓN GENERAL Y RANKINGS ---
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Información General")
        
        # Información básica en tabla
        row_cp = df_cp[df_cp['equipo'] == equipo_sel]
        row_hdd = df_hdd[df_hdd['equipo'] == equipo_sel]
        
        info_data = [
            {'Campo': 'Equipo', 'Valor': equipo_sel},
            {'Campo': 'Fecha de Análisis', 'Valor': datetime.now().strftime('%d/%m/%Y %H:%M')},
            {'Campo': 'Versión', 'Valor': 'V6.0 - Dashboard'}
        ]
        
        if not row_cp.empty:
            info_data.append({'Campo': 'Puntaje CP', 'Valor': f"{row_cp.iloc[0]['score_final']:.1f}/100"})
        if not row_hdd.empty:
            info_data.append({'Campo': 'Puntaje HDD', 'Valor': f"{row_hdd.iloc[0]['score_final']:.1f}/100"})
        
        df_info = pd.DataFrame(info_data)
        st.dataframe(df_info, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("📈 Rankings")
        
        # Tabla de rankings compacta
        ranking_data = []
        
        if not row_cp.empty:
            ranking_data.append({
                'Tipo': 'CP',
                'Posición': f"#{row_cp.iloc[0]['posicion']}",
                'Categoría': row_cp.iloc[0]['categoria']
            })
        
        if not row_hdd.empty:
            ranking_data.append({
                'Tipo': 'HDD',
                'Posición': f"#{row_hdd.iloc[0]['posicion']}",
                'Categoría': row_hdd.iloc[0]['categoria']
            })
        
        if ranking_data:
            df_ranking = pd.DataFrame(ranking_data)
            st.dataframe(df_ranking, use_container_width=True, hide_index=True)
    
    # --- SEGUNDA FILA: RECOMENDACIONES Y PUNTUACIONES ---
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("💡 Recomendaciones del Sistema")
        
        if not row_cp.empty:
            st.markdown("**🔧 Procesamiento (CP)**")
            recomendaciones_cp = generar_recomendaciones_simples_cp(row_cp.iloc[0])
            for rec in recomendaciones_cp:
                st.markdown(rec)
        
        if not row_hdd.empty:
            st.markdown("**💾 Almacenamiento (HDD)**")
            recomendaciones_hdd = generar_recomendaciones_simples_hdd(row_hdd.iloc[0])
            for rec in recomendaciones_hdd:
                st.markdown(rec)
    
    with col4:
        st.subheader("🎯 Evaluación General")
        
        if not row_cp.empty and not row_hdd.empty:
            score_cp = row_cp.iloc[0]['score_final']
            score_hdd = row_hdd.iloc[0]['score_final']
            score_promedio = (score_cp + score_hdd) / 2
            
            st.metric("Puntaje Promedio", f"{score_promedio:.1f}/100")
            
            if score_promedio >= 80:
                st.success("🎉 **Excelente rendimiento general**")
            elif score_promedio >= 60:
                st.info("👍 **Buen rendimiento general**")
            elif score_promedio >= 40:
                st.warning("⚠️ **Rendimiento regular**")
            else:
                st.error("🚨 **Rendimiento bajo**")
        
        elif not row_cp.empty:
            score_cp = row_cp.iloc[0]['score_final']
            st.metric("Puntaje CP", f"{score_cp:.1f}/100")
            if score_cp >= 80:
                st.success("🎉 **Excelente rendimiento CP**")
            elif score_cp >= 60:
                st.info("👍 **Buen rendimiento CP**")
            elif score_cp >= 40:
                st.warning("⚠️ **Rendimiento regular CP**")
            else:
                st.error("🚨 **Rendimiento bajo CP**")
        
        elif not row_hdd.empty:
            score_hdd = row_hdd.iloc[0]['score_final']
            st.metric("Puntaje HDD", f"{score_hdd:.1f}/100")
            if score_hdd >= 80:
                st.success("🎉 **Excelente rendimiento HDD**")
            elif score_hdd >= 60:
                st.info("👍 **Buen rendimiento HDD**")
            elif score_hdd >= 40:
                st.warning("⚠️ **Rendimiento regular HDD**")
            else:
                st.error("🚨 **Rendimiento bajo HDD**")
    
    # --- TERCERA FILA: PERFILES DE RENDIMIENTO ---
    if not row_cp.empty or not row_hdd.empty:
        st.subheader("📊 Perfiles de Rendimiento")
        
        col5, col6 = st.columns(2)
        
        # Perfil CP
        if not row_cp.empty:
            with col5:
                st.markdown("#### 🖥️ Perfil CP")
                
                if pd.notna(row_cp.iloc[0].get('cp_llenado_score')) and pd.notna(row_cp.iloc[0].get('cp_inestabilidad_score')) and pd.notna(row_cp.iloc[0].get('cp_tasa_cambio_score')):
                    eficiencia = row_cp.iloc[0]['cp_llenado_score']
                    estabilidad = row_cp.iloc[0]['cp_inestabilidad_score']
                    predecibilidad = row_cp.iloc[0]['cp_tasa_cambio_score']
                    
                    # Gráfico compacto
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=[eficiencia, estabilidad, predecibilidad],
                        theta=['Eficiencia', 'Estabilidad', 'Predecibilidad'],
                        fill='toself',
                        name='CP',
                        line_color='#1f77b4',
                        fillcolor='rgba(31, 119, 180, 0.3)'
                    ))
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                        showlegend=False,
                        title="CP",
                        height=300
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Explicación compacta
                    explicaciones = explicar_perfil_rendimiento_cp(eficiencia, estabilidad, predecibilidad)
                    for explicacion in explicaciones:
                        st.markdown(explicacion)
        
        # Perfil HDD
        if not row_hdd.empty:
            with col6:
                st.markdown("#### 💾 Perfil HDD")
                
                if pd.notna(row_hdd.iloc[0].get('hdd_uso_score')) and pd.notna(row_hdd.iloc[0].get('hdd_inestabilidad_score')) and pd.notna(row_hdd.iloc[0].get('hdd_tasa_cambio_score')):
                    uso_eficiente = row_hdd.iloc[0]['hdd_uso_score']
                    estabilidad = row_hdd.iloc[0]['hdd_inestabilidad_score']
                    cambios_controlados = row_hdd.iloc[0]['hdd_tasa_cambio_score']
                    
                    # Gráfico compacto
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=[uso_eficiente, estabilidad, cambios_controlados],
                        theta=['Uso Eficiente', 'Estabilidad', 'Cambios Controlados'],
                        fill='toself',
                        name='HDD',
                        line_color='#2ca02c',
                        fillcolor='rgba(44, 160, 44, 0.3)'
                    ))
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                        showlegend=False,
                        title="HDD",
                        height=300
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Explicación compacta
                    explicaciones = explicar_perfil_rendimiento_hdd(uso_eficiente, estabilidad, cambios_controlados)
                    for explicacion in explicaciones:
                        st.markdown(explicacion)
                    
                    # Unidades HDD
                    unidades_hdd = row_hdd.iloc[0].get('unidades_hdd', [])
                    if unidades_hdd:
                        st.markdown(f"**💽 Unidades:** {', '.join(unidades_hdd)}")
    
    # --- CUARTA FILA: ANÁLISIS POR ÁREA CP ---
    if not row_cp.empty:
        st.subheader("🔍 Análisis por Área - CP")
        
        areas_cp = row_cp.iloc[0].get('areas_cp', [])
        if isinstance(areas_cp, str):
            try:
                areas_cp = ast.literal_eval(areas_cp)
            except:
                areas_cp = [areas_cp]
        
        if areas_cp:
            # Crear columnas dinámicas para las áreas
            num_areas = len(areas_cp)
            if num_areas <= 3:
                cols = st.columns(num_areas)
            else:
                cols = st.columns(3)
            
            for i, area in enumerate(areas_cp):
                col_idx = i % 3
                analisis = analizar_area_cp_automatico(area, row_cp.iloc[0])
                
                with cols[col_idx]:
                    st.markdown(f"**{analisis['estado']} {area}**")
                    st.markdown(f"*{analisis['problema']}*")
                    st.markdown(f"**Acción:** {analisis['accion']}")
                    
                    # Mostrar valor relevante
                    if area in ['PP_NFD', 'totmem', 'TLCONS', 'CPLOAD']:
                        valor = row_cp.iloc[0].get('cp_llenado', 0)
                        st.metric(f"Valor", f"{valor:.0f}")
                    elif area in ['IOLOAD', 'OMOVRN', 'OMLDAV']:
                        valor = row_cp.iloc[0].get('cp_inestabilidad', 0)
                        st.metric(f"Variabilidad", f"{valor:.0f}")
                    elif area in ['CUMOVR', 'MAXMEM']:
                        valor = row_cp.iloc[0].get('cp_tasa_cambio', 0)
                        st.metric(f"Cambios", f"{valor:.0f}")

st.markdown("---")
st.caption("Desarrollado por InfoDesign Colombia | Dashboard V6.0 | 2024") 