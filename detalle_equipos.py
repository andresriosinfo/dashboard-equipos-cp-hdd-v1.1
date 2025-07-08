import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Detalle de Equipos - CP & HDD", layout="wide", page_icon="🔍")

# --- Cargar datos ---
@st.cache_data
def load_data():
    df_cp = pd.read_csv('ranking_cp.csv')
    df_hdd = pd.read_csv('ranking_hdd.csv')
    return df_cp, df_hdd

df_cp, df_hdd = load_data()

# --- Funciones para explicaciones humanas ---
def generar_explicacion_humana_cp(row):
    """Genera una explicación más humana y sustancial para CP"""
    explicacion = []
    
    if pd.notna(row['cp_llenado']):
        llenado_score = row['cp_llenado_score']
        llenado_valor = row['cp_llenado']
        
        if llenado_score >= 80:
            explicacion.append(f"**Ocupación CP Excelente ({llenado_score:.1f}pts)**: El equipo mantiene una ocupación del {llenado_valor:.1f}%, lo que indica un uso eficiente de los recursos de procesamiento. Esto significa que el equipo está aprovechando bien su capacidad de CPU.")
        elif llenado_score >= 60:
            explicacion.append(f"**Ocupación CP Buena ({llenado_score:.1f}pts)**: Con una ocupación del {llenado_valor:.1f}%, el equipo tiene un rendimiento aceptable en el uso de CPU, aunque hay margen para optimización.")
        elif llenado_score >= 40:
            explicacion.append(f"**Ocupación CP Regular ({llenado_score:.1f}pts)**: La ocupación del {llenado_valor:.1f}% sugiere que el equipo podría estar subutilizando sus recursos de procesamiento.")
        else:
            explicacion.append(f"**Ocupación CP Baja ({llenado_score:.1f}pts)**: Con solo {llenado_valor:.1f}% de ocupación, el equipo está significativamente subutilizado, lo que puede indicar problemas de configuración o carga de trabajo insuficiente.")
    
    if pd.notna(row['cp_inestabilidad']):
        inestabilidad_score = row['cp_inestabilidad_score']
        inestabilidad_valor = row['cp_inestabilidad']
        
        if inestabilidad_score >= 80:
            explicacion.append(f"**Estabilidad CP Excelente ({inestabilidad_score:.1f}pts)**: El equipo muestra una variabilidad muy baja ({inestabilidad_valor:.1f}), indicando un rendimiento consistente y predecible en el tiempo.")
        elif inestabilidad_score >= 60:
            explicacion.append(f"**Estabilidad CP Buena ({inestabilidad_score:.1f}pts)**: Con una variabilidad de {inestabilidad_valor:.1f}, el equipo mantiene un rendimiento relativamente estable.")
        elif inestabilidad_score >= 40:
            explicacion.append(f"**Estabilidad CP Regular ({inestabilidad_score:.1f}pts)**: La variabilidad de {inestabilidad_valor:.1f} sugiere fluctuaciones moderadas en el rendimiento que podrían afectar la consistencia.")
        else:
            explicacion.append(f"**Estabilidad CP Baja ({inestabilidad_score:.1f}pts)**: La alta variabilidad de {inestabilidad_valor:.1f} indica inestabilidad significativa en el rendimiento, lo que puede causar problemas de confiabilidad.")
    
    if pd.notna(row['cp_tasa_cambio']):
        cambio_score = row['cp_tasa_cambio_score']
        cambio_valor = row['cp_tasa_cambio']
        
        if cambio_score >= 80:
            explicacion.append(f"**Cambios CP Estables ({cambio_score:.1f}pts)**: Los cambios en el rendimiento son muy predecibles ({cambio_valor:.1f}), lo que facilita la planificación y gestión de recursos.")
        elif cambio_score >= 60:
            explicacion.append(f"**Cambios CP Controlados ({cambio_score:.1f}pts)**: Con una tasa de cambio de {cambio_valor:.1f}, los cambios son manejables y no representan un riesgo significativo.")
        elif cambio_score >= 40:
            explicacion.append(f"**Cambios CP Variables ({cambio_score:.1f}pts)**: La tasa de cambio de {cambio_valor:.1f} indica fluctuaciones que requieren monitoreo más frecuente.")
        else:
            explicacion.append(f"**Cambios CP Inestables ({cambio_score:.1f}pts)**: La alta tasa de cambio de {cambio_valor:.1f} sugiere cambios bruscos e impredecibles que pueden afectar la estabilidad del sistema.")
    
    return " ".join(explicacion)

def generar_explicacion_humana_hdd(row):
    """Genera una explicación más humana y sustancial para HDD"""
    explicacion = []
    
    if pd.notna(row['hdd_uso']):
        uso_score = row['hdd_uso_score']
        uso_valor = row['hdd_uso']
        
        if uso_score >= 80:
            explicacion.append(f"**Uso HDD Excelente ({uso_score:.1f}pts)**: Con un uso del {uso_valor:.1f}%, el equipo mantiene un balance óptimo entre utilización y espacio libre, asegurando buen rendimiento sin riesgo de saturación.")
        elif uso_score >= 60:
            explicacion.append(f"**Uso HDD Bueno ({uso_score:.1f}pts)**: El uso del {uso_valor:.1f}% está dentro de parámetros aceptables, aunque hay oportunidad para optimizar el almacenamiento.")
        elif uso_score >= 40:
            explicacion.append(f"**Uso HDD Regular ({uso_score:.1f}pts)**: Con {uso_valor:.1f}% de uso, el equipo podría estar subutilizando su capacidad de almacenamiento o tener problemas de gestión de archivos.")
        else:
            explicacion.append(f"**Uso HDD Bajo ({uso_score:.1f}pts)**: El uso de solo {uso_valor:.1f}% indica subutilización significativa del almacenamiento, posiblemente por falta de datos o configuración inadecuada.")
    
    if pd.notna(row['hdd_inestabilidad']):
        inestabilidad_score = row['hdd_inestabilidad_score']
        inestabilidad_valor = row['hdd_inestabilidad']
        
        if inestabilidad_score >= 80:
            explicacion.append(f"**Estabilidad HDD Excelente ({inestabilidad_score:.1f}pts)**: La variabilidad de {inestabilidad_valor:.1f} indica un rendimiento de disco muy consistente, lo que es ideal para operaciones confiables.")
        elif inestabilidad_score >= 60:
            explicacion.append(f"**Estabilidad HDD Buena ({inestabilidad_score:.1f}pts)**: Con variabilidad de {inestabilidad_valor:.1f}, el disco mantiene un rendimiento relativamente estable.")
        elif inestabilidad_score >= 40:
            explicacion.append(f"**Estabilidad HDD Regular ({inestabilidad_score:.1f}pts)**: La variabilidad de {inestabilidad_valor:.1f} sugiere fluctuaciones que pueden afectar la velocidad de acceso a datos.")
        else:
            explicacion.append(f"**Estabilidad HDD Baja ({inestabilidad_score:.1f}pts)**: La alta variabilidad de {inestabilidad_valor:.1f} indica problemas de rendimiento del disco que pueden causar lentitud y errores.")
    
    if pd.notna(row['hdd_tasa_cambio']):
        cambio_score = row['hdd_tasa_cambio_score']
        cambio_valor = row['hdd_tasa_cambio']
        
        if cambio_score >= 80:
            explicacion.append(f"**Cambios HDD Estables ({cambio_score:.1f}pts)**: Los cambios en el uso del disco son predecibles ({cambio_valor:.1f}), facilitando la gestión de almacenamiento.")
        elif cambio_score >= 60:
            explicacion.append(f"**Cambios HDD Controlados ({cambio_score:.1f}pts)**: Con tasa de cambio de {cambio_valor:.1f}, los cambios son manejables y no representan riesgo.")
        elif cambio_score >= 40:
            explicacion.append(f"**Cambios HDD Variables ({cambio_score:.1f}pts)**: La tasa de cambio de {cambio_valor:.1f} requiere monitoreo más frecuente del almacenamiento.")
        else:
            explicacion.append(f"**Cambios HDD Inestables ({cambio_score:.1f}pts)**: La alta tasa de cambio de {cambio_valor:.1f} indica cambios bruscos que pueden causar problemas de almacenamiento.")
    
    return " ".join(explicacion)

def generar_recomendaciones_humanas_cp(row):
    """Genera recomendaciones más humanas para CP"""
    recomendaciones = []
    
    if pd.notna(row['cp_llenado']) and row['cp_llenado_score'] < 50:
        recomendaciones.append("🔧 **Optimizar carga de trabajo**: Considerar redistribuir tareas o aumentar la carga de procesamiento para aprovechar mejor los recursos de CPU.")
    
    if pd.notna(row['cp_inestabilidad']) and row['cp_inestabilidad_score'] < 50:
        recomendaciones.append("📊 **Monitorear procesos**: Identificar y resolver procesos que causen picos de CPU para estabilizar el rendimiento.")
    
    if pd.notna(row['cp_tasa_cambio']) and row['cp_tasa_cambio_score'] < 50:
        recomendaciones.append("⚙️ **Revisar configuración**: Evaluar configuraciones de procesos y servicios para reducir cambios bruscos en el uso de CPU.")
    
    if not recomendaciones:
        recomendaciones.append("✅ **Mantener rendimiento actual**: El equipo está funcionando de manera óptima. Continuar con las prácticas actuales.")
    
    return recomendaciones

def generar_recomendaciones_humanas_hdd(row):
    """Genera recomendaciones más humanas para HDD"""
    recomendaciones = []
    
    if pd.notna(row['hdd_uso']) and row['hdd_uso_score'] < 50:
        recomendaciones.append("💾 **Optimizar almacenamiento**: Revisar archivos temporales, logs antiguos y datos no utilizados para liberar espacio.")
    
    if pd.notna(row['hdd_inestabilidad']) and row['hdd_inestabilidad_score'] < 50:
        recomendaciones.append("🔍 **Diagnosticar disco**: Verificar la salud del disco duro y considerar defragmentación o reemplazo si es necesario.")
    
    if pd.notna(row['hdd_tasa_cambio']) and row['hdd_tasa_cambio_score'] < 50:
        recomendaciones.append("📈 **Monitorear crecimiento**: Implementar alertas para detectar cambios bruscos en el uso de almacenamiento.")
    
    if not recomendaciones:
        recomendaciones.append("✅ **Mantener rendimiento actual**: El almacenamiento está funcionando de manera óptima. Continuar con las prácticas actuales.")
    
    return recomendaciones

# --- Interfaz principal ---
st.title("🔍 Detalle Completo de Equipos")
st.markdown("Analiza el rendimiento detallado de cada equipo con explicaciones sustanciales y recomendaciones específicas.")

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
            st.write(f"**CP:** {row_cp.iloc[0]['categoria']}")
        else:
            st.write("**CP:** Sin datos")
            
        if not row_hdd.empty:
            st.write(f"**HDD:** {row_hdd.iloc[0]['categoria']}")
        else:
            st.write("**HDD:** Sin datos")
    
    # --- Análisis CP ---
    if not row_cp.empty:
        st.markdown("---")
        st.subheader("🖥️ Análisis Detallado - CP (Procesamiento)")
        
        col4, col5 = st.columns(2)
        
        with col4:
            st.metric("Score CP", f"{row_cp.iloc[0]['score_final']:.2f}/100")
            
            # Gráfico de radar para métricas CP
            if pd.notna(row_cp.iloc[0]['cp_llenado']) and pd.notna(row_cp.iloc[0]['cp_inestabilidad']) and pd.notna(row_cp.iloc[0]['cp_tasa_cambio']):
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=[row_cp.iloc[0]['cp_llenado_score'], row_cp.iloc[0]['cp_inestabilidad_score'], row_cp.iloc[0]['cp_tasa_cambio_score']],
                    theta=['Ocupación', 'Estabilidad', 'Cambios'],
                    fill='toself',
                    name='Métricas CP'
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=False,
                    title="Perfil de Métricas CP"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col5:
            # Explicación humana
            st.markdown("#### 📝 Explicación Detallada")
            explicacion_cp = generar_explicacion_humana_cp(row_cp.iloc[0])
            st.markdown(explicacion_cp)
            
            # Recomendaciones
            st.markdown("#### 💡 Recomendaciones")
            recomendaciones_cp = generar_recomendaciones_humanas_cp(row_cp.iloc[0])
            for rec in recomendaciones_cp:
                st.markdown(rec)
        
        # Información adicional CP
        st.markdown("#### 📊 Métricas Técnicas CP")
        col6, col7, col8 = st.columns(3)
        
        with col6:
            if pd.notna(row_cp.iloc[0]['cp_llenado']):
                st.metric("Ocupación CP", f"{row_cp.iloc[0]['cp_llenado']:.2f}%")
                st.metric("Score Ocupación", f"{row_cp.iloc[0]['cp_llenado_score']:.1f}/100")
        
        with col7:
            if pd.notna(row_cp.iloc[0]['cp_inestabilidad']):
                st.metric("Inestabilidad CP", f"{row_cp.iloc[0]['cp_inestabilidad']:.2f}")
                st.metric("Score Estabilidad", f"{row_cp.iloc[0]['cp_inestabilidad_score']:.1f}/100")
        
        with col8:
            if pd.notna(row_cp.iloc[0]['cp_tasa_cambio']):
                st.metric("Tasa Cambio CP", f"{row_cp.iloc[0]['cp_tasa_cambio']:.2f}")
                st.metric("Score Cambios", f"{row_cp.iloc[0]['cp_tasa_cambio_score']:.1f}/100")
        
        # Áreas CP
        areas_cp = row_cp.iloc[0]['areas_cp']
        if isinstance(areas_cp, str):
            try:
                areas_cp = eval(areas_cp)
            except:
                areas_cp = [areas_cp]
        st.markdown(f"**Áreas CP monitoreadas:** {', '.join(areas_cp) if areas_cp else 'N/A'}")
    
    # --- Análisis HDD ---
    if not row_hdd.empty:
        st.markdown("---")
        st.subheader("💾 Análisis Detallado - HDD (Almacenamiento)")
        
        col9, col10 = st.columns(2)
        
        with col9:
            st.metric("Score HDD", f"{row_hdd.iloc[0]['score_final']:.2f}/100")
            
            # Gráfico de radar para métricas HDD
            if pd.notna(row_hdd.iloc[0]['hdd_uso']) and pd.notna(row_hdd.iloc[0]['hdd_inestabilidad']) and pd.notna(row_hdd.iloc[0]['hdd_tasa_cambio']):
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=[row_hdd.iloc[0]['hdd_uso_score'], row_hdd.iloc[0]['hdd_inestabilidad_score'], row_hdd.iloc[0]['hdd_tasa_cambio_score']],
                    theta=['Uso', 'Estabilidad', 'Cambios'],
                    fill='toself',
                    name='Métricas HDD'
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=False,
                    title="Perfil de Métricas HDD"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col10:
            # Explicación humana
            st.markdown("#### 📝 Explicación Detallada")
            explicacion_hdd = generar_explicacion_humana_hdd(row_hdd.iloc[0])
            st.markdown(explicacion_hdd)
            
            # Recomendaciones
            st.markdown("#### 💡 Recomendaciones")
            recomendaciones_hdd = generar_recomendaciones_humanas_hdd(row_hdd.iloc[0])
            for rec in recomendaciones_hdd:
                st.markdown(rec)
        
        # Información adicional HDD
        st.markdown("#### 📊 Métricas Técnicas HDD")
        col11, col12, col13 = st.columns(3)
        
        with col11:
            if pd.notna(row_hdd.iloc[0]['hdd_uso']):
                st.metric("Uso HDD", f"{row_hdd.iloc[0]['hdd_uso']:.2f}%")
                st.metric("Score Uso", f"{row_hdd.iloc[0]['hdd_uso_score']:.1f}/100")
        
        with col12:
            if pd.notna(row_hdd.iloc[0]['hdd_inestabilidad']):
                st.metric("Inestabilidad HDD", f"{row_hdd.iloc[0]['hdd_inestabilidad']:.2f}")
                st.metric("Score Estabilidad", f"{row_hdd.iloc[0]['hdd_inestabilidad_score']:.1f}/100")
        
        with col13:
            if pd.notna(row_hdd.iloc[0]['hdd_tasa_cambio']):
                st.metric("Tasa Cambio HDD", f"{row_hdd.iloc[0]['hdd_tasa_cambio']:.2f}")
                st.metric("Score Cambios", f"{row_hdd.iloc[0]['hdd_tasa_cambio_score']:.1f}/100")
        
        # Unidades HDD
        unidades_hdd = row_hdd.iloc[0]['unidades_hdd']
        if isinstance(unidades_hdd, str):
            try:
                unidades_hdd = eval(unidades_hdd)
            except:
                unidades_hdd = [unidades_hdd]
        st.markdown(f"**Unidades HDD monitoreadas:** {', '.join(unidades_hdd) if unidades_hdd else 'N/A'}")
    
    # --- Resumen ejecutivo ---
    if not row_cp.empty or not row_hdd.empty:
        st.markdown("---")
        st.subheader("📋 Resumen Ejecutivo")
        
        if not row_cp.empty and not row_hdd.empty:
            score_cp = row_cp.iloc[0]['score_final']
            score_hdd = row_hdd.iloc[0]['score_final']
            score_promedio = (score_cp + score_hdd) / 2
            
            st.metric("Score Promedio General", f"{score_promedio:.2f}/100")
            
            if score_promedio >= 80:
                st.success("🎉 **Excelente rendimiento general**. El equipo está funcionando de manera óptima en ambas dimensiones.")
            elif score_promedio >= 60:
                st.info("👍 **Buen rendimiento general**. El equipo funciona bien con algunas oportunidades de mejora.")
            elif score_promedio >= 40:
                st.warning("⚠️ **Rendimiento regular**. Se recomienda revisar y optimizar varios aspectos del equipo.")
            else:
                st.error("🚨 **Rendimiento bajo**. Se requiere atención inmediata y plan de mejora.")
        
        elif not row_cp.empty:
            st.info("📊 Solo se tienen datos de CP para este equipo.")
        elif not row_hdd.empty:
            st.info("📊 Solo se tienen datos de HDD para este equipo.")

st.markdown("---")
st.caption("Desarrollado por InfoDesign Colombia | Análisis Detallado de Equipos | 2024") 