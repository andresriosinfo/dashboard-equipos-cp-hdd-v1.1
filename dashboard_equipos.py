import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Dashboard de Equipos - CP & HDD", layout="wide", page_icon="📊")

# --- Cargar datos ---
@st.cache_data
def load_data():
    df_cp = pd.read_csv('ranking_cp.csv')
    df_hdd = pd.read_csv('ranking_hdd.csv')
    return df_cp, df_hdd

df_cp, df_hdd = load_data()

# --- Estilos ---
st.markdown("""
    <style>
    .main {background-color: #f7f9fa;}
    .stApp {font-family: 'Segoe UI', Arial, sans-serif;}
    .metric {font-size: 1.2em;}
    .st-bb {background: #e3eaf2; border-radius: 10px; padding: 1em;}
    </style>
""", unsafe_allow_html=True)

# --- Dashboard Global ---
st.title("Dashboard de Equipos - CP & HDD")
st.markdown("""
Visualiza el desempeño global y detallado de los equipos según sus métricas de CP y HDD. 
Utiliza el buscador para ver el detalle de cada equipo.
""")

col1, col2 = st.columns(2)

with col1:
    st.header("Visión Global CP")
    st.metric("Equipos Analizados", len(df_cp))
    st.metric("Score Máximo", f"{df_cp['score_final'].max():.2f}")
    st.metric("Score Promedio", f"{df_cp['score_final'].mean():.2f}")
    st.metric("Score Mínimo", f"{df_cp['score_final'].min():.2f}")
    st.metric("Mediana", f"{df_cp['score_final'].median():.2f}")
    st.metric("Desviación estándar", f"{df_cp['score_final'].std():.2f}")
    st.markdown("#### Distribución de Categorías CP")
    st.plotly_chart(px.pie(df_cp, names='categoria', title='Categorías CP', color_discrete_sequence=px.colors.sequential.Blues), use_container_width=True)
    st.markdown("#### Histograma de Puntajes CP")
    st.plotly_chart(px.histogram(df_cp, x='score_final', nbins=20, color='categoria', color_discrete_sequence=px.colors.sequential.Blues), use_container_width=True)

with col2:
    st.header("Visión Global HDD")
    st.metric("Equipos Analizados", len(df_hdd))
    st.metric("Score Máximo", f"{df_hdd['score_final'].max():.2f}")
    st.metric("Score Promedio", f"{df_hdd['score_final'].mean():.2f}")
    st.metric("Score Mínimo", f"{df_hdd['score_final'].min():.2f}")
    st.metric("Mediana", f"{df_hdd['score_final'].median():.2f}")
    st.metric("Desviación estándar", f"{df_hdd['score_final'].std():.2f}")
    st.markdown("#### Distribución de Categorías HDD")
    st.plotly_chart(px.pie(df_hdd, names='categoria', title='Categorías HDD', color_discrete_sequence=px.colors.sequential.Greens), use_container_width=True)
    st.markdown("#### Histograma de Puntajes HDD")
    st.plotly_chart(px.histogram(df_hdd, x='score_final', nbins=20, color='categoria', color_discrete_sequence=px.colors.sequential.Greens), use_container_width=True)

# --- Comparación visual ---
st.markdown("---")
st.subheader("Comparación de Puntajes CP vs HDD")

comp = pd.DataFrame({
    'CP': df_cp['score_final'],
    'HDD': df_hdd['score_final'].sample(n=len(df_cp), random_state=42) if len(df_hdd) > len(df_cp) else df_hdd['score_final']
})
st.plotly_chart(px.box(comp, points="all", title="Distribución de Puntajes CP vs HDD", 
                       color_discrete_sequence=['#FF6B6B', '#4ECDC4']), use_container_width=True)

# --- Top y Bottom equipos ---
st.markdown("---")
st.subheader("Top y Peores Equipos")
col3, col4 = st.columns(2)
with col3:
    st.markdown("#### Top 5 CP")
    st.dataframe(df_cp[['posicion','equipo','score_final','categoria']].head(5), use_container_width=True, hide_index=True)
    st.markdown("#### Peores 5 CP")
    st.dataframe(df_cp[['posicion','equipo','score_final','categoria']].tail(5), use_container_width=True, hide_index=True)
with col4:
    st.markdown("#### Top 5 HDD")
    st.dataframe(df_hdd[['posicion','equipo','score_final','categoria']].head(5), use_container_width=True, hide_index=True)
    st.markdown("#### Peores 5 HDD")
    st.dataframe(df_hdd[['posicion','equipo','score_final','categoria']].tail(5), use_container_width=True, hide_index=True)

# --- Detalle de Equipo ---
st.markdown("---")
st.header("Detalle de Equipo")

# Unir todos los equipos posibles
all_equipos = sorted(set(df_cp['equipo']).union(set(df_hdd['equipo'])), key=lambda x: str(x))
equipo_sel = st.selectbox("Selecciona un equipo para ver el detalle:", all_equipos)

col5, col6 = st.columns(2)
with col5:
    st.subheader("Detalle CP")
    row_cp = df_cp[df_cp['equipo'] == equipo_sel]
    if not row_cp.empty:
        st.metric("Score CP", f"{row_cp.iloc[0]['score_final']:.2f}", help="Puntaje global CP")
        st.write(f"Categoría: **{row_cp.iloc[0]['categoria']}**")
        st.write(f"Explicación: {row_cp.iloc[0]['explicacion']}")
        st.write(f"Recomendaciones: {row_cp.iloc[0]['recomendaciones']}")
        areas_cp = row_cp.iloc[0]['areas_cp']
        if isinstance(areas_cp, str):
            # Si es string, intentar evaluarlo como lista
            try:
                areas_cp = eval(areas_cp)
            except:
                areas_cp = [areas_cp]
        st.write(f"Áreas CP: {', '.join(areas_cp) if areas_cp else 'N/A'}")
    else:
        st.info("Este equipo no tiene datos CP.")
with col6:
    st.subheader("Detalle HDD")
    row_hdd = df_hdd[df_hdd['equipo'] == equipo_sel]
    if not row_hdd.empty:
        st.metric("Score HDD", f"{row_hdd.iloc[0]['score_final']:.2f}", help="Puntaje global HDD")
        st.write(f"Categoría: **{row_hdd.iloc[0]['categoria']}**")
        st.write(f"Explicación: {row_hdd.iloc[0]['explicacion']}")
        st.write(f"Recomendaciones: {row_hdd.iloc[0]['recomendaciones']}")
        unidades_hdd = row_hdd.iloc[0]['unidades_hdd']
        if isinstance(unidades_hdd, str):
            # Si es string, intentar evaluarlo como lista
            try:
                unidades_hdd = eval(unidades_hdd)
            except:
                unidades_hdd = [unidades_hdd]
        st.write(f"Unidades HDD: {', '.join(unidades_hdd) if unidades_hdd else 'N/A'}")
    else:
        st.info("Este equipo no tiene datos HDD.")

st.markdown("---")
st.caption("Desarrollado por InfoDesign Colombia | Streamlit Dashboard | 2024") 