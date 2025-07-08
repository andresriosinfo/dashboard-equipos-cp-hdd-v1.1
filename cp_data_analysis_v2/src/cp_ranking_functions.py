#!/usr/bin/env python
# coding: utf-8

import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger('cp_data_analysis')

def calcular_ranking_llenado(df_dict):
    """
    Calcula el ranking de equipos por nivel de llenado (valores más altos).
    
    Args:
        df_dict (dict): Diccionario con DataFrames de datos
        
    Returns:
        pd.DataFrame: DataFrame con ranking de equipos por llenado
    """
    registros = []
    fecha_ejecucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for nombre_df, df in df_dict.items():
        try:
            # Verificar columnas requeridas
            columnas_requeridas = {'codigo', 'fecha', 'equipo', 'area', 'valor', 'actualizacion'}
            if not columnas_requeridas.issubset(df.columns):
                logger.warning(f"DataFrame '{nombre_df}' no tiene todas las columnas requeridas")
                continue
            
            if df.empty:
                logger.warning(f"DataFrame '{nombre_df}' está vacío")
                continue
            
            # Crear copia para no modificar el original
            df = df.copy()
            
            # Convertir 'fecha' a tipo datetime
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
            df = df.dropna(subset=['fecha'])
            
            if df.empty:
                continue
            
            # Convertir 'valor' a numérico
            df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
            df = df.dropna(subset=['valor'])
            
            if df.empty:
                continue
            
            # Filtrar los últimos 7 días
            fecha_maxima = df['fecha'].max()
            df_ultimos_7_dias = df[df['fecha'] >= fecha_maxima - timedelta(days=7)]
            
            if df_ultimos_7_dias.empty:
                continue
            
            # Calcular promedio de valores por equipo en los últimos 7 días
            promedio_por_equipo = df_ultimos_7_dias.groupby(['equipo', 'area'])['valor'].mean().reset_index()
            
            # Ordenar por valor promedio (descendente) para crear ranking
            promedio_por_equipo = promedio_por_equipo.sort_values('valor', ascending=False)
            
            # Asignar posiciones del ranking
            promedio_por_equipo['posicion_llenado'] = range(1, len(promedio_por_equipo) + 1)
            
            # Para cada equipo, obtener los últimos 7 valores
            for idx, row in promedio_por_equipo.iterrows():
                equipo = row['equipo']
                area = row['area']
                posicion = row['posicion_llenado']
                valor_promedio = row['valor']
                
                # Obtener los últimos 7 valores del equipo
                df_equipo = df_ultimos_7_dias[df_ultimos_7_dias['equipo'] == equipo].sort_values(by='fecha', ascending=False)
                ultimos_7_valores = df_equipo['valor'].head(7).tolist()
                
                # Rellenar con None si hay menos de 7 valores
                while len(ultimos_7_valores) < 7:
                    ultimos_7_valores.append(None)
                
                registros.append({
                    'id': str(uuid.uuid4()),
                    'area': area,
                    'equipo': equipo,
                    'fecha_ejecucion_del_codigo': fecha_ejecucion,
                    'metrica': 'llenado',
                    'posicion': posicion,
                    'valor_metrico': int(valor_promedio) if pd.notna(valor_promedio) else None,
                    'valor_1': int(ultimos_7_valores[0]) if ultimos_7_valores[0] is not None and pd.notna(ultimos_7_valores[0]) else None,
                    'valor_2': int(ultimos_7_valores[1]) if ultimos_7_valores[1] is not None and pd.notna(ultimos_7_valores[1]) else None,
                    'valor_3': int(ultimos_7_valores[2]) if ultimos_7_valores[2] is not None and pd.notna(ultimos_7_valores[2]) else None,
                    'valor_4': int(ultimos_7_valores[3]) if ultimos_7_valores[3] is not None and pd.notna(ultimos_7_valores[3]) else None,
                    'valor_5': int(ultimos_7_valores[4]) if ultimos_7_valores[4] is not None and pd.notna(ultimos_7_valores[4]) else None,
                    'valor_6': int(ultimos_7_valores[5]) if ultimos_7_valores[5] is not None and pd.notna(ultimos_7_valores[5]) else None,
                    'valor_7': int(ultimos_7_valores[6]) if ultimos_7_valores[6] is not None and pd.notna(ultimos_7_valores[6]) else None
                })
                
        except Exception as e:
            logger.error(f"Error procesando DataFrame '{nombre_df}' para ranking de llenado: {str(e)}")
            continue
    
    return pd.DataFrame(registros)

def calcular_ranking_inestabilidad(df_dict):
    """
    Calcula el ranking de equipos por inestabilidad (desviación estándar).
    
    Args:
        df_dict (dict): Diccionario con DataFrames de datos
        
    Returns:
        pd.DataFrame: DataFrame con ranking de equipos por inestabilidad
    """
    registros = []
    fecha_ejecucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for nombre_df, df in df_dict.items():
        try:
            # Verificar columnas requeridas
            columnas_requeridas = {'codigo', 'fecha', 'equipo', 'area', 'valor', 'actualizacion'}
            if not columnas_requeridas.issubset(df.columns):
                logger.warning(f"DataFrame '{nombre_df}' no tiene todas las columnas requeridas")
                continue
            
            if df.empty:
                logger.warning(f"DataFrame '{nombre_df}' está vacío")
                continue
            
            # Crear copia para no modificar el original
            df = df.copy()
            
            # Convertir 'fecha' a tipo datetime
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
            df = df.dropna(subset=['fecha'])
            
            if df.empty:
                continue
            
            # Convertir 'valor' a numérico
            df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
            df = df.dropna(subset=['valor'])
            
            if df.empty:
                continue
            
            # Filtrar los últimos 7 días
            fecha_maxima = df['fecha'].max()
            df_ultimos_7_dias = df[df['fecha'] >= fecha_maxima - timedelta(days=7)]
            
            if df_ultimos_7_dias.empty:
                continue
            
            # Calcular desviación estándar por equipo
            desviacion_por_equipo = df_ultimos_7_dias.groupby(['equipo', 'area'])['valor'].std().reset_index()
            desviacion_por_equipo = desviacion_por_equipo.rename(columns={'valor': 'desviacion'})
            
            # Ordenar por desviación estándar (descendente) para crear ranking
            desviacion_por_equipo = desviacion_por_equipo.sort_values('desviacion', ascending=False)
            
            # Asignar posiciones del ranking
            desviacion_por_equipo['posicion_inestabilidad'] = range(1, len(desviacion_por_equipo) + 1)
            
            # Para cada equipo, obtener los últimos 7 valores
            for idx, row in desviacion_por_equipo.iterrows():
                equipo = row['equipo']
                area = row['area']
                posicion = row['posicion_inestabilidad']
                desviacion = row['desviacion']
                
                # Obtener los últimos 7 valores del equipo
                df_equipo = df_ultimos_7_dias[df_ultimos_7_dias['equipo'] == equipo].sort_values(by='fecha', ascending=False)
                ultimos_7_valores = df_equipo['valor'].head(7).tolist()
                
                # Rellenar con None si hay menos de 7 valores
                while len(ultimos_7_valores) < 7:
                    ultimos_7_valores.append(None)
                
                registros.append({
                    'id': str(uuid.uuid4()),
                    'area': area,
                    'equipo': equipo,
                    'fecha_ejecucion_del_codigo': fecha_ejecucion,
                    'metrica': 'inestabilidad',
                    'posicion': posicion,
                    'valor_metrico': int(desviacion * 1000) if pd.notna(desviacion) else None,  # Convert to integer (multiply by 1000 to preserve precision)
                    'valor_1': int(ultimos_7_valores[0]) if ultimos_7_valores[0] is not None and pd.notna(ultimos_7_valores[0]) else None,
                    'valor_2': int(ultimos_7_valores[1]) if ultimos_7_valores[1] is not None and pd.notna(ultimos_7_valores[1]) else None,
                    'valor_3': int(ultimos_7_valores[2]) if ultimos_7_valores[2] is not None and pd.notna(ultimos_7_valores[2]) else None,
                    'valor_4': int(ultimos_7_valores[3]) if ultimos_7_valores[3] is not None and pd.notna(ultimos_7_valores[3]) else None,
                    'valor_5': int(ultimos_7_valores[4]) if ultimos_7_valores[4] is not None and pd.notna(ultimos_7_valores[4]) else None,
                    'valor_6': int(ultimos_7_valores[5]) if ultimos_7_valores[5] is not None and pd.notna(ultimos_7_valores[5]) else None,
                    'valor_7': int(ultimos_7_valores[6]) if ultimos_7_valores[6] is not None and pd.notna(ultimos_7_valores[6]) else None
                })
                
        except Exception as e:
            logger.error(f"Error procesando DataFrame '{nombre_df}' para ranking de inestabilidad: {str(e)}")
            continue
    
    return pd.DataFrame(registros)

def calcular_ranking_tasa_cambio(df_dict):
    """
    Calcula el ranking de equipos por tasa de cambio (variabilidad de cambios).
    
    Args:
        df_dict (dict): Diccionario con DataFrames de datos
        
    Returns:
        pd.DataFrame: DataFrame con ranking de equipos por tasa de cambio
    """
    registros = []
    fecha_ejecucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for nombre_df, df in df_dict.items():
        try:
            # Verificar columnas requeridas
            columnas_requeridas = {'codigo', 'fecha', 'equipo', 'area', 'valor', 'actualizacion'}
            if not columnas_requeridas.issubset(df.columns):
                logger.warning(f"DataFrame '{nombre_df}' no tiene todas las columnas requeridas")
                continue
            
            if df.empty:
                logger.warning(f"DataFrame '{nombre_df}' está vacío")
                continue
            
            # Crear copia para no modificar el original
            df = df.copy()
            
            # Convertir 'fecha' a tipo datetime
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
            df = df.dropna(subset=['fecha'])
            
            if df.empty:
                continue
            
            # Convertir 'valor' a numérico
            df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
            df = df.dropna(subset=['valor'])
            
            if df.empty:
                continue
            
            # Filtrar los últimos 7 días
            fecha_maxima = df['fecha'].max()
            df_ultimos_7_dias = df[df['fecha'] >= fecha_maxima - timedelta(days=7)]
            
            if df_ultimos_7_dias.empty:
                continue
            
            # Ordenar por fecha para calcular tasas de cambio
            df_ultimos_7_dias = df_ultimos_7_dias.sort_values(['equipo', 'fecha'])
            
            # Calcular tasa de cambio por equipo
            df_ultimos_7_dias['tasa_cambio'] = df_ultimos_7_dias.groupby('equipo')['valor'].pct_change()
            
            # Calcular desviación estándar de la tasa de cambio por equipo
            tasa_cambio_por_equipo = df_ultimos_7_dias.groupby(['equipo', 'area'])['tasa_cambio'].std().reset_index()
            tasa_cambio_por_equipo = tasa_cambio_por_equipo.rename(columns={'tasa_cambio': 'variabilidad_tasa'})
            
            # Eliminar valores NaN
            tasa_cambio_por_equipo = tasa_cambio_por_equipo.dropna()
            
            if tasa_cambio_por_equipo.empty:
                continue
            
            # Ordenar por variabilidad de tasa de cambio (descendente) para crear ranking
            tasa_cambio_por_equipo = tasa_cambio_por_equipo.sort_values('variabilidad_tasa', ascending=False)
            
            # Asignar posiciones del ranking
            tasa_cambio_por_equipo['posicion_tasa_cambio'] = range(1, len(tasa_cambio_por_equipo) + 1)
            
            # Para cada equipo, obtener los últimos 7 valores
            for idx, row in tasa_cambio_por_equipo.iterrows():
                equipo = row['equipo']
                area = row['area']
                posicion = row['posicion_tasa_cambio']
                variabilidad = row['variabilidad_tasa']
                
                # Obtener los últimos 7 valores del equipo
                df_equipo = df_ultimos_7_dias[df_ultimos_7_dias['equipo'] == equipo].sort_values(by='fecha', ascending=False)
                ultimos_7_valores = df_equipo['valor'].head(7).tolist()
                
                # Rellenar con None si hay menos de 7 valores
                while len(ultimos_7_valores) < 7:
                    ultimos_7_valores.append(None)
                
                registros.append({
                    'id': str(uuid.uuid4()),
                    'area': area,
                    'equipo': equipo,
                    'fecha_ejecucion_del_codigo': fecha_ejecucion,
                    'metrica': 'tasa_cambio',
                    'posicion': posicion,
                    'valor_metrico': int(variabilidad * 10000) if pd.notna(variabilidad) else None,  # Convert to integer (multiply by 10000 to preserve precision)
                    'valor_1': int(ultimos_7_valores[0]) if ultimos_7_valores[0] is not None and pd.notna(ultimos_7_valores[0]) else None,
                    'valor_2': int(ultimos_7_valores[1]) if ultimos_7_valores[1] is not None and pd.notna(ultimos_7_valores[1]) else None,
                    'valor_3': int(ultimos_7_valores[2]) if ultimos_7_valores[2] is not None and pd.notna(ultimos_7_valores[2]) else None,
                    'valor_4': int(ultimos_7_valores[3]) if ultimos_7_valores[3] is not None and pd.notna(ultimos_7_valores[3]) else None,
                    'valor_5': int(ultimos_7_valores[4]) if ultimos_7_valores[4] is not None and pd.notna(ultimos_7_valores[4]) else None,
                    'valor_6': int(ultimos_7_valores[5]) if ultimos_7_valores[5] is not None and pd.notna(ultimos_7_valores[5]) else None,
                    'valor_7': int(ultimos_7_valores[6]) if ultimos_7_valores[6] is not None and pd.notna(ultimos_7_valores[6]) else None
                })
                
        except Exception as e:
            logger.error(f"Error procesando DataFrame '{nombre_df}' para ranking de tasa de cambio: {str(e)}")
            continue
    
    return pd.DataFrame(registros)

def generar_ranking_completo(df_dict):
    """
    Genera un ranking completo de equipos basado en las tres métricas clave.
    
    Args:
        df_dict (dict): Diccionario con DataFrames de datos
        
    Returns:
        pd.DataFrame: DataFrame con ranking completo de equipos
    """
    try:
        logger.info("Iniciando generación de ranking completo...")
        
        if not df_dict:
            logger.warning("No hay datos para generar ranking: diccionario vacío")
            return pd.DataFrame()
        
        # Calcular rankings individuales
        logger.info("Calculando ranking por llenado...")
        df_llenado = calcular_ranking_llenado(df_dict)
        
        logger.info("Calculando ranking por inestabilidad...")
        df_inestabilidad = calcular_ranking_inestabilidad(df_dict)
        
        logger.info("Calculando ranking por tasa de cambio...")
        df_tasa_cambio = calcular_ranking_tasa_cambio(df_dict)
        
        # Concatenar todos los rankings
        dfs = []
        if not df_llenado.empty:
            dfs.append(df_llenado)
        if not df_inestabilidad.empty:
            dfs.append(df_inestabilidad)
        if not df_tasa_cambio.empty:
            dfs.append(df_tasa_cambio)
        
        if not dfs:
            logger.warning("No se generaron rankings válidos")
            return pd.DataFrame()
        
        # Concatenar todos los resultados
        df_ranking_completo = pd.concat(dfs, ignore_index=True)
        
        logger.info(f"Ranking completo generado exitosamente: {len(df_ranking_completo)} registros")
        
        return df_ranking_completo
        
    except Exception as e:
        logger.error(f"Error generando ranking completo: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return pd.DataFrame() 