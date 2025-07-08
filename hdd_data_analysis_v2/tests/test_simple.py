#!/usr/bin/env python
# coding: utf-8

"""
Test script simple para verificar que el análisis HDD funciona correctamente
"""

import sys
import logging
import pandas as pd
from datetime import datetime, timedelta

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger('hdd_test_simple')

def test_simple_analysis():
    """Test simple con datos de muestra."""
    logger.info("Iniciando test simple de análisis HDD...")
    
    try:
        # Import HDD functions
        from hdd_functions_deploy import encontrar_maximo_por_equipo, hdd_mean_seven_days
        
        # Create sample data
        sample_data = {
            'codigo': ['HDD001', 'HDD002', 'HDD003', 'HDD004', 'HDD005'] * 10,
            'fecha': [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)] * 7,
            'equipo': ['Server1', 'Server2', 'Server3', 'Server4', 'Server5'] * 10,
            'unidad': ['U1', 'U1', 'U2', 'U2', 'U3'] * 10,
            'uso': [75.5, 45.2, 90.1, 30.8, 85.3] * 10
        }
        
        df = pd.DataFrame(sample_data)
        df_dict = {'df_test': df}
        
        logger.info(f"Datos de prueba creados: {len(df)} registros")
        
        # Test analysis functions
        logger.info("Probando función de máximo...")
        result_max = encontrar_maximo_por_equipo(df_dict)
        logger.info(f"Resultado máximo: {len(result_max)} registros")
        
        logger.info("Probando función de promedios...")
        result_mean = hdd_mean_seven_days(df_dict)
        logger.info(f"Resultado promedios: {len(result_mean)} registros")
        
        # Test database save
        logger.info("Probando guardado en base de datos...")
        from hdd_db_manager import get_db_manager
        
        db_manager = get_db_manager()
        
        if not result_max.empty:
            success = db_manager.save_results(result_max, 'analisis')
            logger.info(f"Guardado de análisis: {'Exitoso' if success else 'Falló'}")
        
        if not result_mean.empty:
            success = db_manager.save_results(result_mean, 'promedios')
            logger.info(f"Guardado de promedios: {'Exitoso' if success else 'Falló'}")
        
        logger.info("✅ Test simple completado exitosamente!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test simple: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Run simple test."""
    logger.info("=" * 50)
    logger.info("TEST SIMPLE HDD DATA ANALYSIS")
    logger.info("=" * 50)
    
    success = test_simple_analysis()
    
    logger.info("=" * 50)
    if success:
        logger.info("🎉 Test simple PASÓ - La aplicación HDD funciona correctamente")
        return 0
    else:
        logger.error("❌ Test simple FALLÓ - Hay problemas que resolver")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 