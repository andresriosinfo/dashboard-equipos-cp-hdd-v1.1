#!/usr/bin/env python
# coding: utf-8

from sqlalchemy import create_engine
import pandas as pd
import time
from sqlalchemy.exc import SQLAlchemyError, DBAPIError, OperationalError
from sqlalchemy.sql import text

# Import new components
from hdd_config_manager import get_config
from hdd_log_manager import get_log_manager, time_execution
from hdd_db_manager import get_db_manager

import logging
logger = logging.getLogger('hdd_data_analysis')

@time_execution('db_query')
def upload_data_sql():
    """
    Establece conexión con SQL Server y ejecuta una consulta para obtener datos de HDD.
    
    Retorna:
    dict: Diccionario de DataFrames agrupados por unidad
    """
    try:
        # Get database manager
        db_manager = get_db_manager()
        
        # Get configuration
        host = get_config('DB_HOST', '')
        port = get_config('DB_PORT', '')
        db_name = get_config('DB_NAME', '')
        user = get_config('DB_USER', '')
        password = get_config('DB_PASSWORD', '')
        
        # If configuration is not available in the database, fall back to config.py
        if not all([host, port, db_name, user, password]):
            from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
            host = DB_HOST
            port = DB_PORT
            db_name = DB_NAME
            user = DB_USER
            password = DB_PASSWORD
        
        # Get the query from configuration or use default for HDD
        query = get_config('query_datos', "SELECT * FROM dbo.nv_hdd_history")
        
        # Validate connection configuration
        if not all([host, port, db_name, user, password]):
            raise ValueError("Faltan parámetros de conexión a la base de datos")
            
        logger.info(f"Conectando a la base de datos {db_name} en {host}:{port} para datos HDD")
        connection_str = f'mssql+pyodbc://{user}:{password}@{host}:{port}/{db_name}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes'
        
        # Get connection parameters
        connection_timeout = get_config('timeout_db', 30)  # seconds
        max_retries = get_config('max_reintentos', 3)
        retry_interval = get_config('intervalo_reintento', 2)  # seconds
        
        # Try to connect with timeout and retries
        start_time = time.time()
        retry_count = 0
        
        while retry_count < max_retries and time.time() - start_time < connection_timeout:
            try:
                engine = create_engine(connection_str, connect_args={'timeout': 10})
                # Verify connection
                with engine.connect() as conn:
                    logger.info("Conexión a la base de datos establecida con éxito para HDD")
                    break
            except (SQLAlchemyError, OperationalError, DBAPIError) as e:
                retry_count += 1
                if retry_count >= max_retries or time.time() - start_time >= connection_timeout:
                    logger.error(f"Timeout al conectar a la base de datos después de {retry_count} intentos: {str(e)}")
                    raise
                logger.warning(f"Reintentando conexión (intento {retry_count}/{max_retries}, {int(time.time() - start_time)}s): {str(e)}")
                time.sleep(retry_interval)
        
        # Execute the query
        logger.info(f"Ejecutando consulta SQL para HDD: {query}")
        
        # Record query start time for performance logging
        query_start_time = time.time()
        
        # Use batched query execution if the data might be large
        if get_config('usar_batch_query', True):
            # Use database manager to execute the query
            data = db_manager.execute_query(query)
            if data:
                df = pd.DataFrame(data)
            else:
                logger.warning("La consulta no devolvió resultados")
                df = pd.DataFrame()
        else:
            # Direct query execution
            df = pd.read_sql(query, con=engine)
        
        # Record query duration
        query_duration = time.time() - query_start_time
        logger.info(f"Consulta SQL completada en {query_duration:.2f}s")
        
        # Verify results
        if df.empty:
            logger.warning("La consulta no devolvió resultados")
            return {}
        else:
            logger.info(f"Datos HDD obtenidos: {len(df)} filas, {len(df.columns)} columnas")
            
        # Verify data types and handle nulls
        for col in df.columns:
            na_count = df[col].isna().sum()
            if na_count > 0:
                logger.warning(f"La columna '{col}' contiene {na_count} valores nulos")
            
        # Create dictionary of DataFrames by unidad (instead of area for HDD)
        df_dict = {}
        
        # Use the configured grouping column or default to 'unidad' for HDD
        grouping_col = get_config('columna_agrupacion', 'unidad')
        
        if grouping_col not in df.columns:
            logger.error(f"La columna de agrupación '{grouping_col}' no existe en los datos HDD")
            # Fall back to unidad if it exists
            if 'unidad' in df.columns:
                grouping_col = 'unidad'
                logger.info(f"Usando 'unidad' como columna de agrupación por defecto para HDD")
            else:
                logger.error("No se puede agrupar los datos HDD, no hay columna de agrupación válida")
                # Return a single DataFrame with all data
                df_dict['df_all'] = df
                return df_dict
        
        # Group by the specified column
        for variable in df[grouping_col].unique():
            df_dict[f"df_{variable}"] = df[df[grouping_col] == variable]
            logger.debug(f"DataFrame HDD 'df_{variable}' creado con {len(df_dict[f'df_{variable}'])} filas")

        # Update metadata about the data fetch
        if db_manager.is_connected:
            db_manager.set_metadata('stats', 'last_hdd_data_fetch', 
                                  time.strftime('%Y-%m-%d %H:%M:%S'),
                                  'Last time HDD data was fetched from the source database')
        
        return df_dict
        
    except Exception as e:
        logger.error(f"Error al obtener datos HDD de SQL Server: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {} 