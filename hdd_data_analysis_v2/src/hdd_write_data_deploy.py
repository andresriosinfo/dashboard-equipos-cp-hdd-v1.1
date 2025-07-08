#!/usr/bin/env python
# coding: utf-8

from sqlalchemy import create_engine
import pandas as pd
import time
import json
from sqlalchemy.exc import SQLAlchemyError, DBAPIError, OperationalError

# Import new components
from hdd_config_manager import get_config
from hdd_log_manager import get_log_manager, time_execution
from hdd_db_manager import get_db_manager
from hdd_batch_processor import get_batch_processor

import logging
logger = logging.getLogger('hdd_data_analysis')

@time_execution('db_write')
def save_data_to_sql(df1, df2):
    """
    Guarda dos DataFrames en las tablas de resultados HDD de la base de datos SQL Server.
    
    Parámetros:
    df1 (pd.DataFrame): Primer DataFrame a guardar en hdd_an_resultados.
    df2 (pd.DataFrame): Segundo DataFrame a guardar en hdd_an_resultados_promedios.
    
    Raises:
        TypeError: Si df1 o df2 no son DataFrames válidos
        ValueError: Si faltan parámetros de conexión
        Exception: Cualquier error durante la conexión o guardado
    """
    try:
        # Get database manager
        db_manager = get_db_manager()
        
        # Get batch processor for large datasets
        batch_processor = get_batch_processor()
        
        # Validate input DataFrames
        if not isinstance(df1, pd.DataFrame) or not isinstance(df2, pd.DataFrame):
            raise TypeError("Los argumentos df1 y df2 deben ser DataFrames válidos")
            
        if df1.empty and df2.empty:
            logger.warning("Los DataFrames de entrada están vacíos, no hay datos para guardar")
            return
        
        # Get table names from configuration or use defaults for HDD
        table1 = get_config('tabla_resultados', 'hdd_an_resultados')
        table2 = get_config('tabla_promedios', 'hdd_an_resultados_promedios')
        
        # Save results using the database manager
        logger.info("Guardando resultados HDD en la base de datos...")
        
        # Save first DataFrame if not empty
        if not df1.empty:
            # Save to HDD results table
            logger.info(f"Guardando {len(df1)} registros en la tabla HDD {table1}")
            db_manager.save_results(df1, 'analisis')
        else:
            logger.warning(f"El DataFrame df1 está vacío, no se guardará")
        
        # Save second DataFrame if not empty
        if not df2.empty:
            # Save to HDD averages table
            logger.info(f"Guardando {len(df2)} registros en la tabla HDD {table2}")
            db_manager.save_results(df2, 'promedios')
        else:
            logger.warning(f"El DataFrame df2 está vacío, no se guardará")
            
        # Update metadata about the save operation
        if db_manager.is_connected:
            stats = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'records_df1': len(df1) if not df1.empty else 0,
                'records_df2': len(df2) if not df2.empty else 0,
                'tables': [table1, table2]
            }
            db_manager.set_metadata('stats', 'last_hdd_data_save', 
                                  json.dumps(stats), 
                                  'Last time HDD data was saved to the database')
        
        logger.info(f"Datos HDD guardados exitosamente")
        print(f"Datos HDD guardados en {table1} y {table2}")
        
    except Exception as e:
        logger.error(f"Error al guardar datos HDD en la base de datos: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise


@time_execution('db_write')
def _save_to_legacy_table(df, table_name, batch_size=None):
    """
    Save data to a legacy table using batch processing.
    
    Args:
        df: DataFrame to save
        table_name: Name of the target table
        batch_size: Size of batches for processing (default: from config)
    """
    if df.empty:
        logger.warning(f"DataFrame vacío, no se guardará en {table_name}")
        return
    
    try:
        # Get connection parameters from config
        from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
        
        host = DB_HOST
        port = DB_PORT
        db_name = DB_NAME
        user = DB_USER
        password = DB_PASSWORD
        
        # Validate connection configuration
        if not all([host, port, db_name, user, password]):
            raise ValueError("Faltan parámetros de conexión a la base de datos")
        
        # Create connection string
        connection_str = f'mssql+pyodbc://{user}:{password}@{host}:{port}/{db_name}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes'
        
        # Get batch size from config or use default
        if batch_size is None:
            batch_size = get_config('tamano_lote_escritura', 1000)
        
        # Create engine
        engine = create_engine(connection_str, connect_args={'timeout': 30})
        
        # Get batch processor
        batch_processor = get_batch_processor(batch_size=batch_size)
        
        # Define batch processing function
        def _save_batch(batch_df):
            try:
                logger.debug(f"Guardando lote de {len(batch_df)} registros en {table_name}")
                batch_df.to_sql(table_name, con=engine, if_exists='append', index=False)
                return len(batch_df)
            except Exception as e:
                logger.error(f"Error guardando lote en {table_name}: {str(e)}")
                raise
        
        # Check if table exists, if it does, truncate it
        with engine.connect() as connection:
            # Check if table exists
            try:
                connection.execute(f"SELECT TOP 1 * FROM {table_name}")
                # Table exists, truncate it
                connection.execute(f"TRUNCATE TABLE {table_name}")
                logger.info(f"Tabla {table_name} truncada")
            except:
                # Table doesn't exist, it will be created by to_sql
                logger.info(f"Tabla {table_name} no existe, se creará")
        
        # Process in batches
        total_rows = len(df)
        batch_count = (total_rows + batch_size - 1) // batch_size
        logger.info(f"Guardando {total_rows} registros en {batch_count} lotes en {table_name}")
        
        for i in range(batch_count):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, total_rows)
            batch_df = df.iloc[start_idx:end_idx].copy()
            
            # For the first batch, use replace to create/replace the table
            if_exists = 'replace' if i == 0 else 'append'
            
            logger.debug(f"Guardando lote {i+1}/{batch_count} ({start_idx}:{end_idx}) en {table_name}")
            batch_df.to_sql(table_name, con=engine, if_exists=if_exists, index=False)
        
        logger.info(f"Guardados {total_rows} registros en {table_name} exitosamente")
        
    except Exception as e:
        logger.error(f"Error guardando en tabla legacy {table_name}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc()) 