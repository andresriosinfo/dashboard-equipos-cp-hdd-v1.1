#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejecutar Ranking HDD Real - Script para generar rankings con datos reales
=======================================================================

Este script ejecuta el análisis de ranking de unidades de disco duro usando
datos reales de la tabla nv_hdd_history y guarda los resultados en
nv_hdd_analisis_datos_v2.

Autor: Sistema de Análisis HDD
Fecha: 2025
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ranking_hdd_real.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('ranking_hdd_real')

# Importar módulos del proyecto
from hdd_upload_data_deploy import upload_data_sql
from hdd_ranking_functions import generar_ranking_completo
from hdd_db_manager import get_db_manager

def ejecutar_ranking_hdd_real():
    """Ejecuta el análisis de ranking HDD con datos reales."""
    try:
        logger.info("=" * 80)
        logger.info("INICIANDO ANÁLISIS DE RANKING HDD CON DATOS REALES")
        logger.info("=" * 80)
        
        # Cargar datos reales
        logger.info("Cargando datos reales de HDD desde nv_hdd_history...")
        datos_dict = upload_data_sql()
        
        if not datos_dict:
            logger.error("No se pudieron cargar datos de HDD")
            return False
        
        # Combinar todos los DataFrames en uno solo para el análisis
        datos_list = []
        for key, df in datos_dict.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                datos_list.append(df)
        
        if not datos_list:
            logger.error("No hay DataFrames válidos en los datos cargados")
            return False
        
        datos = pd.concat(datos_list, ignore_index=True)
        
        logger.info(f"Datos HDD cargados exitosamente: {len(datos)} registros")
        logger.info(f"Columnas disponibles: {list(datos.columns)}")
        
        # Información básica de los datos
        logger.info(f"Rango de fechas: {datos['fecha'].min()} a {datos['fecha'].max()}")
        logger.info(f"Unidades únicas: {datos['unidad'].nunique()}")
        logger.info(f"Equipos únicos: {datos['equipo'].nunique()}")
        
        # Generar rankings usando la nueva estructura
        logger.info("Generando rankings de HDD...")
        df_ranking_completo = generar_ranking_completo(datos_dict)
        
        if df_ranking_completo.empty:
            logger.error("No se pudieron generar rankings")
            return False
        
        # Obtener manager de base de datos
        db_manager = get_db_manager()
        
        # Guardar rankings en la base de datos
        logger.info("Guardando rankings en la base de datos...")
        
        # Preparar rankings en formato de diccionario por tipo
        rankings_dict = {}
        for metrica in df_ranking_completo['metrica'].unique():
            df_metrica = df_ranking_completo[df_ranking_completo['metrica'] == metrica].copy()
            rankings_dict[metrica] = df_metrica
        
        # Usar el método guardar_rankings que guarda en nv_hdd_analisis_datos_v2
        if db_manager.guardar_rankings(rankings_dict):
            logger.info("Rankings guardados exitosamente en nv_hdd_analisis_datos_v2")
        else:
            logger.error("Error guardando rankings en la base de datos")
            return False
        
        # Mostrar resumen de resultados
        logger.info("=" * 80)
        logger.info("RESULTADOS DE RANKINGS HDD")
        logger.info("=" * 80)
        
        # Resumen por métrica
        metricas = df_ranking_completo['metrica'].unique()
        for metrica in metricas:
            df_metrica = df_ranking_completo[df_ranking_completo['metrica'] == metrica]
            logger.info(f"\n{metrica.upper()}:")
            logger.info("-" * 50)
            
            # Top 5
            for _, row in df_metrica.head(5).iterrows():
                logger.info(f"  {row['posicion']:3d}. Equipo {str(row['equipo']):>4s} - {row['unidad']:3s} - Valor: {row['valor_metrico']:8.4f}")
            
            logger.info("  ...")
            
            # Bottom 5
            for _, row in df_metrica.tail(5).iterrows():
                logger.info(f"  {row['posicion']:3d}. Equipo {str(row['equipo']):>4s} - {row['unidad']:3s} - Valor: {row['valor_metrico']:8.4f}")
        
        # Verificar datos guardados en la base de datos
        logger.info("Verificando datos guardados en la base de datos...")
        
        # Obtener rankings guardados usando el método obtener_rankings
        df_guardados = db_manager.obtener_rankings()
        
        if not df_guardados.empty:
            logger.info(f"Rankings encontrados en BD: {len(df_guardados)} registros")
            
            # Contar por tipo de ranking
            for tipo in df_guardados['tipo_ranking'].unique():
                count = len(df_guardados[df_guardados['tipo_ranking'] == tipo])
                logger.info(f"  {tipo}: {count} registros")
        else:
            logger.warning("No se encontraron rankings guardados en la base de datos")
        
        # Guardar metadata
        db_manager.set_metadata('rankings', 'ultima_generacion', 
                               datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                               'Última generación de rankings HDD')
        db_manager.set_metadata('rankings', 'total_registros', str(len(df_ranking_completo)),
                               'Total de registros de ranking guardados')
        
        logger.info("=" * 80)
        logger.info("ANÁLISIS DE RANKING HDD COMPLETADO EXITOSAMENTE")
        logger.info("=" * 80)
        
        print("\n✅ Análisis de ranking HDD completado exitosamente")
        print("📊 Revisa los logs para más detalles")
        
        return True
        
    except Exception as e:
        logger.error(f"Error ejecutando ranking HDD: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"\n❌ Error ejecutando ranking HDD: {str(e)}")
        return False

if __name__ == "__main__":
    ejecutar_ranking_hdd_real() 