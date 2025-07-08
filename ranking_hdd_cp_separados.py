#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ranking_hdd_cp_separados')

# --- Utilidades de percentil ---
def calculate_percentile_score(value, all_values, direction='higher_better'):
    if len(all_values) < 2 or pd.isna(value):
        return 50.0
    if direction == 'higher_better':
        pct = (np.sum(np.array(all_values) <= value) - 1) / (len(all_values) - 1)
    else:
        pct = (np.sum(np.array(all_values) >= value) - 1) / (len(all_values) - 1)
    return round(pct * 100, 2)

# --- Cargar y procesar datos CP ---
def get_cp_metrics():
    sys.path.append('cp_data_analysis_v2/src')
    from cp_upload_data_deploy import upload_data_sql
    logger.info('Cargando datos CP...')
    cp_data = upload_data_sql()
    equipos = {}
    for nombre_df, df in cp_data.items():
        if df.empty or not set(['equipo','fecha','valor','area']).issubset(df.columns):
            continue
        df = df.copy()
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
        df = df.dropna(subset=['fecha','valor'])
        if df.empty:
            continue
        fecha_max = df['fecha'].max()
        df = df[df['fecha'] >= fecha_max - timedelta(days=7)]
        if df.empty:
            continue
        for equipo in df['equipo'].unique():
            df_eq = df[df['equipo']==equipo]
            if len(df_eq) < 3:
                continue
            if equipo not in equipos:
                equipos[equipo] = {'llenado':[],'inestabilidad':[],'tasa_cambio':[],'areas':set(),'registros':0}
            valores = df_eq['valor'].tolist()
            equipos[equipo]['llenado'].append(np.mean(valores))
            equipos[equipo]['inestabilidad'].append(np.std(valores)*1000)
            # Tasa de cambio
            df_eq_sorted = df_eq.sort_values('fecha')
            tasas = []
            for i in range(1,len(df_eq_sorted)):
                v0 = df_eq_sorted.iloc[i-1]['valor']
                v1 = df_eq_sorted.iloc[i]['valor']
                if v0 != 0:
                    tasas.append(((v1-v0)/v0)*100)
            equipos[equipo]['tasa_cambio'].append(np.std(tasas)*10000 if tasas else 0)
            equipos[equipo]['areas'].add(df_eq['area'].iloc[0])
            equipos[equipo]['registros'] += len(df_eq)
    # Consolidar métricas promedio por equipo
    rows = []
    for eq, vals in equipos.items():
        rows.append({
            'equipo': eq,
            'cp_llenado': np.mean(vals['llenado']) if vals['llenado'] else np.nan,
            'cp_inestabilidad': np.mean(vals['inestabilidad']) if vals['inestabilidad'] else np.nan,
            'cp_tasa_cambio': np.mean(vals['tasa_cambio']) if vals['tasa_cambio'] else np.nan,
            'areas_cp': list(vals['areas']),
            'registros_cp': vals['registros']
        })
    return pd.DataFrame(rows)

# --- Cargar y procesar datos HDD ---
def get_hdd_metrics():
    sys.path.append('hdd_data_analysis_v2/src')
    from hdd_upload_data_deploy import upload_data_sql
    logger.info('Cargando datos HDD...')
    hdd_data = upload_data_sql()
    equipos = {}
    for nombre_df, df in hdd_data.items():
        if df.empty or not set(['equipo','fecha','uso','unidad']).issubset(df.columns):
            continue
        df = df.copy()
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        df['uso'] = pd.to_numeric(df['uso'], errors='coerce')
        df = df.dropna(subset=['fecha','uso'])
        if df.empty:
            continue
        fecha_max = df['fecha'].max()
        df = df[df['fecha'] >= fecha_max - timedelta(days=7)]
        if df.empty:
            continue
        for equipo in df['equipo'].unique():
            df_eq = df[df['equipo']==equipo]
            if len(df_eq) < 3:
                continue
            if equipo not in equipos:
                equipos[equipo] = {'uso':[],'inestabilidad':[],'tasa_cambio':[],'unidades':set(),'registros':0}
            valores = df_eq['uso'].tolist()
            equipos[equipo]['uso'].append(np.mean(valores)*100)
            equipos[equipo]['inestabilidad'].append(np.std(valores)*1000)
            # Tasa de cambio
            df_eq_sorted = df_eq.sort_values('fecha')
            tasas = []
            for i in range(1,len(df_eq_sorted)):
                v0 = df_eq_sorted.iloc[i-1]['uso']
                v1 = df_eq_sorted.iloc[i]['uso']
                if v0 != 0:
                    tasas.append(((v1-v0)/v0)*100)
            equipos[equipo]['tasa_cambio'].append(np.std(tasas)*10000 if tasas else 0)
            equipos[equipo]['unidades'].add(df_eq['unidad'].iloc[0])
            equipos[equipo]['registros'] += len(df_eq)
    # Consolidar métricas promedio por equipo
    rows = []
    for eq, vals in equipos.items():
        rows.append({
            'equipo': eq,
            'hdd_uso': np.mean(vals['uso']) if vals['uso'] else np.nan,
            'hdd_inestabilidad': np.mean(vals['inestabilidad']) if vals['inestabilidad'] else np.nan,
            'hdd_tasa_cambio': np.mean(vals['tasa_cambio']) if vals['tasa_cambio'] else np.nan,
            'unidades_hdd': list(vals['unidades']),
            'registros_hdd': vals['registros']
        })
    return pd.DataFrame(rows)

# --- Scoring y explicación ---
def score_and_explain(df, metric_configs, tipo):
    df = df.copy()
    # Calcular percentiles
    for metric, config in metric_configs.items():
        vals = df[metric].dropna()
        if len(vals) > 1:
            df[f'{metric}_score'] = [calculate_percentile_score(v, vals, config['direction']) if pd.notna(v) else 50.0 for v in df[metric]]
        else:
            df[f'{metric}_score'] = 50.0
    # Score final
    df['score_final'] = 0.0
    for metric, config in metric_configs.items():
        df['score_final'] += df[f'{metric}_score'] * config['weight']
    # Explicación y recomendaciones
    def categoria(score):
        if score >= 90: return 'Excelente'
        if score >= 75: return 'Muy Bueno'
        if score >= 50: return 'Bueno'
        if score >= 25: return 'Regular'
        return 'Necesita Mejora'
    explicaciones = []
    recomendaciones = []
    for _, row in df.iterrows():
        exp = []
        rec = []
        if tipo=='CP':
            if pd.notna(row['cp_llenado']):
                exp.append(f"Llenado: {row['cp_llenado_score']:.1f}pts")
                if row['cp_llenado_score']<50: rec.append('Mejorar ocupación CP')
            if pd.notna(row['cp_inestabilidad']):
                exp.append(f"Estabilidad: {row['cp_inestabilidad_score']:.1f}pts")
                if row['cp_inestabilidad_score']<50: rec.append('Reducir variabilidad CP')
            if pd.notna(row['cp_tasa_cambio']):
                exp.append(f"Cambios: {row['cp_tasa_cambio_score']:.1f}pts")
                if row['cp_tasa_cambio_score']<50: rec.append('Estabilizar cambios CP')
        else:
            if pd.notna(row['hdd_uso']):
                exp.append(f"Uso: {row['hdd_uso_score']:.1f}pts")
                if row['hdd_uso_score']<50: rec.append('Optimizar uso HDD')
            if pd.notna(row['hdd_inestabilidad']):
                exp.append(f"Estabilidad: {row['hdd_inestabilidad_score']:.1f}pts")
                if row['hdd_inestabilidad_score']<50: rec.append('Reducir variabilidad HDD')
            if pd.notna(row['hdd_tasa_cambio']):
                exp.append(f"Cambios: {row['hdd_tasa_cambio_score']:.1f}pts")
                if row['hdd_tasa_cambio_score']<50: rec.append('Estabilizar cambios HDD')
        if not rec:
            rec.append('Mantener rendimiento actual')
        explicaciones.append(' | '.join(exp))
        recomendaciones.append('; '.join(rec))
    df['explicacion'] = explicaciones
    df['recomendaciones'] = recomendaciones
    df['categoria'] = df['score_final'].apply(categoria)
    return df

# --- Main ---
def main():
    # Configuración de métricas
    metric_configs_cp = {
        'cp_llenado': {'direction':'higher_better','weight':1/3},
        'cp_inestabilidad': {'direction':'lower_better','weight':1/3},
        'cp_tasa_cambio': {'direction':'lower_better','weight':1/3},
    }
    metric_configs_hdd = {
        'hdd_uso': {'direction':'lower_better','weight':1/3},
        'hdd_inestabilidad': {'direction':'lower_better','weight':1/3},
        'hdd_tasa_cambio': {'direction':'lower_better','weight':1/3},
    }
    print("Calculando ranking CP...")
    df_cp = get_cp_metrics()
    df_cp = score_and_explain(df_cp, metric_configs_cp, tipo='CP')
    df_cp = df_cp.sort_values('score_final', ascending=False)
    df_cp['posicion'] = range(1, len(df_cp)+1)
    df_cp.to_csv('ranking_cp.csv', index=False)
    print("\nTOP 10 EQUIPOS - CP")
    print(df_cp[['posicion','equipo','score_final','categoria','explicacion','recomendaciones']].head(10).to_string(index=False))
    print(f"\nTotal equipos CP: {len(df_cp)}")
    print("Ranking CP guardado en ranking_cp.csv")

    print("\nCalculando ranking HDD...")
    df_hdd = get_hdd_metrics()
    df_hdd = score_and_explain(df_hdd, metric_configs_hdd, tipo='HDD')
    df_hdd = df_hdd.sort_values('score_final', ascending=False)
    df_hdd['posicion'] = range(1, len(df_hdd)+1)
    df_hdd.to_csv('ranking_hdd.csv', index=False)
    print("\nTOP 10 EQUIPOS - HDD")
    print(df_hdd[['posicion','equipo','score_final','categoria','explicacion','recomendaciones']].head(10).to_string(index=False))
    print(f"\nTotal equipos HDD: {len(df_hdd)}")
    print("Ranking HDD guardado en ranking_hdd.csv")

if __name__ == "__main__":
    main() 