import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import ast

st.set_page_config(page_title="Detalle de Equipos V2 - CP & HDD", layout="wide", page_icon="🔍")

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

# --- Funciones para explicaciones por área CP ---
def generar_explicacion_por_area_cp(row):
    """Genera explicaciones específicas por área de CP"""
    explicaciones = []
    
    # Obtener áreas CP
    areas_cp = row.get('areas_cp', [])
    if isinstance(areas_cp, str):
        try:
            areas_cp = ast.literal_eval(areas_cp)
        except:
            areas_cp = [areas_cp]
    
    if not areas_cp:
        return ["No se encontraron áreas CP específicas para este equipo."]
    
    # Explicación por área
    for area in areas_cp:
        if area == 'PP_NFD':
            explicaciones.append("**🔄 PP_NFD (Procesos por Nodo):** Monitorea la distribución de procesos entre nodos del sistema. Una distribución equilibrada mejora el rendimiento general.")
        elif area == 'IOLOAD':
            explicaciones.append("**📊 IOLOAD (Carga de E/S):** Evalúa la intensidad de operaciones de entrada/salida. Valores altos pueden indicar cuellos de botella en el almacenamiento.")
        elif area == 'totmem':
            explicaciones.append("**💾 totmem (Memoria Total):** Controla el uso total de memoria RAM. Un uso eficiente es crucial para el rendimiento del sistema.")
        elif area == 'CUMOVR':
            explicaciones.append("**🔄 CUMOVR (Cobertura de Memoria):** Mide qué tan bien se distribuye la memoria entre procesos. Una buena cobertura optimiza el uso de recursos.")
        elif area == 'OMOVRN':
            explicaciones.append("**⚡ OMOVRN (Overlap de Memoria):** Evalúa la superposición de memoria entre procesos. Menor overlap significa mejor gestión de memoria.")
        elif area == 'TLCONS':
            explicaciones.append("**⏱️ TLCONS (Consumo de Tiempo):** Monitorea el tiempo de CPU consumido por procesos. Ayuda a identificar procesos que consumen demasiados recursos.")
        elif area == 'OMLDAV':
            explicaciones.append("**📈 OMLDAV (Carga Promedio):** Mide la carga promedio del sistema. Valores estables indican un rendimiento predecible.")
        elif area == 'CPLOAD':
            explicaciones.append("**🖥️ CPLOAD (Carga del CPU):** Evalúa la utilización del procesador. Una carga equilibrada es esencial para el rendimiento óptimo.")
        elif area == 'MAXMEM':
            explicaciones.append("**🚀 MAXMEM (Memoria Máxima):** Controla el uso máximo de memoria. Ayuda a prevenir problemas de memoria insuficiente.")
        else:
            explicaciones.append(f"**📋 {area}:** Área específica del sistema que contribuye al rendimiento general del procesamiento.")
    
    return explicaciones

def generar_explicacion_detallada_cp(row):
    """Genera explicación detallada de métricas CP con contexto mejorado"""
    explicacion = []
    
    # CP_LLENADO (Ocupación del CPU)
    if pd.notna(row.get('cp_llenado')):
        llenado_score = row.get('cp_llenado_score', 0)
        llenado_valor = row['cp_llenado']
        
        if llenado_score >= 80:
            explicacion.append(f"**🎯 Ocupación CP Excelente ({llenado_score:.1f}pts)**: El equipo mantiene una ocupación del {llenado_valor:.1f}%, lo que indica un uso **muy eficiente** de los recursos de procesamiento. Esto significa que el equipo está aprovechando al máximo su capacidad de CPU sin sobrecargarse.")
        elif llenado_score >= 60:
            explicacion.append(f"**✅ Ocupación CP Buena ({llenado_score:.1f}pts)**: Con una ocupación del {llenado_valor:.1f}%, el equipo tiene un rendimiento **aceptable** en el uso de CPU. Hay margen para optimización pero el rendimiento es estable.")
        elif llenado_score >= 40:
            explicacion.append(f"**⚠️ Ocupación CP Regular ({llenado_score:.1f}pts)**: La ocupación del {llenado_valor:.1f}% sugiere que el equipo podría estar **subutilizando** sus recursos de procesamiento. Esto puede indicar falta de carga de trabajo o configuración inadecuada.")
        else:
            explicacion.append(f"**🚨 Ocupación CP Baja ({llenado_score:.1f}pts)**: Con solo {llenado_valor:.1f}% de ocupación, el equipo está **significativamente subutilizado**. Esto puede indicar problemas de configuración, carga de trabajo insuficiente o recursos desperdiciados.")
    
    # CP_INESTABILIDAD (Variabilidad del CPU)
    if pd.notna(row.get('cp_inestabilidad')):
        inestabilidad_score = row.get('cp_inestabilidad_score', 0)
        inestabilidad_valor = row['cp_inestabilidad']
        
        if inestabilidad_score >= 80:
            explicacion.append(f"**🎯 Estabilidad CP Excelente ({inestabilidad_score:.1f}pts)**: El equipo muestra una variabilidad muy baja ({inestabilidad_valor:.1f}), indicando un rendimiento **extremadamente consistente** y predecible en el tiempo. Esto es ideal para operaciones críticas.")
        elif inestabilidad_score >= 60:
            explicacion.append(f"**✅ Estabilidad CP Buena ({inestabilidad_score:.1f}pts)**: Con una variabilidad de {inestabilidad_valor:.1f}, el equipo mantiene un rendimiento **relativamente estable**. Las fluctuaciones son mínimas y controladas.")
        elif inestabilidad_score >= 40:
            explicacion.append(f"**⚠️ Estabilidad CP Regular ({inestabilidad_score:.1f}pts)**: La variabilidad de {inestabilidad_valor:.1f} sugiere **fluctuaciones moderadas** en el rendimiento que podrían afectar la consistencia. Se recomienda monitoreo más frecuente.")
        else:
            explicacion.append(f"**🚨 Estabilidad CP Baja ({inestabilidad_score:.1f}pts)**: La alta variabilidad de {inestabilidad_valor:.1f} indica **inestabilidad significativa** en el rendimiento. Esto puede causar problemas de confiabilidad y requiere atención inmediata.")
    
    # CP_TASA_CAMBIO (Cambios en el CPU)
    if pd.notna(row.get('cp_tasa_cambio')):
        cambio_score = row.get('cp_tasa_cambio_score', 0)
        cambio_valor = row['cp_tasa_cambio']
        
        if cambio_score >= 80:
            explicacion.append(f"**🎯 Cambios CP Estables ({cambio_score:.1f}pts)**: Los cambios en el rendimiento son muy predecibles ({cambio_valor:.1f}), lo que facilita la **planificación y gestión de recursos**. El sistema es altamente confiable.")
        elif cambio_score >= 60:
            explicacion.append(f"**✅ Cambios CP Controlados ({cambio_score:.1f}pts)**: Con una tasa de cambio de {cambio_valor:.1f}, los cambios son **manejables** y no representan un riesgo significativo. El sistema es estable.")
        elif cambio_score >= 40:
            explicacion.append(f"**⚠️ Cambios CP Variables ({cambio_score:.1f}pts)**: La tasa de cambio de {cambio_valor:.1f} indica **fluctuaciones** que requieren monitoreo más frecuente. Se recomienda análisis de patrones.")
        else:
            explicacion.append(f"**🚨 Cambios CP Inestables ({cambio_score:.1f}pts)**: La alta tasa de cambio de {cambio_valor:.1f} sugiere cambios **bruscos e impredecibles** que pueden afectar la estabilidad del sistema. Requiere intervención técnica.")
    
    return " ".join(explicacion)

def generar_explicacion_detallada_hdd(row):
    """Genera explicación detallada de métricas HDD con contexto mejorado"""
    explicacion = []
    
    # HDD_USO (Uso del disco)
    if pd.notna(row.get('hdd_uso')):
        uso_score = row.get('hdd_uso_score', 0)
        uso_valor = row['hdd_uso']
        
        if uso_score >= 80:
            explicacion.append(f"**🎯 Uso HDD Excelente ({uso_score:.1f}pts)**: Con un uso del {uso_valor:.1f}%, el equipo mantiene un **balance óptimo** entre utilización y espacio libre. Esto asegura buen rendimiento sin riesgo de saturación del disco.")
        elif uso_score >= 60:
            explicacion.append(f"**✅ Uso HDD Bueno ({uso_score:.1f}pts)**: El uso del {uso_valor:.1f}% está dentro de **parámetros aceptables**. Hay oportunidad para optimizar el almacenamiento pero el rendimiento es adecuado.")
        elif uso_score >= 40:
            explicacion.append(f"**⚠️ Uso HDD Regular ({uso_score:.1f}pts)**: Con {uso_valor:.1f}% de uso, el equipo podría estar **subutilizando** su capacidad de almacenamiento o tener problemas de gestión de archivos.")
        else:
            explicacion.append(f"**🚨 Uso HDD Bajo ({uso_score:.1f}pts)**: El uso de solo {uso_valor:.1f}% indica **subutilización significativa** del almacenamiento. Posiblemente por falta de datos o configuración inadecuada.")
    
    # HDD_INESTABILIDAD (Variabilidad del disco)
    if pd.notna(row.get('hdd_inestabilidad')):
        inestabilidad_score = row.get('hdd_inestabilidad_score', 0)
        inestabilidad_valor = row['hdd_inestabilidad']
        
        if inestabilidad_score >= 80:
            explicacion.append(f"**🎯 Estabilidad HDD Excelente ({inestabilidad_score:.1f}pts)**: La variabilidad de {inestabilidad_valor:.1f} indica un rendimiento de disco **extremadamente consistente**. Esto es ideal para operaciones confiables y críticas.")
        elif inestabilidad_score >= 60:
            explicacion.append(f"**✅ Estabilidad HDD Buena ({inestabilidad_score:.1f}pts)**: Con variabilidad de {inestabilidad_valor:.1f}, el disco mantiene un rendimiento **relativamente estable**. Las fluctuaciones son controladas.")
        elif inestabilidad_score >= 40:
            explicacion.append(f"**⚠️ Estabilidad HDD Regular ({inestabilidad_score:.1f}pts)**: La variabilidad de {inestabilidad_valor:.1f} sugiere **fluctuaciones** que pueden afectar la velocidad de acceso a datos. Se recomienda monitoreo.")
        else:
            explicacion.append(f"**🚨 Estabilidad HDD Baja ({inestabilidad_score:.1f}pts)**: La alta variabilidad de {inestabilidad_valor:.1f} indica **problemas de rendimiento** del disco que pueden causar lentitud y errores. Requiere diagnóstico.")
    
    # HDD_TASA_CAMBIO (Cambios en el disco)
    if pd.notna(row.get('hdd_tasa_cambio')):
        cambio_score = row.get('hdd_tasa_cambio_score', 0)
        cambio_valor = row['hdd_tasa_cambio']
        
        if cambio_score >= 80:
            explicacion.append(f"**🎯 Cambios HDD Estables ({cambio_score:.1f}pts)**: Los cambios en el uso del disco son **muy predecibles** ({cambio_valor:.1f}), facilitando la gestión de almacenamiento y planificación de capacidad.")
        elif cambio_score >= 60:
            explicacion.append(f"**✅ Cambios HDD Controlados ({cambio_score:.1f}pts)**: Con tasa de cambio de {cambio_valor:.1f}, los cambios son **manejables** y no representan riesgo significativo para el almacenamiento.")
        elif cambio_score >= 40:
            explicacion.append(f"**⚠️ Cambios HDD Variables ({cambio_score:.1f}pts)**: La tasa de cambio de {cambio_valor:.1f} requiere **monitoreo más frecuente** del almacenamiento para detectar patrones anómalos.")
        else:
            explicacion.append(f"**🚨 Cambios HDD Inestables ({cambio_score:.1f}pts)**: La alta tasa de cambio de {cambio_valor:.1f} indica cambios **bruscos** que pueden causar problemas de almacenamiento y fragmentación.")
    
    return " ".join(explicacion)

def generar_recomendaciones_mejoradas_cp(row):
    """Genera recomendaciones mejoradas y específicas para CP"""
    recomendaciones = []
    
    # Recomendaciones basadas en CP_LLENADO
    if pd.notna(row.get('cp_llenado')) and row.get('cp_llenado_score', 100) < 50:
        recomendaciones.append("🔧 **Optimizar carga de trabajo**: Considerar redistribuir tareas o aumentar la carga de procesamiento para aprovechar mejor los recursos de CPU. Evaluar si hay procesos inactivos que puedan ser activados.")
    
    if pd.notna(row.get('cp_llenado')) and row.get('cp_llenado_score', 100) < 30:
        recomendaciones.append("⚡ **Revisar configuración de procesos**: El equipo está significativamente subutilizado. Verificar configuraciones de servicios, aplicaciones y carga de trabajo para maximizar el uso de CPU.")
    
    # Recomendaciones basadas en CP_INESTABILIDAD
    if pd.notna(row.get('cp_inestabilidad')) and row.get('cp_inestabilidad_score', 100) < 50:
        recomendaciones.append("📊 **Monitorear procesos problemáticos**: Identificar y resolver procesos que causen picos de CPU. Implementar alertas para detectar patrones de inestabilidad.")
    
    if pd.notna(row.get('cp_inestabilidad')) and row.get('cp_inestabilidad_score', 100) < 30:
        recomendaciones.append("🚨 **Diagnóstico de estabilidad**: La alta inestabilidad requiere análisis profundo. Revisar logs del sistema, procesos críticos y configuraciones de recursos.")
    
    # Recomendaciones basadas en CP_TASA_CAMBIO
    if pd.notna(row.get('cp_tasa_cambio')) and row.get('cp_tasa_cambio_score', 100) < 50:
        recomendaciones.append("⚙️ **Revisar configuración de servicios**: Evaluar configuraciones de procesos y servicios para reducir cambios bruscos en el uso de CPU. Implementar políticas de throttling si es necesario.")
    
    if pd.notna(row.get('cp_tasa_cambio')) and row.get('cp_tasa_cambio_score', 100) < 30:
        recomendaciones.append("🔄 **Estabilizar patrones de uso**: Los cambios muy bruscos indican problemas de configuración. Revisar cron jobs, servicios automáticos y procesos programados.")
    
    # Recomendación general si todo está bien
    if not recomendaciones:
        recomendaciones.append("✅ **Mantener rendimiento actual**: El equipo está funcionando de manera óptima en todas las métricas de procesamiento. Continuar con las prácticas actuales y monitoreo regular.")
    
    return recomendaciones

def generar_recomendaciones_mejoradas_hdd(row):
    """Genera recomendaciones mejoradas y específicas para HDD"""
    recomendaciones = []
    
    # Recomendaciones basadas en HDD_USO
    if pd.notna(row.get('hdd_uso')) and row.get('hdd_uso_score', 100) < 50:
        recomendaciones.append("💾 **Optimizar almacenamiento**: Revisar archivos temporales, logs antiguos, datos no utilizados y aplicaciones obsoletas para liberar espacio en disco.")
    
    if pd.notna(row.get('hdd_uso')) and row.get('hdd_uso_score', 100) < 30:
        recomendaciones.append("🗂️ **Auditoría completa de archivos**: Implementar limpieza automática de archivos temporales, compresión de datos antiguos y migración a almacenamiento secundario.")
    
    # Recomendaciones basadas en HDD_INESTABILIDAD
    if pd.notna(row.get('hdd_inestabilidad')) and row.get('hdd_inestabilidad_score', 100) < 50:
        recomendaciones.append("🔍 **Diagnosticar salud del disco**: Verificar la salud del disco duro, considerar defragmentación, revisar sectores dañados y evaluar necesidad de reemplazo.")
    
    if pd.notna(row.get('hdd_inestabilidad')) and row.get('hdd_inestabilidad_score', 100) < 30:
        recomendaciones.append("🚨 **Evaluación crítica del hardware**: La alta inestabilidad sugiere problemas de hardware. Realizar diagnóstico completo y considerar reemplazo del disco.")
    
    # Recomendaciones basadas en HDD_TASA_CAMBIO
    if pd.notna(row.get('hdd_tasa_cambio')) and row.get('hdd_tasa_cambio_score', 100) < 50:
        recomendaciones.append("📈 **Monitorear crecimiento de datos**: Implementar alertas para detectar cambios bruscos en el uso de almacenamiento. Establecer políticas de retención de datos.")
    
    if pd.notna(row.get('hdd_tasa_cambio')) and row.get('hdd_tasa_cambio_score', 100) < 30:
        recomendaciones.append("🔄 **Estabilizar patrones de almacenamiento**: Los cambios muy bruscos indican problemas de gestión. Revisar procesos de backup, logs y aplicaciones que escriban datos.")
    
    # Recomendación general si todo está bien
    if not recomendaciones:
        recomendaciones.append("✅ **Mantener rendimiento actual**: El almacenamiento está funcionando de manera óptima. Continuar con las prácticas actuales de gestión de archivos y monitoreo regular.")
    
    return recomendaciones

# --- Interfaz principal ---
st.title("🔍 Detalle Completo de Equipos V2")
st.markdown("### Análisis Avanzado con Explicaciones por Área y Recomendaciones Mejoradas")
st.markdown("Analiza el rendimiento detallado de cada equipo con explicaciones sustanciales, análisis por área y recomendaciones específicas.")

# --- Selector de equipo ---
all_equipos = sorted(set(df_cp['equipo']).union(set(df_hdd['equipo'])), key=lambda x: str(x))
equipo_sel = st.selectbox("Selecciona un equipo para análisis detallado:", all_equipos)

if equipo_sel:
    st.markdown("---")
    
    # --- Información del equipo ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📋 Información General")
        st.write(f"**Equipo:** {equipo_sel}")
        st.write(f"**Fecha de análisis:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        st.write(f"**Versión del análisis:** V2.0")
    
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
    
    # --- Análisis CP ---
    if not row_cp.empty:
        st.markdown("---")
        st.subheader("🖥️ Análisis Detallado - CP (Procesamiento)")
        
        col4, col5 = st.columns(2)
        
        with col4:
            st.metric("Score CP", f"{row_cp.iloc[0]['score_final']:.2f}/100")
            
            # Gráfico de radar mejorado para métricas CP
            if pd.notna(row_cp.iloc[0].get('cp_llenado_score')) and pd.notna(row_cp.iloc[0].get('cp_inestabilidad_score')) and pd.notna(row_cp.iloc[0].get('cp_tasa_cambio_score')):
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=[row_cp.iloc[0]['cp_llenado_score'], row_cp.iloc[0]['cp_inestabilidad_score'], row_cp.iloc[0]['cp_tasa_cambio_score']],
                    theta=['Ocupación', 'Estabilidad', 'Cambios'],
                    fill='toself',
                    name='Métricas CP',
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
                    title="Perfil de Métricas CP",
                    title_x=0.5,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col5:
            # Explicación detallada
            st.markdown("#### 📝 Explicación Detallada")
            explicacion_cp = generar_explicacion_detallada_cp(row_cp.iloc[0])
            st.markdown(explicacion_cp)
            
            # Recomendaciones mejoradas
            st.markdown("#### 💡 Recomendaciones Específicas")
            recomendaciones_cp = generar_recomendaciones_mejoradas_cp(row_cp.iloc[0])
            for i, rec in enumerate(recomendaciones_cp, 1):
                st.markdown(f"{i}. {rec}")
        
        # Información adicional CP
        st.markdown("#### 📊 Métricas Técnicas CP")
        col6, col7, col8 = st.columns(3)
        
        with col6:
            if pd.notna(row_cp.iloc[0].get('cp_llenado')):
                st.metric("Ocupación CP", f"{row_cp.iloc[0]['cp_llenado']:.2f}%")
                st.metric("Score Ocupación", f"{row_cp.iloc[0]['cp_llenado_score']:.1f}/100")
        
        with col7:
            if pd.notna(row_cp.iloc[0].get('cp_inestabilidad')):
                st.metric("Inestabilidad CP", f"{row_cp.iloc[0]['cp_inestabilidad']:.2f}")
                st.metric("Score Estabilidad", f"{row_cp.iloc[0]['cp_inestabilidad_score']:.1f}/100")
        
        with col8:
            if pd.notna(row_cp.iloc[0].get('cp_tasa_cambio')):
                st.metric("Tasa Cambio CP", f"{row_cp.iloc[0]['cp_tasa_cambio']:.2f}")
                st.metric("Score Cambios", f"{row_cp.iloc[0]['cp_tasa_cambio_score']:.1f}/100")
        
        # Áreas CP con explicaciones
        st.markdown("#### 🎯 Análisis por Áreas CP")
        explicaciones_areas = generar_explicacion_por_area_cp(row_cp.iloc[0])
        for explicacion in explicaciones_areas:
            st.markdown(explicacion)
    
    # --- Análisis HDD ---
    if not row_hdd.empty:
        st.markdown("---")
        st.subheader("💾 Análisis Detallado - HDD (Almacenamiento)")
        
        col9, col10 = st.columns(2)
        
        with col9:
            st.metric("Score HDD", f"{row_hdd.iloc[0]['score_final']:.2f}/100")
            
            # Gráfico de radar mejorado para métricas HDD
            if pd.notna(row_hdd.iloc[0].get('hdd_uso_score')) and pd.notna(row_hdd.iloc[0].get('hdd_inestabilidad_score')) and pd.notna(row_hdd.iloc[0].get('hdd_tasa_cambio_score')):
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=[row_hdd.iloc[0]['hdd_uso_score'], row_hdd.iloc[0]['hdd_inestabilidad_score'], row_hdd.iloc[0]['hdd_tasa_cambio_score']],
                    theta=['Uso', 'Estabilidad', 'Cambios'],
                    fill='toself',
                    name='Métricas HDD',
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
                    title="Perfil de Métricas HDD",
                    title_x=0.5,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col10:
            # Explicación detallada
            st.markdown("#### 📝 Explicación Detallada")
            explicacion_hdd = generar_explicacion_detallada_hdd(row_hdd.iloc[0])
            st.markdown(explicacion_hdd)
            
            # Recomendaciones mejoradas
            st.markdown("#### 💡 Recomendaciones Específicas")
            recomendaciones_hdd = generar_recomendaciones_mejoradas_hdd(row_hdd.iloc[0])
            for i, rec in enumerate(recomendaciones_hdd, 1):
                st.markdown(f"{i}. {rec}")
        
        # Información adicional HDD
        st.markdown("#### 📊 Métricas Técnicas HDD")
        col11, col12, col13 = st.columns(3)
        
        with col11:
            if pd.notna(row_hdd.iloc[0].get('hdd_uso')):
                st.metric("Uso HDD", f"{row_hdd.iloc[0]['hdd_uso']:.2f}%")
                st.metric("Score Uso", f"{row_hdd.iloc[0]['hdd_uso_score']:.1f}/100")
        
        with col12:
            if pd.notna(row_hdd.iloc[0].get('hdd_inestabilidad')):
                st.metric("Inestabilidad HDD", f"{row_hdd.iloc[0]['hdd_inestabilidad']:.2f}")
                st.metric("Score Estabilidad", f"{row_hdd.iloc[0]['hdd_inestabilidad_score']:.1f}/100")
        
        with col13:
            if pd.notna(row_hdd.iloc[0].get('hdd_tasa_cambio')):
                st.metric("Tasa Cambio HDD", f"{row_hdd.iloc[0]['hdd_tasa_cambio']:.2f}")
                st.metric("Score Cambios", f"{row_hdd.iloc[0]['hdd_tasa_cambio_score']:.1f}/100")
        
        # Unidades HDD
        unidades_hdd = row_hdd.iloc[0].get('unidades_hdd', [])
        if unidades_hdd:
            st.markdown(f"**💽 Unidades HDD monitoreadas:** {', '.join(unidades_hdd)}")
    
    # --- Resumen ejecutivo mejorado ---
    if not row_cp.empty or not row_hdd.empty:
        st.markdown("---")
        st.subheader("📋 Resumen Ejecutivo V2")
        
        if not row_cp.empty and not row_hdd.empty:
            score_cp = row_cp.iloc[0]['score_final']
            score_hdd = row_hdd.iloc[0]['score_final']
            score_promedio = (score_cp + score_hdd) / 2
            
            col14, col15, col16 = st.columns(3)
            
            with col14:
                st.metric("Score CP", f"{score_cp:.2f}/100")
            with col15:
                st.metric("Score HDD", f"{score_hdd:.2f}/100")
            with col16:
                st.metric("Score Promedio General", f"{score_promedio:.2f}/100")
            
            # Evaluación general mejorada
            if score_promedio >= 80:
                st.success("🎉 **Excelente rendimiento general**. El equipo está funcionando de manera óptima en ambas dimensiones. Mantener las prácticas actuales y continuar con el monitoreo regular.")
            elif score_promedio >= 60:
                st.info("👍 **Buen rendimiento general**. El equipo funciona bien con algunas oportunidades de mejora. Implementar las recomendaciones específicas para optimizar el rendimiento.")
            elif score_promedio >= 40:
                st.warning("⚠️ **Rendimiento regular**. Se recomienda revisar y optimizar varios aspectos del equipo. Priorizar las recomendaciones más críticas.")
            else:
                st.error("🚨 **Rendimiento bajo**. Se requiere atención inmediata y plan de mejora. Implementar todas las recomendaciones de forma prioritaria.")
            
            # Análisis de balance
            diferencia = abs(score_cp - score_hdd)
            if diferencia < 10:
                st.info("⚖️ **Equilibrio**: El equipo tiene un rendimiento equilibrado entre procesamiento y almacenamiento.")
            elif score_cp > score_hdd:
                st.info("⚡ **Fuerte en CP**: El equipo destaca más en procesamiento que en almacenamiento.")
            else:
                st.info("💾 **Fuerte en HDD**: El equipo destaca más en almacenamiento que en procesamiento.")
        
        elif not row_cp.empty:
            st.info("📊 Solo se tienen datos de CP para este equipo. El análisis de almacenamiento no está disponible.")
        elif not row_hdd.empty:
            st.info("📊 Solo se tienen datos de HDD para este equipo. El análisis de procesamiento no está disponible.")

st.markdown("---")
st.caption("Desarrollado por InfoDesign Colombia | Análisis Detallado de Equipos V2.0 | 2024") 