#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
import logging
import schedule
import traceback
import pandas as pd
from datetime import datetime

# Import the new HDD components
from hdd_config_manager import get_config, get_config_manager
from hdd_log_manager import get_log_manager, setup_logging, time_execution
from hdd_db_manager import get_db_manager
from hdd_batch_processor import get_batch_processor, get_parallel_processor

# Initialize configuration manager
config_manager = get_config_manager()

# Initialize log manager and setup logging
log_manager = get_log_manager()
logger = setup_logging(console=True, file=True, db=False)
logger.info(f"Iniciando aplicación HDD con nivel de log: {get_config('nivel_log', 'INFO')}")

# Initialize database manager
db_manager = get_db_manager()

# Get schedule hour from configuration
SCHEDULE_HOUR = get_config('hora_ejecucion', "02:00")

# Import custom modules with error handling
try:
    from hdd_functions_deploy import hdd_units, hdd_mean_seven_days
    from hdd_upload_data_deploy import upload_data_sql
    from hdd_write_data_deploy import save_data_to_sql
    logger.info("Successfully imported all HDD modules")
except ImportError as e:
    logger.error(f"Failed to import required HDD modules: {str(e)}")
    sys.exit(1)

@time_execution('ejecutar_tareas_diarias_hdd')
def ejecutar_tareas_diarias():
    """
    Execute the daily HDD data analysis tasks:
    1. Fetch HDD data from SQL Server
    2. Analyze the data to find HDD metrics
    3. Save results back to the database
    
    Returns:
        bool: True if execution was successful, False otherwise
    """
    start_time = time.time()
    success = False
    
    # Generate a unique execution ID
    execution_id = log_manager.get_execution_id()
    
    try:
        logger.info("==========================================")
        logger.info("INICIANDO CICLO DE ANÁLISIS DE DATOS HDD")
        logger.info(f"ID de ejecución: {execution_id}")
        logger.info(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("==========================================")
        
        # Step 1: Fetch HDD data from SQL Server using batch processing
        logger.info("PASO 1: Obteniendo datos HDD de SQL Server...")
        try:
            # Get batch processor
            batch_processor = get_batch_processor()
            
            # Connect to database and fetch HDD data
            df_dict = upload_data_sql()
            if not df_dict:
                logger.error("No se obtuvieron datos HDD de SQL Server (diccionario vacío)")
                return False
                
            logger.info(f"Datos HDD obtenidos exitosamente: {len(df_dict)} DataFrames")
            for name, df in df_dict.items():
                logger.info(f"  - {name}: {len(df)} filas, {len(df.columns)} columnas")
                
            # Apply data validation and preprocessing in batches
            logger.info("Validando y preprocesando datos HDD...")
            for name, df in df_dict.items():
                # Validate required columns for HDD
                required_columns = {'codigo', 'fecha', 'equipo', 'unidad', 'uso'}
                if not required_columns.issubset(df.columns):
                    missing_cols = required_columns - set(df.columns)
                    logger.error(f"DataFrame '{name}' no tiene todas las columnas requeridas para HDD. Faltantes: {missing_cols}")
                    continue
                
                # Process in batches
                df_dict[name] = batch_processor.process_dataframe_in_batches(
                    df, 
                    _preprocess_dataframe_hdd,
                    dias_analisis=get_config('dias_analisis', 7),
                    umbral_maximo=get_config('umbral_maximo', 100.0),
                    umbral_minimo=get_config('umbral_minimo', 0.0)
                )
                
                logger.info(f"DataFrame HDD '{name}' preprocesado: {len(df_dict[name])} filas válidas")
                
        except Exception as e:
            logger.error(f"ERROR en el paso 1 (obtención de datos HDD): {str(e)}")
            logger.error(traceback.format_exc())
            return False
        
        # Step 2: Analyze HDD data using parallel processing
        logger.info("PASO 2: Analizando datos HDD...")
        try:
            # Get parallel processor
            parallel_processor = get_parallel_processor()
            
            # Get analysis parameters
            analysis_params = get_config('parametros_analisis', 
                                        {'max': True, 'min': True, 'inestabilidad': True, 'tasa_cambio': True})
            
            # Create tasks for parallel execution
            analysis_tasks = []
            
            if analysis_params.get('max', True):
                from hdd_functions_deploy import encontrar_maximo_por_equipo_corregido
                analysis_tasks.append((encontrar_maximo_por_equipo_corregido, (df_dict,), {}))
            
            if analysis_params.get('min', True):
                from hdd_functions_deploy import encontrar_minimo_por_equipo_corregido
                analysis_tasks.append((encontrar_minimo_por_equipo_corregido, (df_dict,), {}))
            
            if analysis_params.get('inestabilidad', True):
                from hdd_functions_deploy import encontrar_equipo_mas_inestable_corregido
                analysis_tasks.append((encontrar_equipo_mas_inestable_corregido, (df_dict,), {}))
            
            if analysis_params.get('tasa_cambio', True):
                from hdd_functions_deploy import encontrar_equipo_tasa_cambio_corregido
                analysis_tasks.append((encontrar_equipo_tasa_cambio_corregido, (df_dict,), {}))
            
            # Execute analysis tasks in parallel
            logger.info(f"Ejecutando {len(analysis_tasks)} tareas de análisis HDD en paralelo...")
            analysis_results = parallel_processor.execute_parallel(analysis_tasks)
            
            # Combine results
            logger.info("Combinando resultados de análisis HDD...")
            valid_results = [result for result in analysis_results if result is not None and not result.empty]
            
            if valid_results:
                df_final = pd.concat(valid_results, ignore_index=True)
                logger.info(f"Análisis de equipos HDD completado: {len(df_final)} registros")
            else:
                df_final = pd.DataFrame()
                logger.warning("El análisis de equipos HDD no generó resultados")
            
            # Calculate daily averages for HDD
            logger.info("Calculando promedios diarios HDD...")
            df_mean = hdd_mean_seven_days(df_dict)
            
            if df_mean.empty:
                logger.warning("El cálculo de promedios HDD no generó resultados")
            else:
                logger.info(f"Cálculo de promedios HDD completado: {len(df_mean)} registros")
                
            # Verify if both results are empty
            if df_final.empty and df_mean.empty:
                logger.error("No se generaron resultados en ninguno de los análisis HDD")
                return False
                
        except Exception as e:
            logger.error(f"ERROR en el paso 2 (análisis de datos HDD): {str(e)}")
            logger.error(traceback.format_exc())
            return False
        
        # Step 3: Save HDD results to database using the database manager
        logger.info("PASO 3: Guardando resultados HDD en SQL Server...")
        try:
            # Save analysis results
            if not df_final.empty:
                db_manager.save_results(df_final, 'analisis')
            
            # Save average results
            if not df_mean.empty:
                db_manager.save_results(df_mean, 'promedios')
                
            logger.info("Resultados HDD guardados exitosamente en la base de datos")
            
            # Clean up old logs if configured
            if get_config('auto_limpiar_logs', False):
                dias_retencion = get_config('dias_retencion_logs', 30)
                log_manager.clean_old_logs(dias_retencion)
                logger.info(f"Logs antiguos limpiados (retención: {dias_retencion} días)")
                
        except Exception as e:
            logger.error(f"ERROR en el paso 3 (guardado de resultados HDD): {str(e)}")
            logger.error(traceback.format_exc())
            return False
        
        # All tasks completed successfully
        elapsed_time = time.time() - start_time
        logger.info("==========================================")
        logger.info(f"TAREAS HDD COMPLETADAS EXITOSAMENTE en {elapsed_time:.2f} segundos")
        logger.info("==========================================")
        success = True
        
    except Exception as e:
        logger.error("==========================================")
        logger.error(f"ERROR GENERAL EN LA EJECUCIÓN HDD: {str(e)}")
        logger.error(traceback.format_exc())
        logger.error("==========================================")
        
    finally:
        return success


def _preprocess_dataframe_hdd(df, dias_analisis=7, umbral_maximo=100.0, umbral_minimo=0.0):
    """
    Preprocess a DataFrame for HDD analysis.
    
    Args:
        df: DataFrame to process
        dias_analisis: Number of days to analyze
        umbral_maximo: Maximum threshold for usage values
        umbral_minimo: Minimum threshold for usage values
    
    Returns:
        Preprocessed DataFrame
    """
    try:
        # Create a copy to avoid modifying the original
        df = df.copy()
        
        # Convert data types for HDD
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        df['uso'] = pd.to_numeric(df['uso'], errors='coerce')
        
        # Remove rows with invalid dates or usage values
        df = df.dropna(subset=['fecha', 'uso'])
        
        # Filter by date range
        fecha_maxima = df['fecha'].max()
        df = df[df['fecha'] >= fecha_maxima - pd.Timedelta(days=dias_analisis)]
        
        # Filter by usage thresholds
        df = df[(df['uso'] >= umbral_minimo) & (df['uso'] <= umbral_maximo)]
        
        return df
        
    except Exception as e:
        logger.error(f"Error preprocessing HDD DataFrame: {str(e)}")
        # Return the original DataFrame if there's an error
        return df

def job_function():
    """
    Wrapper function to handle any exceptions from the scheduled job
    
    Returns:
        bool: True if execution was successful, False otherwise
    """
    success = False
    try:
        # Ejecutar las tareas diarias y capturar el resultado
        success = ejecutar_tareas_diarias()
        
        # Registrar el resultado en el log
        if success:
            logger.info("Ejecución programada HDD completada exitosamente")
        else:
            logger.warning("Ejecución programada HDD completada con errores")
            
        return success
        
    except Exception as e:
        logger.error(f"Error fatal en job_function HDD: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def run_once():
    """Run the HDD analysis once immediately"""
    logger.info("Ejecutando análisis HDD una vez...")
    job_function()

def run_scheduled():
    """Run the HDD analysis on a schedule (using time from config file)"""
    logger.info("Iniciando ejecución programada HDD...")
    
    # Configurar señales para manejar interrupciones (solo en plataformas Unix)
    import signal
    import platform
    
    def signal_handler(sig, frame):
        logger.info(f"Recibida señal {sig}. Deteniendo el programa HDD...")
        sys.exit(0)
    
    # Configurar manejadores de señales en sistemas Unix
    if platform.system() != 'Windows':
        signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
        signal.signal(signal.SIGTERM, signal_handler) # Señal de terminación
        logger.info("Manejadores de señales configurados para HDD")
    
    # Configurar el trabajo programado
    try:
        # Schedule the job to run daily at configured time
        schedule.every().day.at(SCHEDULE_HOUR).do(job_function)
        logger.info(f"Scheduler HDD iniciado. Tareas programadas para ejecutarse a las {SCHEDULE_HOUR} diariamente.")
        
        # Registrar la hora de la próxima ejecución
        next_run = schedule.next_run()
        if next_run:
            time_until = next_run - datetime.now()
            hours, remainder = divmod(time_until.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            logger.info(f"Próxima ejecución HDD: {next_run.strftime('%Y-%m-%d %H:%M:%S')} "
                      f"(en {hours}h {minutes}m {seconds}s)")
    
        # Variables para manejar errores consecutivos
        error_count = 0
        max_consecutive_errors = 5
        last_successful_check = time.time()
        
        # Keep the script running to allow scheduled tasks to execute
        while True:
            try:
                # Ejecutar tareas pendientes
                schedule.run_pending()
                
                # Si llegamos aquí, resetear contador de errores
                if error_count > 0:
                    logger.info(f"Scheduler HDD recuperado después de {error_count} errores")
                    error_count = 0
                
                # Actualizar tiempo de última verificación exitosa
                last_successful_check = time.time()
                
                # Dormir menos tiempo para mejor respuesta
                time.sleep(30)  # Verificar cada 30 segundos
                
                # Periódicamente mostrar información de la próxima ejecución (cada hora)
                if int(time.time()) % 3600 < 30:  # En los primeros 30 segundos de cada hora
                    next_run = schedule.next_run()
                    if next_run:
                        time_until = next_run - datetime.now()
                        hours, remainder = divmod(time_until.seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        logger.info(f"Próxima ejecución HDD: {next_run.strftime('%Y-%m-%d %H:%M:%S')} "
                                  f"(en {hours}h {minutes}m {seconds}s)")
                
            except KeyboardInterrupt:
                logger.info("Programa HDD detenido por el usuario")
                break
                
            except Exception as e:
                error_count += 1
                logger.error(f"Error en el scheduler HDD (#{error_count}): {str(e)}")
                logger.error(traceback.format_exc())
                
                # Si hay demasiados errores consecutivos, reiniciar el scheduler
                if error_count >= max_consecutive_errors:
                    logger.critical(f"Demasiados errores consecutivos HDD ({error_count}). Reiniciando scheduler...")
                    
                    # Limpiar tareas programadas y reprogramar
                    schedule.clear()
                    schedule.every().day.at(SCHEDULE_HOUR).do(job_function)
                    error_count = 0
                    logger.info("Scheduler HDD reiniciado")
                
                # Verificar si ha pasado demasiado tiempo desde la última verificación exitosa
                if time.time() - last_successful_check > 3600:  # 1 hora
                    logger.critical("No se ha podido ejecutar el scheduler HDD por más de 1 hora. Reiniciando...")
                    schedule.clear()
                    schedule.every().day.at(SCHEDULE_HOUR).do(job_function)
                    last_successful_check = time.time()
                    logger.info("Scheduler HDD reiniciado después de inactividad prolongada")
                
                # Esperar menos tiempo en caso de error para recuperarse más rápido
                time.sleep(30)
                
    except Exception as e:
        logger.critical(f"Error fatal en el scheduler HDD: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='HDD Data Analysis Application')
    parser.add_argument('--run-once', action='store_true', help='Run the HDD analysis once and exit')
    parser.add_argument('--schedule', action='store_true', help='Run on schedule (daily at 2:00 AM)')
    
    args = parser.parse_args()
    
    if args.run_once:
        run_once()
    elif args.schedule:
        run_scheduled()
    else:
        # Default behavior if no arguments provided
        logger.info("No se especificó modo de ejecución HDD. Use --run-once o --schedule.")
        parser.print_help() 