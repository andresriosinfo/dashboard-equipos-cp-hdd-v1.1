import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Computer Units Dashboard - CP & HDD", layout="wide", page_icon="📊")

# --- Load data ---
@st.cache_data
def load_data():
    df_cp = pd.read_csv('ranking_cp.csv')
    df_hdd = pd.read_csv('ranking_hdd.csv')
    return df_cp, df_hdd

def translate_category(category):
    """Translate Spanish categories to English"""
    translations = {
        'Excelente': 'Excellent',
        'Muy Bueno': 'Very Good',
        'Bueno': 'Good',
        'Regular': 'Regular',
        'Necesita Mejora': 'Needs Improvement'
    }
    return translations.get(category, category)

df_cp, df_hdd = load_data()

# --- Styles ---
st.markdown("""
    <style>
    .main {background-color: #f7f9fa;}
    .stApp {font-family: 'Segoe UI', Arial, sans-serif;}
    .metric {font-size: 1.2em;}
    .st-bb {background: #e3eaf2; border-radius: 10px; padding: 1em;}
    </style>
""", unsafe_allow_html=True)

# --- Global Dashboard ---
st.title("Computer Units Dashboard - CP & HDD")
st.markdown("""
Visualize the global and detailed performance of computer units according to their CP and HDD metrics. 
Use the search tool to see the details of each unit.
""")

col1, col2 = st.columns(2)

with col1:
    st.header("Global CP Overview")
    st.metric("Units Analyzed", len(df_cp))
    st.metric("Maximum Score", f"{df_cp['score_final'].max():.2f}")
    st.metric("Average Score", f"{df_cp['score_final'].mean():.2f}")
    st.metric("Minimum Score", f"{df_cp['score_final'].min():.2f}")
    st.metric("Median", f"{df_cp['score_final'].median():.2f}")
    st.metric("Standard Deviation", f"{df_cp['score_final'].std():.2f}")
    st.markdown("#### CP Categories Distribution")
    # Create a copy and translate categories
    df_cp_pie = df_cp.copy()
    df_cp_pie['categoria_en'] = df_cp_pie['categoria'].apply(translate_category)
    
    # Define color mapping from worst to best
    color_map = {
        'Needs Improvement': '#FF6B6B',  # Red (worst)
        'Regular': '#FFA500',            # Orange
        'Good': '#FFD700',               # Yellow
        'Very Good': '#90EE90',          # Light Green
        'Excellent': '#32CD32'           # Green (best)
    }
    
    fig_pie_cp = px.pie(df_cp_pie, names='categoria_en', title='CP Categories', 
                        color='categoria_en', color_discrete_map=color_map)
    st.plotly_chart(fig_pie_cp, use_container_width=True)
    
    st.markdown("#### CP Scores Histogram")
    # Create a copy and translate categories for histogram
    df_cp_hist = df_cp.copy()
    df_cp_hist['categoria_en'] = df_cp_hist['categoria'].apply(translate_category)
    
    fig_hist_cp = px.histogram(df_cp_hist, x='score_final', nbins=20, color='categoria_en', 
                               color_discrete_map=color_map, title='CP Scores Distribution')
    st.plotly_chart(fig_hist_cp, use_container_width=True)

with col2:
    st.header("Global HDD Overview")
    st.metric("Units Analyzed", len(df_hdd))
    st.metric("Maximum Score", f"{df_hdd['score_final'].max():.2f}")
    st.metric("Average Score", f"{df_hdd['score_final'].mean():.2f}")
    st.metric("Minimum Score", f"{df_hdd['score_final'].min():.2f}")
    st.metric("Median", f"{df_hdd['score_final'].median():.2f}")
    st.metric("Standard Deviation", f"{df_hdd['score_final'].std():.2f}")
    st.markdown("#### HDD Categories Distribution")
    # Create a copy and translate categories
    df_hdd_pie = df_hdd.copy()
    df_hdd_pie['categoria_en'] = df_hdd_pie['categoria'].apply(translate_category)
    
    # Use the same color mapping for consistency
    fig_pie_hdd = px.pie(df_hdd_pie, names='categoria_en', title='HDD Categories', 
                         color='categoria_en', color_discrete_map=color_map)
    st.plotly_chart(fig_pie_hdd, use_container_width=True)
    
    st.markdown("#### HDD Scores Histogram")
    # Create a copy and translate categories for histogram
    df_hdd_hist = df_hdd.copy()
    df_hdd_hist['categoria_en'] = df_hdd_hist['categoria'].apply(translate_category)
    
    fig_hist_hdd = px.histogram(df_hdd_hist, x='score_final', nbins=20, color='categoria_en', 
                                color_discrete_map=color_map, title='HDD Scores Distribution')
    st.plotly_chart(fig_hist_hdd, use_container_width=True)

# --- Visual comparison ---
st.markdown("---")
st.subheader("CP vs HDD Scores Comparison")

comp = pd.DataFrame({
    'CP': df_cp['score_final'],
    'HDD': df_hdd['score_final'].sample(n=len(df_cp), random_state=42) if len(df_hdd) > len(df_cp) else df_hdd['score_final']
})
st.plotly_chart(px.box(comp, points="all", title="CP vs HDD Scores Distribution", 
                       color_discrete_sequence=['#FF6B6B', '#4ECDC4']), use_container_width=True)

# --- Top and Bottom units ---
st.markdown("---")
st.subheader("Top and Worst Units")
col3, col4 = st.columns(2)
with col3:
    st.markdown("#### Top 5 CP")
    df_cp_top = df_cp[['posicion','equipo','score_final','categoria']].head(5).copy()
    df_cp_top.columns = ['Position', 'Unit', 'Score', 'Category']
    df_cp_top['Category'] = df_cp_top['Category'].apply(translate_category)
    st.dataframe(df_cp_top, use_container_width=True, hide_index=True)
    st.markdown("#### Worst 5 CP")
    df_cp_worst = df_cp[['posicion','equipo','score_final','categoria']].tail(5).copy()
    df_cp_worst.columns = ['Position', 'Unit', 'Score', 'Category']
    df_cp_worst['Category'] = df_cp_worst['Category'].apply(translate_category)
    st.dataframe(df_cp_worst, use_container_width=True, hide_index=True)
with col4:
    st.markdown("#### Top 5 HDD")
    df_hdd_top = df_hdd[['posicion','equipo','score_final','categoria']].head(5).copy()
    df_hdd_top.columns = ['Position', 'Unit', 'Score', 'Category']
    df_hdd_top['Category'] = df_hdd_top['Category'].apply(translate_category)
    st.dataframe(df_hdd_top, use_container_width=True, hide_index=True)
    st.markdown("#### Worst 5 HDD")
    df_hdd_worst = df_hdd[['posicion','equipo','score_final','categoria']].tail(5).copy()
    df_hdd_worst.columns = ['Position', 'Unit', 'Score', 'Category']
    df_hdd_worst['Category'] = df_hdd_worst['Category'].apply(translate_category)
    st.dataframe(df_hdd_worst, use_container_width=True, hide_index=True)

# --- Unit Detail ---
st.markdown("---")
st.header("Unit Detail")

# Join all possible units
all_units = sorted(set(df_cp['equipo']).union(set(df_hdd['equipo'])), key=lambda x: str(x))
unit_sel = st.selectbox("Select a unit to see details:", all_units)

col5, col6 = st.columns(2)
with col5:
    st.subheader("CP Detail")
    row_cp = df_cp[df_cp['equipo'] == unit_sel]
    if not row_cp.empty:
        st.metric("CP Score", f"{row_cp.iloc[0]['score_final']:.2f}", help="Global CP score")
        st.write(f"Category: **{translate_category(row_cp.iloc[0]['categoria'])}**")
        st.write(f"Explanation: {row_cp.iloc[0]['explicacion']}")
        st.write(f"Recommendations: {row_cp.iloc[0]['recomendaciones']}")
        cp_areas = row_cp.iloc[0]['areas_cp']
        if isinstance(cp_areas, str):
            # If it's a string, try to evaluate it as a list
            try:
                cp_areas = eval(cp_areas)
            except:
                cp_areas = [cp_areas]
        st.write(f"CP Areas: {', '.join(cp_areas) if cp_areas else 'N/A'}")
    else:
        st.info("This unit has no CP data.")
with col6:
    st.subheader("HDD Detail")
    row_hdd = df_hdd[df_hdd['equipo'] == unit_sel]
    if not row_hdd.empty:
        st.metric("HDD Score", f"{row_hdd.iloc[0]['score_final']:.2f}", help="Global HDD score")
        st.write(f"Category: **{translate_category(row_hdd.iloc[0]['categoria'])}**")
        st.write(f"Explanation: {row_hdd.iloc[0]['explicacion']}")
        st.write(f"Recommendations: {row_hdd.iloc[0]['recomendaciones']}")
        hdd_units = row_hdd.iloc[0]['unidades_hdd']
        if isinstance(hdd_units, str):
            # If it's a string, try to evaluate it as a list
            try:
                hdd_units = eval(hdd_units)
            except:
                hdd_units = [hdd_units]
        st.write(f"HDD Units: {', '.join(hdd_units) if hdd_units else 'N/A'}")
    else:
        st.info("This unit has no HDD data.")

st.markdown("---")
st.caption("Developed by InfoDesign Colombia | Streamlit Dashboard V1.1 | 2024") 