#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import ast

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de áreas CP con sus significados
AREAS_CP_SIGNIFICADO = {
    'PP_NFD': 'Archivos no encontrados',
    'IOLOAD': 'Carga de entrada/salida',
    'totmem': 'Memoria total utilizada',
    'CUMOVR': 'Sobrecarga acumulativa',
    'OMOVRN': 'Overhead de memoria',
    'TLCONS': 'Tiempo de respuesta de consola',
    'OMLDAV': 'Carga promedio de memoria',
    'CPLOAD': 'Carga del procesador',
    'MAXMEM': 'Memoria máxima utilizada'
}

def calculate_percentile_score(value, all_values, direction='lower_better'):
    """Calcula el puntaje basado en percentiles"""
    if pd.isna(value) or len(all_values) == 0:
        return 0.0
    
    valid_values = [v for v in all_values if not pd.isna(v)]
    if len(valid_values) == 0:
        return 0.0
    
    percentile = (sum(1 for x in valid_values if x < value) / len(valid_values)) * 100
    
    if direction == 'lower_better':
        percentile = 100 - percentile
    
    return percentile

def generate_area_explanation(equipo, area, valor, all_values, area_nombre, metric_type):
    """Genera explicación específica por área y tipo de métrica"""
    score = calculate_percentile_score(valor, all_values, 'lower_better')
    
    if metric_type == 'llenado':
        if score >= 80:
            return f"**{area_nombre} Excelente ({score:.1f}pts)**: El equipo mantiene una carga baja de {valor:.1f} en {area}, lo que indica un rendimiento excepcional."
        elif score >= 60:
            return f"**{area_nombre} Buena ({score:.1f}pts)**: Con una carga de {valor:.1f} en {area}, el equipo tiene un rendimiento aceptable."
        elif score >= 40:
            return f"**{area_nombre} Regular ({score:.1f}pts)**: La carga de {valor:.1f} en {area} sugiere que el equipo podría estar experimentando problemas de rendimiento."
        else:
            return f"**{area_nombre} Crítica ({score:.1f}pts)**: Con una carga alta de {valor:.1f} en {area}, el equipo está experimentando problemas significativos de rendimiento."
    
    elif metric_type == 'inestabilidad':
        if score >= 80:
            return f"**Estabilidad en {area_nombre} Excelente ({score:.1f}pts)**: El equipo muestra una variabilidad muy baja ({valor:.1f}), indicando un funcionamiento muy estable."
        elif score >= 60:
            return f"**Estabilidad en {area_nombre} Buena ({score:.1f}pts)**: La variabilidad de {valor:.1f} indica un funcionamiento estable con algunas fluctuaciones menores."
        elif score >= 40:
            return f"**Estabilidad en {area_nombre} Regular ({score:.1f}pts)**: La variabilidad de {valor:.1f} sugiere inestabilidad que puede afectar el rendimiento."
        else:
            return f"**Estabilidad en {area_nombre} Crítica ({score:.1f}pts)**: La alta variabilidad de {valor:.1f} indica problemas graves de estabilidad."
    
    elif metric_type == 'tasa_cambio':
        if score >= 80:
            return f"**Cambios en {area_nombre} Predecibles ({score:.1f}pts)**: Los cambios en {area} son muy predecibles ({valor:.1f}), indicando un funcionamiento estable."
        elif score >= 60:
            return f"**Cambios en {area_nombre} Estables ({score:.1f}pts)**: Los cambios en {area} son relativamente estables ({valor:.1f})."
        elif score >= 40:
            return f"**Cambios en {area_nombre} Variables ({score:.1f}pts)**: Los cambios en {area} son impredecibles ({valor:.1f}), lo que puede afectar el rendimiento."
        else:
            return f"**Cambios en {area_nombre} Caóticos ({score:.1f}pts)**: Los cambios en {area} son muy impredecibles ({valor:.1f}), requiriendo atención inmediata."

def generate_recommendations(equipo, explicaciones_por_area):
    """Genera recomendaciones basadas en las explicaciones por área"""
    recomendaciones = []
    
    # Analizar explicaciones por área
    areas_criticas = []
    areas_regulares = []
    
    for explicacion in explicaciones_por_area:
        if "Crítica" in explicacion:
            # Extraer el nombre del área
            if "en " in explicacion:
                area_part = explicacion.split("en ")[1].split(" ")[0]
                if area_part in AREAS_CP_SIGNIFICADO:
                    areas_criticas.append(AREAS_CP_SIGNIFICADO[area_part])
        elif "Regular" in explicacion:
            if "en " in explicacion:
                area_part = explicacion.split("en ")[1].split(" ")[0]
                if area_part in AREAS_CP_SIGNIFICADO:
                    areas_regulares.append(AREAS_CP_SIGNIFICADO[area_part])
    
    # Generar recomendaciones específicas
    if areas_criticas:
        areas_unicas = list(set(areas_criticas))
        if len(areas_unicas) == 1:
            recomendaciones.append(f"Intervención inmediata requerida en {areas_unicas[0]}")
        else:
            recomendaciones.append(f"Intervención inmediata requerida en múltiples áreas: {', '.join(areas_unicas[:3])}")
    
    if areas_regulares:
        areas_unicas = list(set(areas_regulares))
        if len(areas_unicas) == 1:
            recomendaciones.append(f"Optimizar rendimiento en {areas_unicas[0]}")
        else:
            recomendaciones.append(f"Optimizar rendimiento en múltiples áreas: {', '.join(areas_unicas[:3])}")
    
    # Recomendaciones generales
    if not areas_criticas and not areas_regulares:
        recomendaciones.append("Mantener estándares actuales de rendimiento")
    elif len(areas_criticas) > 3:
        recomendaciones.append("Revisión completa del equipo requerida")
    
    return '; '.join(recomendaciones)

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

def generate_rankings_with_area_explanations():
    """Genera rankings con explicaciones por área"""
    logger.info("Generando rankings con explicaciones por área...")
    
    # Cargar datos
    df_cp = get_cp_metrics()
    df_hdd = get_hdd_metrics()
    
    if df_cp.empty and df_hdd.empty:
        logger.error("No se pudieron cargar datos")
        return None, None
    
    # Procesar CP con explicaciones por área
    if not df_cp.empty:
        logger.info("Procesando datos CP...")
        
        # Calcular puntuaciones CP (CORREGIDO: todas lower_better)
        df_cp['cp_llenado_score'] = df_cp['cp_llenado'].apply(
            lambda x: calculate_percentile_score(x, df_cp['cp_llenado'].dropna(), 'lower_better')
        )
        df_cp['cp_inestabilidad_score'] = df_cp['cp_inestabilidad'].apply(
            lambda x: calculate_percentile_score(x, df_cp['cp_inestabilidad'].dropna(), 'lower_better')
        )
        df_cp['cp_tasa_cambio_score'] = df_cp['cp_tasa_cambio'].apply(
            lambda x: calculate_percentile_score(x, df_cp['cp_tasa_cambio'].dropna(), 'lower_better')
        )
        
        # Calcular puntuación final CP
        df_cp['score_final'] = (
            df_cp['cp_llenado_score'] * 0.4 +
            df_cp['cp_inestabilidad_score'] * 0.3 +
            df_cp['cp_tasa_cambio_score'] * 0.3
        )
        
        # Generar explicaciones por área
        explicaciones_cp = []
        recomendaciones_cp = []
        
        for idx, row in df_cp.iterrows():
            equipo_explicaciones = []
            
            # Obtener áreas del equipo
            areas_equipo = row['areas_cp']
            if isinstance(areas_equipo, str):
                try:
                    areas_list = ast.literal_eval(areas_equipo)
                    if not isinstance(areas_list, list):
                        areas_list = [areas_list]
                except:
                    areas_list = [areas_equipo]
            else:
                areas_list = areas_equipo if isinstance(areas_equipo, list) else [areas_equipo]
            
            # Generar explicaciones para cada área
            for area in areas_list:
                if area in AREAS_CP_SIGNIFICADO:
                    area_nombre = AREAS_CP_SIGNIFICADO[area]
                    
                    # Explicación de llenado
                    explicacion_llenado = generate_area_explanation(
                        row['equipo'], area, row['cp_llenado'], 
                        df_cp['cp_llenado'].dropna(), area_nombre, 'llenado'
                    )
                    equipo_explicaciones.append(explicacion_llenado)
                    
                    # Explicación de inestabilidad
                    explicacion_inestabilidad = generate_area_explanation(
                        row['equipo'], area, row['cp_inestabilidad'],
                        df_cp['cp_inestabilidad'].dropna(), area_nombre, 'inestabilidad'
                    )
                    equipo_explicaciones.append(explicacion_inestabilidad)
                    
                    # Explicación de tasa de cambio
                    explicacion_tasa_cambio = generate_area_explanation(
                        row['equipo'], area, row['cp_tasa_cambio'],
                        df_cp['cp_tasa_cambio'].dropna(), area_nombre, 'tasa_cambio'
                    )
                    equipo_explicaciones.append(explicacion_tasa_cambio)
            
            explicaciones_cp.append(' | '.join(equipo_explicaciones))
            
            # Generar recomendaciones
            recomendacion = generate_recommendations(row['equipo'], equipo_explicaciones)
            recomendaciones_cp.append(recomendacion)
        
        df_cp['explicacion'] = explicaciones_cp
        df_cp['recomendaciones'] = recomendaciones_cp
        
        # Categorizar
        df_cp['categoria'] = pd.cut(
            df_cp['score_final'],
            bins=[0, 25, 50, 75, 90, 100],
            labels=['Necesita Mejora', 'Regular', 'Bueno', 'Muy Bueno', 'Excelente'],
            include_lowest=True
        )
        
        # Ordenar por puntuación
        df_cp = df_cp.sort_values('score_final', ascending=False)
        df_cp['posicion'] = range(1, len(df_cp) + 1)
    
    # Procesar HDD
    if not df_hdd.empty:
        logger.info("Procesando datos HDD...")
        
        # Calcular puntuaciones HDD (lower_better)
        df_hdd['hdd_uso_score'] = df_hdd['hdd_uso'].apply(
            lambda x: calculate_percentile_score(x, df_hdd['hdd_uso'].dropna(), 'lower_better')
        )
        df_hdd['hdd_inestabilidad_score'] = df_hdd['hdd_inestabilidad'].apply(
            lambda x: calculate_percentile_score(x, df_hdd['hdd_inestabilidad'].dropna(), 'lower_better')
        )
        df_hdd['hdd_tasa_cambio_score'] = df_hdd['hdd_tasa_cambio'].apply(
            lambda x: calculate_percentile_score(x, df_hdd['hdd_tasa_cambio'].dropna(), 'lower_better')
        )
        
        # Calcular puntuación final HDD
        df_hdd['score_final'] = (
            df_hdd['hdd_uso_score'] * 0.4 +
            df_hdd['hdd_inestabilidad_score'] * 0.4 +
            df_hdd['hdd_tasa_cambio_score'] * 0.2
        )
        
        # Generar explicaciones HDD
        explicaciones_hdd = []
        recomendaciones_hdd = []
        
        for idx, row in df_hdd.iterrows():
            equipo_explicaciones = []
            
            # Explicación de uso HDD
            if not pd.isna(row['hdd_uso']):
                uso_score = row['hdd_uso_score']
                if uso_score >= 80:
                    explicacion = f"**Uso HDD Excelente ({uso_score:.1f}pts)**: El disco está siendo utilizado eficientemente al {row['hdd_uso']:.1f}%."
                elif uso_score >= 60:
                    explicacion = f"**Uso HDD Bueno ({uso_score:.1f}pts)**: El uso del {row['hdd_uso']:.1f}% es aceptable."
                elif uso_score >= 40:
                    explicacion = f"**Uso HDD Regular ({uso_score:.1f}pts)**: El uso del {row['hdd_uso']:.1f}% sugiere que el disco podría estar sobrecargado."
                else:
                    explicacion = f"**Uso HDD Crítico ({uso_score:.1f}pts)**: El uso del {row['hdd_uso']:.1f}% indica problemas graves de espacio en disco."
                equipo_explicaciones.append(explicacion)
            
            # Explicación de inestabilidad HDD
            if not pd.isna(row['hdd_inestabilidad']):
                inestabilidad_score = row['hdd_inestabilidad_score']
                if inestabilidad_score >= 80:
                    explicacion = f"**Estabilidad HDD Excelente ({inestabilidad_score:.1f}pts)**: El uso del disco es muy estable."
                elif inestabilidad_score >= 60:
                    explicacion = f"**Estabilidad HDD Buena ({inestabilidad_score:.1f}pts)**: El uso del disco es relativamente estable."
                elif inestabilidad_score >= 40:
                    explicacion = f"**Estabilidad HDD Regular ({inestabilidad_score:.1f}pts)**: El uso del disco muestra variabilidad que puede afectar el rendimiento."
                else:
                    explicacion = f"**Estabilidad HDD Crítica ({inestabilidad_score:.1f}pts)**: El uso del disco es muy inestable, requiriendo atención inmediata."
                equipo_explicaciones.append(explicacion)
            
            # Explicación de tasa de cambio HDD
            if not pd.isna(row['hdd_tasa_cambio']):
                tasa_cambio_score = row['hdd_tasa_cambio_score']
                if tasa_cambio_score >= 80:
                    explicacion = f"**Cambios HDD Predecibles ({tasa_cambio_score:.1f}pts)**: Los cambios en el uso del disco son muy predecibles."
                elif tasa_cambio_score >= 60:
                    explicacion = f"**Cambios HDD Estables ({tasa_cambio_score:.1f}pts)**: Los cambios en el uso del disco son relativamente estables."
                elif tasa_cambio_score >= 40:
                    explicacion = f"**Cambios HDD Variables ({tasa_cambio_score:.1f}pts)**: Los cambios en el uso del disco son impredecibles."
                else:
                    explicacion = f"**Cambios HDD Caóticos ({tasa_cambio_score:.1f}pts)**: Los cambios en el uso del disco son muy impredecibles."
                equipo_explicaciones.append(explicacion)
            
            explicaciones_hdd.append(' | '.join(equipo_explicaciones))
            
            # Generar recomendaciones HDD
            recomendacion = generate_recommendations(row['equipo'], equipo_explicaciones)
            recomendaciones_hdd.append(recomendacion)
        
        df_hdd['explicacion'] = explicaciones_hdd
        df_hdd['recomendaciones'] = recomendaciones_hdd
        
        # Categorizar
        df_hdd['categoria'] = pd.cut(
            df_hdd['score_final'],
            bins=[0, 25, 50, 75, 90, 100],
            labels=['Necesita Mejora', 'Regular', 'Bueno', 'Muy Bueno', 'Excelente'],
            include_lowest=True
        )
        
        # Ordenar por puntuación
        df_hdd = df_hdd.sort_values('score_final', ascending=False)
        df_hdd['posicion'] = range(1, len(df_hdd) + 1)
    
    return df_cp, df_hdd

def main():
    """Función principal"""
    try:
        logger.info("Iniciando generación de rankings con explicaciones por área...")
        
        # Generar rankings
        df_cp, df_hdd = generate_rankings_with_area_explanations()
        
        if df_cp is not None and not df_cp.empty:
            # Guardar ranking CP
            df_cp.to_csv('ranking_cp_v2.csv', index=False)
            logger.info(f"Ranking CP guardado en ranking_cp_v2.csv")
            
            # Mostrar resumen CP
            print(f"\n=== RESUMEN RANKING CP V2 ===")
            print(f"Total equipos CP: {len(df_cp)}")
            print(f"Puntuación promedio: {df_cp['score_final'].mean():.2f}")
            print(f"Mejor equipo: {df_cp.iloc[0]['equipo']} ({df_cp.iloc[0]['score_final']:.2f} pts)")
            print(f"Peor equipo: {df_cp.iloc[-1]['equipo']} ({df_cp.iloc[-1]['score_final']:.2f} pts)")
            
            # Distribución por categorías
            print(f"\nDistribución por categorías CP:")
            categorias = df_cp['categoria'].value_counts()
            for cat, count in categorias.items():
                porcentaje = (count / len(df_cp)) * 100
                print(f"  {cat}: {count} equipos ({porcentaje:.1f}%)")
        
        if df_hdd is not None and not df_hdd.empty:
            # Guardar ranking HDD
            df_hdd.to_csv('ranking_hdd_v2.csv', index=False)
            logger.info(f"Ranking HDD guardado en ranking_hdd_v2.csv")
            
            # Mostrar resumen HDD
            print(f"\n=== RESUMEN RANKING HDD V2 ===")
            print(f"Total equipos HDD: {len(df_hdd)}")
            print(f"Puntuación promedio: {df_hdd['score_final'].mean():.2f}")
            print(f"Mejor equipo: {df_hdd.iloc[0]['equipo']} ({df_hdd.iloc[0]['score_final']:.2f} pts)")
            print(f"Peor equipo: {df_hdd.iloc[-1]['equipo']} ({df_hdd.iloc[-1]['score_final']:.2f} pts)")
            
            # Distribución por categorías
            print(f"\nDistribución por categorías HDD:")
            categorias = df_hdd['categoria'].value_counts()
            for cat, count in categorias.items():
                porcentaje = (count / len(df_hdd)) * 100
                print(f"  {cat}: {count} equipos ({porcentaje:.1f}%)")
        
        print(f"\n✅ Rankings generados exitosamente con explicaciones por área")
        print(f"📝 Cambios principales:")
        print(f"  1. CP_LLENADO ahora es 'lower_better' (menor = mejor)")
        print(f"  2. Explicaciones específicas por cada área CP")
        print(f"  3. Recomendaciones basadas en áreas problemáticas")
        print(f"  4. Consideración de equipos sin todas las áreas")
        
    except Exception as e:
        logger.error(f"Error generando rankings: {str(e)}")
        raise

if __name__ == "__main__":
    main() 