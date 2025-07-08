#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_cp_data():
    """Debug datos CP"""
    try:
        sys.path.append('cp_data_analysis_v2/src')
        from cp_upload_data_deploy import upload_data_sql
        
        logger.info("=== DEBUG DATOS CP ===")
        cp_data = upload_data_sql()
        
        if not cp_data:
            logger.warning("No se obtuvieron datos CP")
            return
        
        logger.info(f"DataFrames CP obtenidos: {len(cp_data)}")
        
        total_equipos = set()
        for nombre_df, df in cp_data.items():
            logger.info(f"DataFrame '{nombre_df}': {len(df)} filas")
            if not df.empty:
                logger.info(f"  Columnas: {list(df.columns)}")
                logger.info(f"  Equipos únicos: {df['equipo'].nunique() if 'equipo' in df.columns else 'N/A'}")
                if 'equipo' in df.columns:
                    total_equipos.update(df['equipo'].unique())
        
        logger.info(f"Total equipos únicos en CP: {len(total_equipos)}")
        logger.info(f"Primeros 10 equipos CP: {list(total_equipos)[:10]}")
        
    except Exception as e:
        logger.error(f"Error debug CP: {str(e)}")

def debug_hdd_data():
    """Debug datos HDD"""
    try:
        sys.path.append('hdd_data_analysis_v2/src')
        from hdd_upload_data_deploy import upload_data_sql
        
        logger.info("=== DEBUG DATOS HDD ===")
        hdd_data = upload_data_sql()
        
        if not hdd_data:
            logger.warning("No se obtuvieron datos HDD")
            return
        
        logger.info(f"DataFrames HDD obtenidos: {len(hdd_data)}")
        
        total_equipos = set()
        for nombre_df, df in hdd_data.items():
            logger.info(f"DataFrame '{nombre_df}': {len(df)} filas")
            if not df.empty:
                logger.info(f"  Columnas: {list(df.columns)}")
                logger.info(f"  Equipos únicos: {df['equipo'].nunique() if 'equipo' in df.columns else 'N/A'}")
                if 'equipo' in df.columns:
                    total_equipos.update(df['equipo'].unique())
        
        logger.info(f"Total equipos únicos en HDD: {len(total_equipos)}")
        logger.info(f"Primeros 10 equipos HDD: {list(total_equipos)[:10]}")
        
    except Exception as e:
        logger.error(f"Error debug HDD: {str(e)}")

def main():
    """Función principal"""
    logger.info("INICIANDO DEBUG DE FUENTES DE DATOS")
    logger.info("="*50)
    
    debug_cp_data()
    print()
    debug_hdd_data()
    
    logger.info("="*50)
    logger.info("DEBUG COMPLETADO")

if __name__ == "__main__":
    main() 