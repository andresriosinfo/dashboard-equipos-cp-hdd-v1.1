#!/usr/bin/env python
# coding: utf-8

import warnings
warnings.filterwarnings('ignore')
import pandas as pd
from datetime import datetime, timedelta
import uuid  # Para generar identificadores únicos

def encontrar_maximo_por_equipo(df_dict):
    """Encuentra el equipo con el valor máximo de uso en los últimos 7 días para cada DataFrame en el diccionario.
    
    Args:
        df_dict (dict): Diccionario donde las claves son nombres y los valores son DataFrames
        
    Returns:
        pd.DataFrame: DataFrame con información sobre los equipos con valores máximos de uso
        
    Raises:
        ValueError: Si los DataFrames no tienen las columnas requeridas
        TypeError: Si df_dict no es un diccionario
    """
    import logging
    logger = logging.getLogger('hdd_data_analysis')
    
    if not isinstance(df_dict, dict):
        error_msg = f"Se esperaba un diccionario, pero se recibió {type(df_dict)}"
        logger.error(error_msg)
        raise TypeError(error_msg)
        
    resultados = []  # Lista para almacenar los resultados como diccionarios
    fecha_ejecucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fecha de ejecución del código
    
    if not df_dict:
        logger.warning("El diccionario de DataFrames está vacío")
        return pd.DataFrame()
    
    for nombre_df, df in df_dict.items():
        try:
            # Verificar columnas requeridas para HDD
            columnas_requeridas = {'codigo', 'fecha', 'equipo', 'unidad', 'uso'}
            if not columnas_requeridas.issubset(df.columns):
                columnas_faltantes = columnas_requeridas - set(df.columns)
                error_msg = f"El DataFrame '{nombre_df}' no tiene las columnas requeridas. Faltantes: {columnas_faltantes}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            if df.empty:
                logger.warning(f"El DataFrame '{nombre_df}' está vacío.")
                continue
            
            # Crear copia para no modificar el original
            df = df.copy()
            
            # Convertir 'fecha' a tipo datetime con manejo de errores
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
            # Eliminar filas con fechas inválidas
            na_dates = df['fecha'].isna().sum()
            if na_dates > 0:
                logger.warning(f"Se encontraron {na_dates} fechas inválidas en '{nombre_df}' que serán ignoradas")
                df = df.dropna(subset=['fecha'])
                
            if df.empty:
                logger.warning(f"El DataFrame '{nombre_df}' quedó vacío después de eliminar fechas inválidas")
                continue
            
            # Convertir 'uso' a numérico
            df['uso'] = pd.to_numeric(df['uso'], errors='coerce')
            na_values = df['uso'].isna().sum()
            if na_values > 0:
                logger.warning(f"Se encontraron {na_values} valores numéricos inválidos en '{nombre_df}' que serán ignorados")
                df = df.dropna(subset=['uso'])
            
            if df.empty:
                logger.warning(f"El DataFrame '{nombre_df}' quedó vacío después de eliminar valores numéricos inválidos")
                continue
                
            # Filtrar los últimos 7 días
            fecha_maxima = df['fecha'].max()
            df_ultimos_7_dias = df[df['fecha'] >= fecha_maxima - timedelta(days=7)]
        
            if df_ultimos_7_dias.empty:
                logger.warning(f"No hay datos en los últimos 7 días para '{nombre_df}'.")
                continue
            
            # Encontrar el equipo con el valor máximo de uso en los últimos 7 días con manejo de excepciones
            try:
                idx_max = df_ultimos_7_dias['uso'].idxmax()
                equipo_maximo = df_ultimos_7_dias.loc[idx_max, 'equipo']
                unidad_equipo = df_ultimos_7_dias.loc[idx_max, 'unidad']
                
                # Filtrar los últimos 7 valores de uso de ese equipo
                df_equipo = df_ultimos_7_dias[df_ultimos_7_dias['equipo'] == equipo_maximo].sort_values(by='fecha', ascending=False)
                
                if df_equipo.empty:
                    logger.warning(f"No se encontraron datos para el equipo {equipo_maximo} en '{nombre_df}'")
                    continue
                    
                ultimos_7_valores = df_equipo['uso'].head(7).tolist()  # Obtener los últimos 7 valores de uso
        
                # Si hay menos de 7 valores, rellenar con None
                while len(ultimos_7_valores) < 7:
                    ultimos_7_valores.append(None)
                
                # Agregar resultado a la lista con columnas separadas
                resultados.append({
                    'id': str(uuid.uuid4()),  # Generar un identificador único
                    'unidad': unidad_equipo,
                    'equipo': equipo_maximo,
                    'fecha_ejecucion_del_codigo': fecha_ejecucion,
                    'metrica': 'max',
                    'valor_1': ultimos_7_valores[0],
                    'valor_2': ultimos_7_valores[1],
                    'valor_3': ultimos_7_valores[2],
                    'valor_4': ultimos_7_valores[3],
                    'valor_5': ultimos_7_valores[4],
                    'valor_6': ultimos_7_valores[5],
                    'valor_7': ultimos_7_valores[6]
                })
                logger.debug(f"Procesado máximo para '{nombre_df}': equipo {equipo_maximo}")
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Error al encontrar el valor máximo en '{nombre_df}': {str(e)}")
                continue
                
        except Exception as e:
            logger.error(f"Error procesando DataFrame '{nombre_df}': {str(e)}")
            continue
    
    # Convertir la lista de resultados en un DataFrame
    if not resultados:
        logger.warning("No se encontraron resultados máximos para ningún DataFrame")
        return pd.DataFrame()
        
    try:
        df_resultados = pd.DataFrame(resultados)
        logger.info(f"Análisis de máximos HDD completado: {len(df_resultados)} registros generados")
        return df_resultados
    except Exception as e:
        logger.error(f"Error al crear DataFrame de resultados: {str(e)}")
        return pd.DataFrame()


def encontrar_minimo_por_equipo(df_dict):
    """Encuentra el equipo con el valor mínimo de uso en los últimos 7 días para cada DataFrame en el diccionario.
    
    Args:
        df_dict (dict): Diccionario donde las claves son nombres y los valores son DataFrames
        
    Returns:
        pd.DataFrame: DataFrame con información sobre los equipos con valores mínimos de uso
    """
    import logging
    logger = logging.getLogger('hdd_data_analysis')
    
    resultados = []  # Lista para almacenar los resultados como diccionarios
    fecha_ejecucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fecha de ejecución del código
    
    for nombre_df, df in df_dict.items():
        try:
            # Verificar columnas requeridas para HDD
            columnas_requeridas = {'codigo', 'fecha', 'equipo', 'unidad', 'uso'}
            if not columnas_requeridas.issubset(df.columns):
                columnas_faltantes = columnas_requeridas - set(df.columns)
                error_msg = f"El DataFrame '{nombre_df}' no tiene las columnas requeridas. Faltantes: {columnas_faltantes}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            if df.empty:
                logger.warning(f"El DataFrame '{nombre_df}' está vacío.")
                continue
            
            # Crear copia para no modificar el original
            df = df.copy()
            
            # Convertir 'fecha' a tipo datetime y filtrar los últimos 7 días
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
            df = df.dropna(subset=['fecha'])
            
            if df.empty:
                logger.warning(f"El DataFrame '{nombre_df}' quedó vacío después de eliminar fechas inválidas")
                continue
            
            fecha_maxima = df['fecha'].max()
            df_ultimos_7_dias = df[df['fecha'] >= fecha_maxima - timedelta(days=7)]
            
            if df_ultimos_7_dias.empty:
                logger.warning(f"No hay datos en los últimos 7 días para '{nombre_df}'.")
                continue
            
            # Convertir 'uso' a numérico
            df_ultimos_7_dias['uso'] = pd.to_numeric(df_ultimos_7_dias['uso'], errors='coerce')
            df_ultimos_7_dias = df_ultimos_7_dias.dropna(subset=['uso'])
            
            if df_ultimos_7_dias.empty:
                logger.warning(f"El DataFrame '{nombre_df}' quedó vacío después de eliminar valores numéricos inválidos")
                continue
            
            # Encontrar el equipo con el valor mínimo de uso en los últimos 7 días
            try:
                idx_min = df_ultimos_7_dias['uso'].idxmin()
                equipo_minimo = df_ultimos_7_dias.loc[idx_min, 'equipo']
                unidad_equipo = df_ultimos_7_dias.loc[idx_min, 'unidad']
                
                # Filtrar los últimos 7 valores de uso de ese equipo
                df_equipo = df_ultimos_7_dias[df_ultimos_7_dias['equipo'] == equipo_minimo].sort_values(by='fecha', ascending=False)
                ultimos_7_valores = df_equipo['uso'].head(7).tolist()  # Obtener los últimos 7 valores de uso
                
                # Si hay menos de 7 valores, rellenar con None
                while len(ultimos_7_valores) < 7:
                    ultimos_7_valores.append(None)
                
                # Agregar resultado a la lista con columnas separadas
                resultados.append({
                    'id': str(uuid.uuid4()),  # Generar un identificador único
                    'unidad': unidad_equipo,
                    'equipo': equipo_minimo,
                    'fecha_ejecucion_del_codigo': fecha_ejecucion,
                    'metrica': 'min',
                    'valor_1': ultimos_7_valores[0],
                    'valor_2': ultimos_7_valores[1],
                    'valor_3': ultimos_7_valores[2],
                    'valor_4': ultimos_7_valores[3],
                    'valor_5': ultimos_7_valores[4],
                    'valor_6': ultimos_7_valores[5],
                    'valor_7': ultimos_7_valores[6]
                })
                logger.debug(f"Procesado mínimo para '{nombre_df}': equipo {equipo_minimo}")
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Error al encontrar el valor mínimo en '{nombre_df}': {str(e)}")
                continue
                
        except Exception as e:
            logger.error(f"Error procesando DataFrame '{nombre_df}': {str(e)}")
            continue
    
    # Convertir la lista de resultados en un DataFrame
    if not resultados:
        logger.warning("No se encontraron resultados mínimos para ningún DataFrame")
        return pd.DataFrame()
        
    try:
        df_resultados = pd.DataFrame(resultados)
        logger.info(f"Análisis de mínimos HDD completado: {len(df_resultados)} registros generados")
        return df_resultados
    except Exception as e:
        logger.error(f"Error al crear DataFrame de resultados: {str(e)}")
        return pd.DataFrame()


def encontrar_equipo_mas_inestable(df_dict):
    """Encuentra el equipo más inestable (mayor desviación estándar) en los últimos 7 días para cada DataFrame.
    
    Args:
        df_dict (dict): Diccionario donde las claves son nombres y los valores son DataFrames
        
    Returns:
        pd.DataFrame: DataFrame con información sobre los equipos más inestables
    """
    import logging
    logger = logging.getLogger('hdd_data_analysis')
    
    resultados = []  # Lista para almacenar los resultados como diccionarios
    fecha_ejecucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fecha de ejecución del código
    
    for nombre_df, df in df_dict.items():
        try:
            # Verificar columnas requeridas para HDD
            columnas_requeridas = {'codigo', 'fecha', 'equipo', 'unidad', 'uso'}
            if not columnas_requeridas.issubset(df.columns):
                columnas_faltantes = columnas_requeridas - set(df.columns)
                error_msg = f"El DataFrame '{nombre_df}' no tiene las columnas requeridas. Faltantes: {columnas_faltantes}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            if df.empty:
                logger.warning(f"El DataFrame '{nombre_df}' está vacío.")
                continue
            
            # Crear copia para no modificar el original
            df = df.copy()
            
            # Convertir 'fecha' a tipo datetime y filtrar los últimos 7 días
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
            df = df.dropna(subset=['fecha'])
            
            if df.empty:
                logger.warning(f"El DataFrame '{nombre_df}' quedó vacío después de eliminar fechas inválidas")
                continue
            
            fecha_maxima = df['fecha'].max()
            df_ultimos_7_dias = df[df['fecha'] >= fecha_maxima - timedelta(days=7)]
            
            if df_ultimos_7_dias.empty:
                logger.warning(f"No hay datos en los últimos 7 días para '{nombre_df}'.")
                continue
            
            # Convertir 'uso' a numérico
            df_ultimos_7_dias['uso'] = pd.to_numeric(df_ultimos_7_dias['uso'], errors='coerce')
            df_ultimos_7_dias = df_ultimos_7_dias.dropna(subset=['uso'])
            
            if df_ultimos_7_dias.empty:
                logger.warning(f"El DataFrame '{nombre_df}' quedó vacío después de eliminar valores numéricos inválidos")
                continue
            
            # Calcular desviación estándar por equipo
            try:
                desv_por_equipo = df_ultimos_7_dias.groupby('equipo')['uso'].agg(['std', 'count']).reset_index()
                desv_por_equipo = desv_por_equipo[desv_por_equipo['count'] >= 3]  # Al menos 3 valores para calcular desviación
                
                if desv_por_equipo.empty:
                    logger.warning(f"No hay suficientes datos para calcular inestabilidad en '{nombre_df}'")
                    continue
                
                # Encontrar el equipo con mayor desviación estándar
                idx_max_std = desv_por_equipo['std'].idxmax()
                equipo_inestable = desv_por_equipo.loc[idx_max_std, 'equipo']
                unidad_equipo = df_ultimos_7_dias[df_ultimos_7_dias['equipo'] == equipo_inestable]['unidad'].iloc[0]
                
                # Filtrar los últimos 7 valores de uso de ese equipo
                df_equipo = df_ultimos_7_dias[df_ultimos_7_dias['equipo'] == equipo_inestable].sort_values(by='fecha', ascending=False)
                ultimos_7_valores = df_equipo['uso'].head(7).tolist()  # Obtener los últimos 7 valores de uso
                
                # Si hay menos de 7 valores, rellenar con None
                while len(ultimos_7_valores) < 7:
                    ultimos_7_valores.append(None)
                
                # Agregar resultado a la lista con columnas separadas
                resultados.append({
                    'id': str(uuid.uuid4()),  # Generar un identificador único
                    'unidad': unidad_equipo,
                    'equipo': equipo_inestable,
                    'fecha_ejecucion_del_codigo': fecha_ejecucion,
                    'metrica': 'inestabilidad',
                    'valor_1': ultimos_7_valores[0],
                    'valor_2': ultimos_7_valores[1],
                    'valor_3': ultimos_7_valores[2],
                    'valor_4': ultimos_7_valores[3],
                    'valor_5': ultimos_7_valores[4],
                    'valor_6': ultimos_7_valores[5],
                    'valor_7': ultimos_7_valores[6]
                })
                logger.debug(f"Procesado inestabilidad para '{nombre_df}': equipo {equipo_inestable}")
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Error al calcular inestabilidad en '{nombre_df}': {str(e)}")
                continue
                
        except Exception as e:
            logger.error(f"Error procesando DataFrame '{nombre_df}': {str(e)}")
            continue
    
    # Convertir la lista de resultados en un DataFrame
    if not resultados:
        logger.warning("No se encontraron resultados de inestabilidad para ningún DataFrame")
        return pd.DataFrame()
        
    try:
        df_resultados = pd.DataFrame(resultados)
        logger.info(f"Análisis de inestabilidad HDD completado: {len(df_resultados)} registros generados")
        return df_resultados
    except Exception as e:
        logger.error(f"Error al crear DataFrame de resultados: {str(e)}")
        return pd.DataFrame()


def encontrar_equipo_tasa_cambio(df_dict):
    """Encuentra el equipo con mayor tasa de cambio en los últimos 7 días para cada DataFrame.
    
    Args:
        df_dict (dict): Diccionario donde las claves son nombres y los valores son DataFrames
        
    Returns:
        pd.DataFrame: DataFrame con información sobre los equipos con mayor tasa de cambio
    """
    import logging
    logger = logging.getLogger('hdd_data_analysis')
    
    resultados = []  # Lista para almacenar los resultados como diccionarios
    fecha_ejecucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fecha de ejecución del código
    
    for nombre_df, df in df_dict.items():
        try:
            # Verificar columnas requeridas para HDD
            columnas_requeridas = {'codigo', 'fecha', 'equipo', 'unidad', 'uso'}
            if not columnas_requeridas.issubset(df.columns):
                columnas_faltantes = columnas_requeridas - set(df.columns)
                error_msg = f"El DataFrame '{nombre_df}' no tiene las columnas requeridas. Faltantes: {columnas_faltantes}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            if df.empty:
                logger.warning(f"El DataFrame '{nombre_df}' está vacío.")
                continue
            
            # Crear copia para no modificar el original
            df = df.copy()
            
            # Convertir 'fecha' a tipo datetime y filtrar los últimos 7 días
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
            df = df.dropna(subset=['fecha'])
            
            if df.empty:
                logger.warning(f"El DataFrame '{nombre_df}' quedó vacío después de eliminar fechas inválidas")
                continue
            
            fecha_maxima = df['fecha'].max()
            df_ultimos_7_dias = df[df['fecha'] >= fecha_maxima - timedelta(days=7)]
            
            if df_ultimos_7_dias.empty:
                logger.warning(f"No hay datos en los últimos 7 días para '{nombre_df}'.")
                continue
            
            # Convertir 'uso' a numérico
            df_ultimos_7_dias['uso'] = pd.to_numeric(df_ultimos_7_dias['uso'], errors='coerce')
            df_ultimos_7_dias = df_ultimos_7_dias.dropna(subset=['uso'])
            
            if df_ultimos_7_dias.empty:
                logger.warning(f"El DataFrame '{nombre_df}' quedó vacío después de eliminar valores numéricos inválidos")
                continue
            
            # Calcular tasa de cambio por equipo
            try:
                tasas_cambio = []
                
                for equipo in df_ultimos_7_dias['equipo'].unique():
                    df_equipo = df_ultimos_7_dias[df_ultimos_7_dias['equipo'] == equipo].sort_values('fecha')
                    
                    if len(df_equipo) >= 2:
                        # Calcular diferencia entre el último y primer valor
                        primer_valor = df_equipo['uso'].iloc[0]
                        ultimo_valor = df_equipo['uso'].iloc[-1]
                        tasa_cambio = abs(ultimo_valor - primer_valor)
                        
                        tasas_cambio.append({
                            'equipo': equipo,
                            'tasa_cambio': tasa_cambio,
                            'unidad': df_equipo['unidad'].iloc[0]
                        })
                
                if not tasas_cambio:
                    logger.warning(f"No se pudieron calcular tasas de cambio en '{nombre_df}'")
                    continue
                
                # Encontrar el equipo con mayor tasa de cambio
                df_tasas = pd.DataFrame(tasas_cambio)
                idx_max_tasa = df_tasas['tasa_cambio'].idxmax()
                equipo_max_tasa = df_tasas.loc[idx_max_tasa, 'equipo']
                unidad_equipo = df_tasas.loc[idx_max_tasa, 'unidad']
                
                # Filtrar los últimos 7 valores de uso de ese equipo
                df_equipo = df_ultimos_7_dias[df_ultimos_7_dias['equipo'] == equipo_max_tasa].sort_values(by='fecha', ascending=False)
                ultimos_7_valores = df_equipo['uso'].head(7).tolist()  # Obtener los últimos 7 valores de uso
                
                # Si hay menos de 7 valores, rellenar con None
                while len(ultimos_7_valores) < 7:
                    ultimos_7_valores.append(None)
                
                # Agregar resultado a la lista con columnas separadas
                resultados.append({
                    'id': str(uuid.uuid4()),  # Generar un identificador único
                    'unidad': unidad_equipo,
                    'equipo': equipo_max_tasa,
                    'fecha_ejecucion_del_codigo': fecha_ejecucion,
                    'metrica': 'tasa_cambio',
                    'valor_1': ultimos_7_valores[0],
                    'valor_2': ultimos_7_valores[1],
                    'valor_3': ultimos_7_valores[2],
                    'valor_4': ultimos_7_valores[3],
                    'valor_5': ultimos_7_valores[4],
                    'valor_6': ultimos_7_valores[5],
                    'valor_7': ultimos_7_valores[6]
                })
                logger.debug(f"Procesado tasa de cambio para '{nombre_df}': equipo {equipo_max_tasa}")
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Error al calcular tasa de cambio en '{nombre_df}': {str(e)}")
                continue
                
        except Exception as e:
            logger.error(f"Error procesando DataFrame '{nombre_df}': {str(e)}")
            continue
    
    # Convertir la lista de resultados en un DataFrame
    if not resultados:
        logger.warning("No se encontraron resultados de tasa de cambio para ningún DataFrame")
        return pd.DataFrame()
        
    try:
        df_resultados = pd.DataFrame(resultados)
        logger.info(f"Análisis de tasa de cambio HDD completado: {len(df_resultados)} registros generados")
        return df_resultados
    except Exception as e:
        logger.error(f"Error al crear DataFrame de resultados: {str(e)}")
        return pd.DataFrame()


def hdd_units(df_dict):
    """Función de compatibilidad que retorna un DataFrame vacío (no se usa en HDD análisis).
    
    Args:
        df_dict (dict): Diccionario de DataFrames
        
    Returns:
        pd.DataFrame: DataFrame vacío
    """
    import logging
    logger = logging.getLogger('hdd_data_analysis')
    logger.info("Función hdd_units llamada (no implementada para HDD)")
    return pd.DataFrame()


def hdd_mean_seven_days(df_dict):
    """Calcula el promedio de uso de los últimos 7 días para cada equipo en cada DataFrame.
    
    Args:
        df_dict (dict): Diccionario donde las claves son nombres y los valores son DataFrames
        
    Returns:
        pd.DataFrame: DataFrame con promedios de uso por equipo
    """
    import logging
    logger = logging.getLogger('hdd_data_analysis')
    
    resultados = []  # Lista para almacenar los resultados como diccionarios
    fecha_ejecucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fecha de ejecución del código
    
    for nombre_df, df in df_dict.items():
        try:
            # Verificar columnas requeridas para HDD
            columnas_requeridas = {'codigo', 'fecha', 'equipo', 'unidad', 'uso'}
            if not columnas_requeridas.issubset(df.columns):
                columnas_faltantes = columnas_requeridas - set(df.columns)
                error_msg = f"El DataFrame '{nombre_df}' no tiene las columnas requeridas. Faltantes: {columnas_faltantes}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            if df.empty:
                logger.warning(f"El DataFrame '{nombre_df}' está vacío.")
                continue
            
            # Crear copia para no modificar el original
            df = df.copy()
            
            # Convertir 'fecha' a tipo datetime y filtrar los últimos 7 días
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
            df = df.dropna(subset=['fecha'])
            
            if df.empty:
                logger.warning(f"El DataFrame '{nombre_df}' quedó vacío después de eliminar fechas inválidas")
                continue
            
            fecha_maxima = df['fecha'].max()
            df_ultimos_7_dias = df[df['fecha'] >= fecha_maxima - timedelta(days=7)]
            
            if df_ultimos_7_dias.empty:
                logger.warning(f"No hay datos en los últimos 7 días para '{nombre_df}'.")
                continue
            
            # Convertir 'uso' a numérico
            df_ultimos_7_dias['uso'] = pd.to_numeric(df_ultimos_7_dias['uso'], errors='coerce')
            df_ultimos_7_dias = df_ultimos_7_dias.dropna(subset=['uso'])
            
            if df_ultimos_7_dias.empty:
                logger.warning(f"El DataFrame '{nombre_df}' quedó vacío después de eliminar valores numéricos inválidos")
                continue
            
            # Calcular promedio por equipo
            try:
                promedios_por_equipo = df_ultimos_7_dias.groupby(['equipo', 'unidad'])['uso'].mean().reset_index()
                
                for _, row in promedios_por_equipo.iterrows():
                    # Agregar resultado a la lista
                    resultados.append({
                        'id': str(uuid.uuid4()),  # Generar un identificador único
                        'unidad': row['unidad'],
                        'equipo': row['equipo'],
                        'fecha': fecha_maxima,
                        'promedio_uso': row['uso'],
                        'fecha_ejecucion_del_codigo': fecha_ejecucion
                    })
                
                logger.debug(f"Procesados promedios para '{nombre_df}': {len(promedios_por_equipo)} equipos")
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Error al calcular promedios en '{nombre_df}': {str(e)}")
                continue
                
        except Exception as e:
            logger.error(f"Error procesando DataFrame '{nombre_df}': {str(e)}")
            continue
    
    # Convertir la lista de resultados en un DataFrame
    if not resultados:
        logger.warning("No se encontraron resultados de promedios para ningún DataFrame")
        return pd.DataFrame()
        
    try:
        df_resultados = pd.DataFrame(resultados)
        logger.info(f"Cálculo de promedios HDD completado: {len(df_resultados)} registros generados")
        return df_resultados
    except Exception as e:
        logger.error(f"Error al crear DataFrame de resultados: {str(e)}")
        return pd.DataFrame()


def encontrar_maximo_por_equipo_corregido(df_dict):
    """
    Encuentra el equipo con el valor máximo de uso en los últimos 7 días.
    Cada equipo puede tener una sola métrica asociada a una sola unidad.
    
    Args:
        df_dict (dict): Diccionario donde las claves son nombres y los valores son DataFrames
        
    Returns:
        pd.DataFrame: DataFrame con información sobre el equipo con valor máximo
    """
    import logging
    logger = logging.getLogger('hdd_data_analysis')
    
    resultados = []  # Lista para almacenar los resultados como diccionarios
    fecha_ejecucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fecha de ejecución del código
    
    # Combinar todos los DataFrames en uno solo para análisis global
    df_combinado = pd.concat(df_dict.values(), ignore_index=True)
    
    if df_combinado.empty:
        logger.warning("No hay datos para analizar")
        return pd.DataFrame()
    
    try:
        # Verificar columnas requeridas para HDD
        columnas_requeridas = {'codigo', 'fecha', 'equipo', 'unidad', 'uso'}
        if not columnas_requeridas.issubset(df_combinado.columns):
            columnas_faltantes = columnas_requeridas - set(df_combinado.columns)
            error_msg = f"El DataFrame combinado no tiene las columnas requeridas. Faltantes: {columnas_faltantes}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Crear copia para no modificar el original
        df = df_combinado.copy()
        
        # Convertir 'fecha' a tipo datetime con manejo de errores
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        # Eliminar filas con fechas inválidas
        na_dates = df['fecha'].isna().sum()
        if na_dates > 0:
            logger.warning(f"Se encontraron {na_dates} fechas inválidas que serán ignoradas")
            df = df.dropna(subset=['fecha'])
            
        if df.empty:
            logger.warning("El DataFrame quedó vacío después de eliminar fechas inválidas")
            return pd.DataFrame()
        
        # Convertir 'uso' a numérico
        df['uso'] = pd.to_numeric(df['uso'], errors='coerce')
        na_values = df['uso'].isna().sum()
        if na_values > 0:
            logger.warning(f"Se encontraron {na_values} valores numéricos inválidos que serán ignorados")
            df = df.dropna(subset=['uso'])
        
        if df.empty:
            logger.warning("El DataFrame quedó vacío después de eliminar valores numéricos inválidos")
            return pd.DataFrame()
            
        # Filtrar los últimos 7 días
        fecha_maxima = df['fecha'].max()
        df_ultimos_7_dias = df[df['fecha'] >= fecha_maxima - timedelta(days=7)]
    
        if df_ultimos_7_dias.empty:
            logger.warning("No hay datos en los últimos 7 días")
            return pd.DataFrame()
        
        # Encontrar el equipo con el valor máximo de uso en los últimos 7 días
        try:
            idx_max = df_ultimos_7_dias['uso'].idxmax()
            equipo_maximo = df_ultimos_7_dias.loc[idx_max, 'equipo']
            unidad_equipo = df_ultimos_7_dias.loc[idx_max, 'unidad']
            
            # Filtrar los últimos 7 valores de uso de ese equipo en esa unidad específica
            df_equipo = df_ultimos_7_dias[
                (df_ultimos_7_dias['equipo'] == equipo_maximo) & 
                (df_ultimos_7_dias['unidad'] == unidad_equipo)
            ].sort_values(by='fecha', ascending=False)
            
            if df_equipo.empty:
                logger.warning(f"No se encontraron datos para el equipo {equipo_maximo} en unidad {unidad_equipo}")
                return pd.DataFrame()
                
            ultimos_7_valores = df_equipo['uso'].head(7).tolist()  # Obtener los últimos 7 valores de uso
    
            # Si hay menos de 7 valores, rellenar con None
            while len(ultimos_7_valores) < 7:
                ultimos_7_valores.append(None)
            
            # Agregar resultado a la lista con columnas separadas
            resultados.append({
                'id': str(uuid.uuid4()),  # Generar un identificador único
                'unidad': unidad_equipo,
                'equipo': equipo_maximo,
                'fecha_ejecucion_del_codigo': fecha_ejecucion,
                'metrica': 'max',
                'valor_1': ultimos_7_valores[0],
                'valor_2': ultimos_7_valores[1],
                'valor_3': ultimos_7_valores[2],
                'valor_4': ultimos_7_valores[3],
                'valor_5': ultimos_7_valores[4],
                'valor_6': ultimos_7_valores[5],
                'valor_7': ultimos_7_valores[6]
            })
            logger.info(f"Procesado máximo: equipo {equipo_maximo} en unidad {unidad_equipo}")
            
        except (ValueError, KeyError) as e:
            logger.warning(f"Error al encontrar el valor máximo: {str(e)}")
            return pd.DataFrame()
            
    except Exception as e:
        logger.error(f"Error procesando datos: {str(e)}")
        return pd.DataFrame()
    
    # Convertir la lista de resultados en un DataFrame
    if not resultados:
        logger.warning("No se encontraron resultados máximos")
        return pd.DataFrame()
        
    try:
        df_resultados = pd.DataFrame(resultados)
        logger.info(f"Análisis de máximo HDD completado: {len(df_resultados)} registros generados")
        return df_resultados
    except Exception as e:
        logger.error(f"Error al crear DataFrame de resultados: {str(e)}")
        return pd.DataFrame()


def encontrar_minimo_por_equipo_corregido(df_dict):
    """
    Encuentra el equipo con el valor mínimo de uso en los últimos 7 días.
    Cada equipo puede tener una sola métrica asociada a una sola unidad.
    
    Args:
        df_dict (dict): Diccionario donde las claves son nombres y los valores son DataFrames
        
    Returns:
        pd.DataFrame: DataFrame con información sobre el equipo con valor mínimo
    """
    import logging
    logger = logging.getLogger('hdd_data_analysis')
    
    resultados = []  # Lista para almacenar los resultados como diccionarios
    fecha_ejecucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fecha de ejecución del código
    
    # Combinar todos los DataFrames en uno solo para análisis global
    df_combinado = pd.concat(df_dict.values(), ignore_index=True)
    
    if df_combinado.empty:
        logger.warning("No hay datos para analizar")
        return pd.DataFrame()
    
    try:
        # Verificar columnas requeridas para HDD
        columnas_requeridas = {'codigo', 'fecha', 'equipo', 'unidad', 'uso'}
        if not columnas_requeridas.issubset(df_combinado.columns):
            columnas_faltantes = columnas_requeridas - set(df_combinado.columns)
            error_msg = f"El DataFrame combinado no tiene las columnas requeridas. Faltantes: {columnas_faltantes}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Crear copia para no modificar el original
        df = df_combinado.copy()
        
        # Convertir 'fecha' a tipo datetime y filtrar los últimos 7 días
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        df = df.dropna(subset=['fecha'])
        
        if df.empty:
            logger.warning("El DataFrame quedó vacío después de eliminar fechas inválidas")
            return pd.DataFrame()
        
        fecha_maxima = df['fecha'].max()
        df_ultimos_7_dias = df[df['fecha'] >= fecha_maxima - timedelta(days=7)]
        
        if df_ultimos_7_dias.empty:
            logger.warning("No hay datos en los últimos 7 días")
            return pd.DataFrame()
        
        # Convertir 'uso' a numérico
        df_ultimos_7_dias['uso'] = pd.to_numeric(df_ultimos_7_dias['uso'], errors='coerce')
        df_ultimos_7_dias = df_ultimos_7_dias.dropna(subset=['uso'])
        
        if df_ultimos_7_dias.empty:
            logger.warning("El DataFrame quedó vacío después de eliminar valores numéricos inválidos")
            return pd.DataFrame()
        
        # Encontrar el equipo con el valor mínimo de uso en los últimos 7 días
        try:
            idx_min = df_ultimos_7_dias['uso'].idxmin()
            equipo_minimo = df_ultimos_7_dias.loc[idx_min, 'equipo']
            unidad_equipo = df_ultimos_7_dias.loc[idx_min, 'unidad']
            
            # Filtrar los últimos 7 valores de uso de ese equipo en esa unidad específica
            df_equipo = df_ultimos_7_dias[
                (df_ultimos_7_dias['equipo'] == equipo_minimo) & 
                (df_ultimos_7_dias['unidad'] == unidad_equipo)
            ].sort_values(by='fecha', ascending=False)
            
            if df_equipo.empty:
                logger.warning(f"No se encontraron datos para el equipo {equipo_minimo} en unidad {unidad_equipo}")
                return pd.DataFrame()
                
            ultimos_7_valores = df_equipo['uso'].head(7).tolist()  # Obtener los últimos 7 valores de uso
            
            # Si hay menos de 7 valores, rellenar con None
            while len(ultimos_7_valores) < 7:
                ultimos_7_valores.append(None)
            
            # Agregar resultado a la lista con columnas separadas
            resultados.append({
                'id': str(uuid.uuid4()),  # Generar un identificador único
                'unidad': unidad_equipo,
                'equipo': equipo_minimo,
                'fecha_ejecucion_del_codigo': fecha_ejecucion,
                'metrica': 'min',
                'valor_1': ultimos_7_valores[0],
                'valor_2': ultimos_7_valores[1],
                'valor_3': ultimos_7_valores[2],
                'valor_4': ultimos_7_valores[3],
                'valor_5': ultimos_7_valores[4],
                'valor_6': ultimos_7_valores[5],
                'valor_7': ultimos_7_valores[6]
            })
            logger.info(f"Procesado mínimo: equipo {equipo_minimo} en unidad {unidad_equipo}")
            
        except (ValueError, KeyError) as e:
            logger.warning(f"Error al encontrar el valor mínimo: {str(e)}")
            return pd.DataFrame()
            
    except Exception as e:
        logger.error(f"Error procesando datos: {str(e)}")
        return pd.DataFrame()
    
    # Convertir la lista de resultados en un DataFrame
    if not resultados:
        logger.warning("No se encontraron resultados mínimos")
        return pd.DataFrame()
        
    try:
        df_resultados = pd.DataFrame(resultados)
        logger.info(f"Análisis de mínimo HDD completado: {len(df_resultados)} registros generados")
        return df_resultados
    except Exception as e:
        logger.error(f"Error al crear DataFrame de resultados: {str(e)}")
        return pd.DataFrame()


def encontrar_equipo_mas_inestable_corregido(df_dict):
    """
    Encuentra el equipo más inestable (mayor desviación estándar) en los últimos 7 días.
    Cada equipo puede tener una sola métrica asociada a una sola unidad.
    
    Args:
        df_dict (dict): Diccionario donde las claves son nombres y los valores son DataFrames
        
    Returns:
        pd.DataFrame: DataFrame con información sobre el equipo más inestable
    """
    import logging
    logger = logging.getLogger('hdd_data_analysis')
    
    resultados = []  # Lista para almacenar los resultados como diccionarios
    fecha_ejecucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fecha de ejecución del código
    
    # Combinar todos los DataFrames en uno solo para análisis global
    df_combinado = pd.concat(df_dict.values(), ignore_index=True)
    
    if df_combinado.empty:
        logger.warning("No hay datos para analizar")
        return pd.DataFrame()
    
    try:
        # Verificar columnas requeridas para HDD
        columnas_requeridas = {'codigo', 'fecha', 'equipo', 'unidad', 'uso'}
        if not columnas_requeridas.issubset(df_combinado.columns):
            columnas_faltantes = columnas_requeridas - set(df_combinado.columns)
            error_msg = f"El DataFrame combinado no tiene las columnas requeridas. Faltantes: {columnas_faltantes}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Crear copia para no modificar el original
        df = df_combinado.copy()
        
        # Convertir 'fecha' a tipo datetime y filtrar los últimos 7 días
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        df = df.dropna(subset=['fecha'])
        
        if df.empty:
            logger.warning("El DataFrame quedó vacío después de eliminar fechas inválidas")
            return pd.DataFrame()
        
        fecha_maxima = df['fecha'].max()
        df_ultimos_7_dias = df[df['fecha'] >= fecha_maxima - timedelta(days=7)]
        
        if df_ultimos_7_dias.empty:
            logger.warning("No hay datos en los últimos 7 días")
            return pd.DataFrame()
        
        # Convertir 'uso' a numérico
        df_ultimos_7_dias['uso'] = pd.to_numeric(df_ultimos_7_dias['uso'], errors='coerce')
        df_ultimos_7_dias = df_ultimos_7_dias.dropna(subset=['uso'])
        
        if df_ultimos_7_dias.empty:
            logger.warning("El DataFrame quedó vacío después de eliminar valores numéricos inválidos")
            return pd.DataFrame()
        
        # Calcular desviación estándar por equipo y unidad
        inestabilidad_por_equipo = []
        
        for (equipo, unidad), grupo in df_ultimos_7_dias.groupby(['equipo', 'unidad']):
            if len(grupo) >= 2:  # Necesitamos al menos 2 valores para calcular desviación estándar
                desv_std = grupo['uso'].std()
                inestabilidad_por_equipo.append({
                    'equipo': equipo,
                    'unidad': unidad,
                    'desv_std': desv_std,
                    'datos': grupo
                })
        
        if not inestabilidad_por_equipo:
            logger.warning("No hay suficientes datos para calcular inestabilidad")
            return pd.DataFrame()
        
        # Encontrar el equipo con mayor desviación estándar
        equipo_mas_inestable = max(inestabilidad_por_equipo, key=lambda x: x['desv_std'])
        
        # Obtener los últimos 7 valores del equipo más inestable
        df_equipo = equipo_mas_inestable['datos'].sort_values(by='fecha', ascending=False)
        ultimos_7_valores = df_equipo['uso'].head(7).tolist()
        
        # Si hay menos de 7 valores, rellenar con None
        while len(ultimos_7_valores) < 7:
            ultimos_7_valores.append(None)
        
        # Agregar resultado a la lista
        resultados.append({
            'id': str(uuid.uuid4()),
            'unidad': equipo_mas_inestable['unidad'],
            'equipo': equipo_mas_inestable['equipo'],
            'fecha_ejecucion_del_codigo': fecha_ejecucion,
            'metrica': 'inestabilidad',
            'valor_1': ultimos_7_valores[0],
            'valor_2': ultimos_7_valores[1],
            'valor_3': ultimos_7_valores[2],
            'valor_4': ultimos_7_valores[3],
            'valor_5': ultimos_7_valores[4],
            'valor_6': ultimos_7_valores[5],
            'valor_7': ultimos_7_valores[6]
        })
        
        logger.info(f"Procesado inestabilidad: equipo {equipo_mas_inestable['equipo']} en unidad {equipo_mas_inestable['unidad']}")
        
    except Exception as e:
        logger.error(f"Error procesando datos: {str(e)}")
        return pd.DataFrame()
    
    # Convertir la lista de resultados en un DataFrame
    if not resultados:
        logger.warning("No se encontraron resultados de inestabilidad")
        return pd.DataFrame()
        
    try:
        df_resultados = pd.DataFrame(resultados)
        logger.info(f"Análisis de inestabilidad HDD completado: {len(df_resultados)} registros generados")
        return df_resultados
    except Exception as e:
        logger.error(f"Error al crear DataFrame de resultados: {str(e)}")
        return pd.DataFrame()


def encontrar_equipo_tasa_cambio_corregido(df_dict):
    """
    Encuentra el equipo con mayor tasa de cambio en los últimos 7 días.
    Cada equipo puede tener una sola métrica asociada a una sola unidad.
    
    Args:
        df_dict (dict): Diccionario donde las claves son nombres y los valores son DataFrames
        
    Returns:
        pd.DataFrame: DataFrame con información sobre el equipo con mayor tasa de cambio
    """
    import logging
    logger = logging.getLogger('hdd_data_analysis')
    
    resultados = []  # Lista para almacenar los resultados como diccionarios
    fecha_ejecucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fecha de ejecución del código
    
    # Combinar todos los DataFrames en uno solo para análisis global
    df_combinado = pd.concat(df_dict.values(), ignore_index=True)
    
    if df_combinado.empty:
        logger.warning("No hay datos para analizar")
        return pd.DataFrame()
    
    try:
        # Verificar columnas requeridas para HDD
        columnas_requeridas = {'codigo', 'fecha', 'equipo', 'unidad', 'uso'}
        if not columnas_requeridas.issubset(df_combinado.columns):
            columnas_faltantes = columnas_requeridas - set(df_combinado.columns)
            error_msg = f"El DataFrame combinado no tiene las columnas requeridas. Faltantes: {columnas_faltantes}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Crear copia para no modificar el original
        df = df_combinado.copy()
        
        # Convertir 'fecha' a tipo datetime y filtrar los últimos 7 días
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        df = df.dropna(subset=['fecha'])
        
        if df.empty:
            logger.warning("El DataFrame quedó vacío después de eliminar fechas inválidas")
            return pd.DataFrame()
        
        fecha_maxima = df['fecha'].max()
        df_ultimos_7_dias = df[df['fecha'] >= fecha_maxima - timedelta(days=7)]
        
        if df_ultimos_7_dias.empty:
            logger.warning("No hay datos en los últimos 7 días")
            return pd.DataFrame()
        
        # Convertir 'uso' a numérico
        df_ultimos_7_dias['uso'] = pd.to_numeric(df_ultimos_7_dias['uso'], errors='coerce')
        df_ultimos_7_dias = df_ultimos_7_dias.dropna(subset=['uso'])
        
        if df_ultimos_7_dias.empty:
            logger.warning("El DataFrame quedó vacío después de eliminar valores numéricos inválidos")
            return pd.DataFrame()
        
        # Calcular tasa de cambio por equipo y unidad
        tasa_cambio_por_equipo = []
        
        for (equipo, unidad), grupo in df_ultimos_7_dias.groupby(['equipo', 'unidad']):
            if len(grupo) >= 2:  # Necesitamos al menos 2 valores para calcular tasa de cambio
                grupo_ordenado = grupo.sort_values('fecha')
                valores = grupo_ordenado['uso'].tolist()
                
                # Calcular tasa de cambio promedio
                tasas_cambio = []
                for i in range(1, len(valores)):
                    cambio = abs(valores[i] - valores[i-1])
                    tasas_cambio.append(cambio)
                
                if tasas_cambio:
                    tasa_promedio = sum(tasas_cambio) / len(tasas_cambio)
                    tasa_cambio_por_equipo.append({
                        'equipo': equipo,
                        'unidad': unidad,
                        'tasa_cambio': tasa_promedio,
                        'datos': grupo_ordenado
                    })
        
        if not tasa_cambio_por_equipo:
            logger.warning("No hay suficientes datos para calcular tasa de cambio")
            return pd.DataFrame()
        
        # Encontrar el equipo con mayor tasa de cambio
        equipo_mayor_tasa = max(tasa_cambio_por_equipo, key=lambda x: x['tasa_cambio'])
        
        # Obtener los últimos 7 valores del equipo con mayor tasa de cambio
        df_equipo = equipo_mayor_tasa['datos'].sort_values(by='fecha', ascending=False)
        ultimos_7_valores = df_equipo['uso'].head(7).tolist()
        
        # Si hay menos de 7 valores, rellenar con None
        while len(ultimos_7_valores) < 7:
            ultimos_7_valores.append(None)
        
        # Agregar resultado a la lista
        resultados.append({
            'id': str(uuid.uuid4()),
            'unidad': equipo_mayor_tasa['unidad'],
            'equipo': equipo_mayor_tasa['equipo'],
            'fecha_ejecucion_del_codigo': fecha_ejecucion,
            'metrica': 'tasa_cambio',
            'valor_1': ultimos_7_valores[0],
            'valor_2': ultimos_7_valores[1],
            'valor_3': ultimos_7_valores[2],
            'valor_4': ultimos_7_valores[3],
            'valor_5': ultimos_7_valores[4],
            'valor_6': ultimos_7_valores[5],
            'valor_7': ultimos_7_valores[6]
        })
        
        logger.info(f"Procesado tasa de cambio: equipo {equipo_mayor_tasa['equipo']} en unidad {equipo_mayor_tasa['unidad']}")
        
    except Exception as e:
        logger.error(f"Error procesando datos: {str(e)}")
        return pd.DataFrame()
    
    # Convertir la lista de resultados en un DataFrame
    if not resultados:
        logger.warning("No se encontraron resultados de tasa de cambio")
        return pd.DataFrame()
        
    try:
        df_resultados = pd.DataFrame(resultados)
        logger.info(f"Análisis de tasa de cambio HDD completado: {len(df_resultados)} registros generados")
        return df_resultados
    except Exception as e:
        logger.error(f"Error al crear DataFrame de resultados: {str(e)}")
        return pd.DataFrame() 