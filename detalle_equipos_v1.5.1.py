import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import ast

st.set_page_config(page_title="Team Analysis V1.5.1 - CP & HDD", layout="wide", page_icon="🔍")

# --- Load data ---
@st.cache_data
def load_data():
    df_cp = pd.read_csv('ranking_cp.csv')
    df_hdd = pd.read_csv('ranking_hdd.csv')
    
    # Convert list columns if they exist
    if 'areas_cp' in df_cp.columns:
        df_cp['areas_cp'] = df_cp['areas_cp'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    if 'unidades_hdd' in df_hdd.columns:
        df_hdd['unidades_hdd'] = df_hdd['unidades_hdd'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    
    return df_cp, df_hdd

df_cp, df_hdd = load_data()

# --- Functions for automatic CP area analysis ---
def analyze_cp_area_automatic(area, row):
    """Automatically analyzes what's happening in each specific CP area"""
    
    # Get metric values
    filling = row.get('cp_llenado', 0)
    instability = row.get('cp_inestabilidad', 0)
    change_rate = row.get('cp_tasa_cambio', 0)
    
    # Specific analysis by area
    if area == 'PP_NFD':
        if filling > 8000:
            return {
                'status': '🔴 CRITICAL',
                'problem': 'Node process overload',
                'explanation': f'The team has {filling:.0f} processes per node, indicating severe system overload. This can cause slowness and lockups.',
                'action': 'Immediately reduce process load or scale resources'
            }
        elif filling > 5000:
            return {
                'status': '🟡 WARNING',
                'problem': 'High process load',
                'explanation': f'With {filling:.0f} processes per node, the system is working at its capacity limit.',
                'action': 'Optimize processes and monitor performance'
            }
        else:
            return {
                'status': '🟢 NORMAL',
                'problem': 'Balanced process load',
                'explanation': f'The team handles {filling:.0f} processes per node efficiently.',
                'action': 'Maintain current configuration'
            }
    
    elif area == 'IOLOAD':
        if instability > 200:
            return {
                'status': '🔴 CRITICAL',
                'problem': 'Input/output bottlenecks',
                'explanation': f'The variability of {instability:.0f} indicates severe problems in disk operations that are affecting performance.',
                'action': 'Review disks, optimize queries and reduce I/O operations'
            }
        elif instability > 100:
            return {
                'status': '🟡 WARNING',
                'problem': 'I/O operation instability',
                'explanation': f'Input/output operations show variability of {instability:.0f}, which can cause slowness.',
                'action': 'Optimize disk access patterns'
            }
        else:
            return {
                'status': '🟢 NORMAL',
                'problem': 'Stable I/O operations',
                'explanation': f'Input/output operations are stable with variability of {instability:.0f}.',
                'action': 'Maintain current configuration'
            }
    
    elif area == 'totmem':
        if filling > 8000:
            return {
                'status': '🔴 CRITICAL',
                'problem': 'Excessive memory usage',
                'explanation': f'The team is using {filling:.0f}% memory, indicating possible RAM saturation.',
                'action': 'Free memory, close unnecessary applications or increase RAM'
            }
        elif filling > 5000:
            return {
                'status': '🟡 WARNING',
                'problem': 'High memory usage',
                'explanation': f'With {filling:.0f}% memory usage, the system is near its limit.',
                'action': 'Optimize memory usage and monitor applications'
            }
        else:
            return {
                'status': '🟢 NORMAL',
                'problem': 'Balanced memory usage',
                'explanation': f'The team uses {filling:.0f}% memory efficiently.',
                'action': 'Maintain current configuration'
            }
    
    elif area == 'CUMOVR':
        if change_rate > 20000:
            return {
                'status': '🔴 CRITICAL',
                'problem': 'Sharp changes in memory coverage',
                'explanation': f'The change rate of {change_rate:.0f} indicates extreme fluctuations in memory management.',
                'action': 'Review applications that consume memory irregularly'
            }
        elif change_rate > 10000:
            return {
                'status': '🟡 WARNING',
                'problem': 'Memory management instability',
                'explanation': f'Memory changes are variable ({change_rate:.0f}), which can affect performance.',
                'action': 'Optimize application memory management'
            }
        else:
            return {
                'status': '🟢 NORMAL',
                'problem': 'Stable memory management',
                'explanation': f'Memory management is stable with changes of {change_rate:.0f}.',
                'action': 'Maintain current configuration'
            }
    
    elif area == 'OMOVRN':
        if instability > 150:
            return {
                'status': '🔴 CRITICAL',
                'problem': 'Severe memory conflict between processes',
                'explanation': f'The variability of {instability:.0f} indicates serious conflicts between processes for memory.',
                'action': 'Review and optimize memory allocation between applications'
            }
        elif instability > 80:
            return {
                'status': '🟡 WARNING',
                'problem': 'Moderate memory conflict',
                'explanation': f'There are memory conflicts with variability of {instability:.0f}.',
                'action': 'Optimize memory distribution between processes'
            }
        else:
            return {
                'status': '🟢 NORMAL',
                'problem': 'Efficient memory management between processes',
                'explanation': f'Processes share memory efficiently with variability of {instability:.0f}.',
                'action': 'Maintain current configuration'
            }
    
    elif area == 'TLCONS':
        if filling > 7000:
            return {
                'status': '🔴 CRITICAL',
                'problem': 'Excessive CPU time consumption',
                'explanation': f'The team consumes {filling:.0f}% CPU time, indicating very demanding processes.',
                'action': 'Identify and optimize processes that consume too much CPU'
            }
        elif filling > 4000:
            return {
                'status': '🟡 WARNING',
                'problem': 'High CPU time consumption',
                'explanation': f'The consumption of {filling:.0f}% CPU is at the acceptable limit.',
                'action': 'Monitor processes and optimize the most demanding ones'
            }
        else:
            return {
                'status': '🟢 NORMAL',
                'problem': 'Balanced CPU consumption',
                'explanation': f'The team consumes {filling:.0f}% CPU efficiently.',
                'action': 'Maintain current configuration'
            }
    
    elif area == 'OMLDAV':
        if instability > 120:
            return {
                'status': '🔴 CRITICAL',
                'problem': 'Very unstable average load',
                'explanation': f'The average load varies {instability:.0f} points, indicating severe activity spikes.',
                'action': 'Stabilize workload and review critical processes'
            }
        elif instability > 60:
            return {
                'status': '🟡 WARNING',
                'problem': 'Variable average load',
                'explanation': f'The average load shows variability of {instability:.0f} points.',
                'action': 'Optimize workload distribution'
            }
        else:
            return {
                'status': '🟢 NORMAL',
                'problem': 'Stable average load',
                'explanation': f'The average load is stable with variability of {instability:.0f} points.',
                'action': 'Maintain current configuration'
            }
    
    elif area == 'CPLOAD':
        if filling > 7500:
            return {
                'status': '🔴 CRITICAL',
                'problem': 'CPU load at limit',
                'explanation': f'The CPU is at {filling:.0f}% capacity, which can cause general slowness.',
                'action': 'Reduce workload or scale CPU resources'
            }
        elif filling > 5000:
            return {
                'status': '🟡 WARNING',
                'problem': 'High CPU load',
                'explanation': f'The CPU is at {filling:.0f}% capacity, near the recommended limit.',
                'action': 'Optimize processes and monitor load'
            }
        else:
            return {
                'status': '🟢 NORMAL',
                'problem': 'Balanced CPU load',
                'explanation': f'The CPU operates at {filling:.0f}% capacity efficiently.',
                'action': 'Maintain current configuration'
            }
    
    elif area == 'MAXMEM':
        if change_rate > 15000:
            return {
                'status': '🔴 CRITICAL',
                'problem': 'Extreme changes in maximum memory usage',
                'explanation': f'Maximum memory usage changes {change_rate:.0f} points, indicating dangerous spikes.',
                'action': 'Review applications that consume memory irregularly'
            }
        elif change_rate > 8000:
            return {
                'status': '🟡 WARNING',
                'problem': 'Variable changes in maximum memory',
                'explanation': f'Maximum memory usage varies {change_rate:.0f} points.',
                'action': 'Optimize application memory management'
            }
        else:
            return {
                'status': '🟢 NORMAL',
                'problem': 'Stable maximum memory usage',
                'explanation': f'Maximum memory usage is stable with changes of {change_rate:.0f} points.',
                'action': 'Maintain current configuration'
            }
    
    else:
        return {
            'status': '⚪ NO DATA',
            'problem': 'Area not analyzed',
            'explanation': f'Not enough data to analyze area {area}.',
            'action': 'Collect more data from this area'
        }

def generate_simple_cp_recommendations(row):
    """Generates simple and direct recommendations for CP"""
    recommendations = []
    
    average_score = (row.get('cp_llenado_score', 0) + row.get('cp_inestabilidad_score', 0) + row.get('cp_tasa_cambio_score', 0)) / 3
    
    if average_score >= 80:
        recommendations.append("✅ **Everything is working well. Maintain current configuration.**")
    elif average_score >= 60:
        recommendations.append("⚠️ **There are some possible improvements. Review problematic areas.**")
    elif average_score >= 40:
        recommendations.append("🔴 **Important improvements needed. Implement suggested actions.**")
    else:
        recommendations.append("🚨 **Immediate attention required. Follow all critical recommendations.**")
    
    return recommendations

def generate_simple_hdd_recommendations(row):
    """Generates simple and direct recommendations for HDD"""
    recommendations = []
    
    hdd_score = row.get('score_final', 0)
    
    if hdd_score >= 80:
        recommendations.append("✅ **Storage is working very well. Maintain current practices.**")
    elif hdd_score >= 60:
        recommendations.append("⚠️ **Storage works well with some possible improvements.**")
    elif hdd_score >= 40:
        recommendations.append("🔴 **Storage needs optimization. Review file management.**")
    else:
        recommendations.append("🚨 **Storage requires urgent attention. Implement cleanup and optimization.**")
    
    return recommendations

def explain_cp_performance_profile(efficiency, stability, predictability):
    """Explains the CP performance profile with specific values"""
    explanation = []
    
    # Explain Efficiency
    if efficiency >= 80:
        explanation.append(f"**Efficiency: {efficiency:.0f}/100** - The team uses its resources very efficiently. It's maximizing its processing capacity.")
    elif efficiency >= 60:
        explanation.append(f"**Efficiency: {efficiency:.0f}/100** - The team uses its resources acceptably, though there's room for optimization.")
    elif efficiency >= 40:
        explanation.append(f"**Efficiency: {efficiency:.0f}/100** - The team could be underutilizing its resources or have configuration problems.")
    else:
        explanation.append(f"**Efficiency: {efficiency:.0f}/100** - The team is significantly underutilized or has serious configuration problems.")
    
    # Explain Stability
    if stability >= 80:
        explanation.append(f"**Stability: {stability:.0f}/100** - Performance is very consistent and predictable. The team operates stably.")
    elif stability >= 60:
        explanation.append(f"**Stability: {stability:.0f}/100** - Performance is relatively stable, with some minor fluctuations.")
    elif stability >= 40:
        explanation.append(f"**Stability: {stability:.0f}/100** - Performance shows variability that can affect consistency.")
    else:
        explanation.append(f"**Stability: {stability:.0f}/100** - Performance is very unstable, which can cause reliability problems.")
    
    # Explain Predictability
    if predictability >= 80:
        explanation.append(f"**Predictability: {predictability:.0f}/100** - Changes in performance are very predictable, facilitating planning.")
    elif predictability >= 60:
        explanation.append(f"**Predictability: {predictability:.0f}/100** - Changes are manageable and don't represent significant risk.")
    elif predictability >= 40:
        explanation.append(f"**Predictability: {predictability:.0f}/100** - Changes are variable and require more frequent monitoring.")
    else:
        explanation.append(f"**Predictability: {predictability:.0f}/100** - Changes are very unpredictable, which can affect system stability.")
    
    # General explanation
    average_score = (efficiency + stability + predictability) / 3
    if average_score >= 80:
        explanation.append("**Overall:** The team has an excellent performance profile, with high efficiency, stability and predictability.")
    elif average_score >= 60:
        explanation.append("**Overall:** The team has a good performance profile, with some improvement opportunities.")
    elif average_score >= 40:
        explanation.append("**Overall:** The team has a regular performance profile that requires optimization in several areas.")
    else:
        explanation.append("**Overall:** The team has a low performance profile that requires immediate attention and significant improvements.")
    
    return explanation

def explain_hdd_performance_profile(efficient_use, stability, controlled_changes):
    """Explains the HDD performance profile with specific values"""
    explanation = []
    
    # Explain Efficient Use
    if efficient_use >= 80:
        explanation.append(f"**Efficient Use: {efficient_use:.0f}/100** - The team manages its storage space very efficiently, maintaining optimal balance.")
    elif efficient_use >= 60:
        explanation.append(f"**Efficient Use: {efficient_use:.0f}/100** - The team manages its storage acceptably, with some optimization opportunities.")
    elif efficient_use >= 40:
        explanation.append(f"**Efficient Use: {efficient_use:.0f}/100** - The team could be underutilizing its storage or have file management problems.")
    else:
        explanation.append(f"**Efficient Use: {efficient_use:.0f}/100** - The team is significantly underutilizing its storage or has serious management problems.")
    
    # Explain Stability
    if stability >= 80:
        explanation.append(f"**Stability: {stability:.0f}/100** - Disk performance is very consistent and reliable.")
    elif stability >= 60:
        explanation.append(f"**Stability: {stability:.0f}/100** - Disk performance is relatively stable, with some minor fluctuations.")
    elif stability >= 40:
        explanation.append(f"**Stability: {stability:.0f}/100** - Disk performance shows variability that can affect access speed.")
    else:
        explanation.append(f"**Stability: {stability:.0f}/100** - Disk performance is very unstable, which can cause slowness and errors.")
    
    # Explain Controlled Changes
    if controlled_changes >= 80:
        explanation.append(f"**Controlled Changes: {controlled_changes:.0f}/100** - Changes in disk usage are very predictable, facilitating storage management.")
    elif controlled_changes >= 60:
        explanation.append(f"**Controlled Changes: {controlled_changes:.0f}/100** - Changes in storage are manageable and don't represent significant risk.")
    elif controlled_changes >= 40:
        explanation.append(f"**Controlled Changes: {controlled_changes:.0f}/100** - Changes in storage are variable and require more frequent monitoring.")
    else:
        explanation.append(f"**Controlled Changes: {controlled_changes:.0f}/100** - Changes in storage are very unpredictable, which can cause management problems.")
    
    # General explanation
    average_score = (efficient_use + stability + controlled_changes) / 3
    if average_score >= 80:
        explanation.append("**Overall:** The team has an excellent storage profile, with efficient management, stability and controlled changes.")
    elif average_score >= 60:
        explanation.append("**Overall:** The team has a good storage profile, with some improvement opportunities.")
    elif average_score >= 40:
        explanation.append("**Overall:** The team has a regular storage profile that requires optimization in several areas.")
    else:
        explanation.append("**Overall:** The team has a low storage profile that requires immediate attention and significant improvements.")
    
    return explanation

# --- Main interface ---
st.title("🔍 Team Analysis")
st.markdown("### Automatic Performance Evaluation System")

# --- Team selector ---
all_teams = sorted(set(df_cp['equipo']).union(set(df_hdd['equipo'])), key=lambda x: str(x))
team_sel = st.selectbox("Select a team:", all_teams)

if team_sel:
    st.markdown("---")
    
    # --- GENERAL INFORMATION AND SCORES ---
    st.subheader("📊 General Information")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Team", team_sel)
    
    with col2:
        st.metric("Analysis Date", datetime.now().strftime('%d/%m/%Y'))
    
    with col3:
        # CP Score
        row_cp = df_cp[df_cp['equipo'] == team_sel]
        if not row_cp.empty:
            score_cp = row_cp.iloc[0]['score_final']
            st.metric("CP Score", f"{score_cp:.1f}/100")
        else:
            st.metric("CP Score", "N/A")
    
    with col4:
        # HDD Score
        row_hdd = df_hdd[df_hdd['equipo'] == team_sel]
        if not row_hdd.empty:
            score_hdd = row_hdd.iloc[0]['score_final']
            st.metric("HDD Score", f"{score_hdd:.1f}/100")
        else:
            st.metric("HDD Score", "N/A")
    
    # --- RANKINGS TABLE ---
    st.markdown("#### 📈 Ranking Position")
    
    # Create rankings table
    ranking_data = []
    
    if not row_cp.empty:
        ranking_data.append({
            'Type': 'CP (Processing)',
            'Position': f"#{row_cp.iloc[0]['posicion']} of {len(df_cp)}",
            'Score': f"{row_cp.iloc[0]['score_final']:.1f}/100",
            'Category': row_cp.iloc[0]['categoria']
        })
    
    if not row_hdd.empty:
        ranking_data.append({
            'Type': 'HDD (Storage)',
            'Position': f"#{row_hdd.iloc[0]['posicion']} of {len(df_hdd)}",
            'Score': f"{row_hdd.iloc[0]['score_final']:.1f}/100",
            'Category': row_hdd.iloc[0]['categoria']
        })
    
    if ranking_data:
        df_ranking = pd.DataFrame(ranking_data)
        st.dataframe(df_ranking, use_container_width=True, hide_index=True)
    
    # --- SYSTEM RECOMMENDATIONS ---
    st.markdown("---")
    st.subheader("💡 System Recommendations")
    
    if not row_cp.empty:
        st.markdown("#### 🔧 Processing (CP)")
        cp_recommendations = generate_simple_cp_recommendations(row_cp.iloc[0])
        for rec in cp_recommendations:
            st.markdown(rec)
    
    if not row_hdd.empty:
        st.markdown("#### 💾 Storage (HDD)")
        hdd_recommendations = generate_simple_hdd_recommendations(row_hdd.iloc[0])
        for rec in hdd_recommendations:
            st.markdown(rec)
    
    # --- CP SCORE EXPLANATION ---
    if not row_cp.empty:
        st.markdown("---")
        st.subheader("🖥️ Score Explanation - Processing (CP)")
        
        # Performance profile
        st.markdown("#### 📊 Performance Profile")
        
        col5, col6 = st.columns(2)
        
        with col5:
            # Radar chart
            if pd.notna(row_cp.iloc[0].get('cp_llenado_score')) and pd.notna(row_cp.iloc[0].get('cp_inestabilidad_score')) and pd.notna(row_cp.iloc[0].get('cp_tasa_cambio_score')):
                efficiency = row_cp.iloc[0]['cp_llenado_score']
                stability = row_cp.iloc[0]['cp_inestabilidad_score']
                predictability = row_cp.iloc[0]['cp_tasa_cambio_score']
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=[efficiency, stability, predictability],
                    theta=['Efficiency', 'Stability', 'Predictability'],
                    fill='toself',
                    name='CP Performance',
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
                    title="CP Performance Profile",
                    title_x=0.5,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col6:
            # Detailed profile explanation
            if pd.notna(row_cp.iloc[0].get('cp_llenado_score')) and pd.notna(row_cp.iloc[0].get('cp_inestabilidad_score')) and pd.notna(row_cp.iloc[0].get('cp_tasa_cambio_score')):
                efficiency = row_cp.iloc[0]['cp_llenado_score']
                stability = row_cp.iloc[0]['cp_inestabilidad_score']
                predictability = row_cp.iloc[0]['cp_tasa_cambio_score']
                
                explanations = explain_cp_performance_profile(efficiency, stability, predictability)
                
                for explanation in explanations:
                    st.markdown(explanation)
                    st.markdown("")
            
            # General CP score
            score_cp = row_cp.iloc[0]['score_final']
            st.metric("General CP Score", f"{score_cp:.1f}/100")
            
            if score_cp >= 80:
                st.success("🎉 **Excellent performance**")
            elif score_cp >= 60:
                st.info("👍 **Good performance**")
            elif score_cp >= 40:
                st.warning("⚠️ **Regular performance**")
            else:
                st.error("🚨 **Low performance**")
        
        # Score explanation by area
        st.markdown("#### 🔍 Area Analysis")
        cp_areas = row_cp.iloc[0].get('areas_cp', [])
        if isinstance(cp_areas, str):
            try:
                cp_areas = ast.literal_eval(cp_areas)
            except:
                cp_areas = [cp_areas]
        
        if cp_areas:
            for area in cp_areas:
                analysis = analyze_cp_area_automatic(area, row_cp.iloc[0])
                
                with st.expander(f"{analysis['status']} {area}", expanded=True):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown(f"**Problem detected:** {analysis['problem']}")
                        st.markdown(f"**Explanation:** {analysis['explanation']}")
                    
                    with col_b:
                        st.markdown(f"**Recommended action:** {analysis['action']}")
                        
                        # Show relevant values
                        if area in ['PP_NFD', 'totmem', 'TLCONS', 'CPLOAD']:
                            value = row_cp.iloc[0].get('cp_llenado', 0)
                            st.metric(f"{area} Value", f"{value:.0f}")
                        elif area in ['IOLOAD', 'OMOVRN', 'OMLDAV']:
                            value = row_cp.iloc[0].get('cp_inestabilidad', 0)
                            st.metric(f"{area} Variability", f"{value:.0f}")
                        elif area in ['CUMOVR', 'MAXMEM']:
                            value = row_cp.iloc[0].get('cp_tasa_cambio', 0)
                            st.metric(f"{area} Changes", f"{value:.0f}")
    
    # --- HDD SCORE EXPLANATION ---
    if not row_hdd.empty:
        st.markdown("---")
        st.subheader("💾 Score Explanation - Storage (HDD)")
        
        col7, col8 = st.columns(2)
        
        with col7:
            # HDD radar chart
            if pd.notna(row_hdd.iloc[0].get('hdd_uso_score')) and pd.notna(row_hdd.iloc[0].get('hdd_inestabilidad_score')) and pd.notna(row_hdd.iloc[0].get('hdd_tasa_cambio_score')):
                efficient_use = row_hdd.iloc[0]['hdd_uso_score']
                stability = row_hdd.iloc[0]['hdd_inestabilidad_score']
                controlled_changes = row_hdd.iloc[0]['hdd_tasa_cambio_score']
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=[efficient_use, stability, controlled_changes],
                    theta=['Efficient Use', 'Stability', 'Controlled Changes'],
                    fill='toself',
                    name='HDD Performance',
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
                    title="HDD Performance Profile",
                    title_x=0.5,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col8:
            # Detailed HDD profile explanation
            if pd.notna(row_hdd.iloc[0].get('hdd_uso_score')) and pd.notna(row_hdd.iloc[0].get('hdd_inestabilidad_score')) and pd.notna(row_hdd.iloc[0].get('hdd_tasa_cambio_score')):
                efficient_use = row_hdd.iloc[0]['hdd_uso_score']
                stability = row_hdd.iloc[0]['hdd_inestabilidad_score']
                controlled_changes = row_hdd.iloc[0]['hdd_tasa_cambio_score']
                
                explanations = explain_hdd_performance_profile(efficient_use, stability, controlled_changes)
                
                for explanation in explanations:
                    st.markdown(explanation)
                    st.markdown("")
            
            # General HDD score
            score_hdd = row_hdd.iloc[0]['score_final']
            st.metric("General HDD Score", f"{score_hdd:.1f}/100")
            
            if score_hdd >= 80:
                st.success("🎉 **Excellent performance**")
            elif score_hdd >= 60:
                st.info("👍 **Good performance**")
            elif score_hdd >= 40:
                st.warning("⚠️ **Regular performance**")
            else:
                st.error("🚨 **Low performance**")
            
            # HDD Units
            hdd_units = row_hdd.iloc[0].get('unidades_hdd', [])
            if hdd_units:
                st.markdown(f"**💽 Monitored units:** {', '.join(hdd_units)}")

st.markdown("---")
st.caption("Developed by InfoDesign Colombia | Automatic Analysis V1.5.1 | 2024") 