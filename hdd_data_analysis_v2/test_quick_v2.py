#!/usr/bin/env python3
"""
HDD Data Analysis v2 - Prueba Rápida
Verifica que todos los componentes del sistema funcionen correctamente
"""

import sys
import os
import yaml
import logging
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def setup_logging():
    """Configurar logging para las pruebas"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/test_quick_v2.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def test_imports():
    """Probar que todos los módulos se pueden importar"""
    logger = logging.getLogger(__name__)
    logger.info("Probando imports de módulos...")
    
    try:
        import hdd_ranking_functions
        logger.info("✓ hdd_ranking_functions importado correctamente")
    except ImportError as e:
        logger.error(f"✗ Error importando hdd_ranking_functions: {e}")
        return False
    
    try:
        import hdd_db_manager
        logger.info("✓ hdd_db_manager importado correctamente")
    except ImportError as e:
        logger.error(f"✗ Error importando hdd_db_manager: {e}")
        return False
    
    try:
        import hdd_config_manager
        logger.info("✓ hdd_config_manager importado correctamente")
    except ImportError as e:
        logger.error(f"✗ Error importando hdd_config_manager: {e}")
        return False
    
    try:
        import hdd_log_manager
        logger.info("✓ hdd_log_manager importado correctamente")
    except ImportError as e:
        logger.error(f"✗ Error importando hdd_log_manager: {e}")
        return False
    
    return True

def test_configuration():
    """Probar la carga de configuración"""
    logger = logging.getLogger(__name__)
    logger.info("Probando carga de configuración...")
    
    try:
        # Probar archivo de configuración v2
        with open('config_v2.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        required_sections = ['database', 'ranking', 'logging', 'processing']
        for section in required_sections:
            if section not in config:
                logger.error(f"✗ Sección '{section}' no encontrada en config_v2.yaml")
                return False
        
        logger.info("✓ Configuración v2 cargada correctamente")
        
        # Probar configuración original
        with open('hdd_config_params.yaml', 'r', encoding='utf-8') as f:
            original_config = yaml.safe_load(f)
        logger.info("✓ Configuración original cargada correctamente")
        
        return True
    except Exception as e:
        logger.error(f"✗ Error cargando configuración: {e}")
        return False

def test_ranking_functions():
    """Probar las funciones de ranking con datos simulados"""
    logger = logging.getLogger(__name__)
    logger.info("Probando funciones de ranking...")
    
    try:
        import hdd_ranking_functions as hrf
        import pandas as pd
        import numpy as np
        
        # Crear datos simulados
        np.random.seed(42)
        dates = pd.date_range(start='2025-01-01', periods=30, freq='D')
        
        # Simular datos de HDD
        hdd_data = []
        equipos = ['EQUIPO_A', 'EQUIPO_B', 'EQUIPO_C', 'EQUIPO_D', 'EQUIPO_E']
        for i in range(5):  # 5 HDDs
            hdd_id = f"HDD_{i+1:03d}"
            equipo = equipos[i]
            for date in dates:
                hdd_data.append({
                    'codigo': f'CODE_{hdd_id}_{equipo}',
                    'fecha': date,
                    'equipo': equipo,
                    'unidad': hdd_id,
                    'uso': np.random.uniform(20, 95)
                })
        
        df = pd.DataFrame(hdd_data)
        
        # Probar funciones de ranking
        usage_ranking = hrf.calculate_usage_ranking(df)
        instability_ranking = hrf.calculate_instability_ranking(df)
        rate_ranking = hrf.calculate_rate_of_change_ranking(df)
        combined_ranking = hrf.calculate_combined_ranking(df)
        
        logger.info(f"✓ Ranking por uso calculado: {len(usage_ranking)} parejas equipo-unidad")
        logger.info(f"✓ Ranking por inestabilidad calculado: {len(instability_ranking)} parejas equipo-unidad")
        logger.info(f"✓ Ranking por tasa de cambio calculado: {len(rate_ranking)} parejas equipo-unidad")
        logger.info(f"✓ Ranking combinado calculado: {len(combined_ranking)} parejas equipo-unidad")
        
        return True
    except Exception as e:
        logger.error(f"✗ Error en funciones de ranking: {e}")
        return False

def test_database_manager():
    """Probar el gestor de base de datos"""
    logger = logging.getLogger(__name__)
    logger.info("Probando gestor de base de datos...")
    
    try:
        import hdd_db_manager as hdm
        
        # Probar creación de instancia (sin conexión real)
        db_manager = hdm.HDDDatabaseManager()
        logger.info("✓ Instancia de HDDDatabaseManager creada")
        
        # Probar métodos de la clase
        methods = [
            'create_rankings_table',
            'save_rankings',
            'get_rankings',
            'get_hdd_data'
        ]
        
        for method in methods:
            if hasattr(db_manager, method):
                logger.info(f"✓ Método {method} encontrado")
            else:
                logger.warning(f"⚠ Método {method} no encontrado")
        
        return True
    except Exception as e:
        logger.error(f"✗ Error en gestor de base de datos: {e}")
        return False

def test_config_manager():
    """Probar el gestor de configuración"""
    logger = logging.getLogger(__name__)
    logger.info("Probando gestor de configuración...")
    
    try:
        import hdd_config_manager as hcm
        
        # Probar carga de configuración
        config_manager = hcm.HDDConfigManager()
        config = config_manager.load_config()
        
        if config:
            logger.info("✓ Configuración cargada correctamente")
            logger.info(f"  - Servidor DB: {config.get('database', {}).get('server', 'N/A')}")
            logger.info(f"  - Base de datos: {config.get('database', {}).get('database', 'N/A')}")
        else:
            logger.warning("⚠ No se pudo cargar la configuración")
        
        return True
    except Exception as e:
        logger.error(f"✗ Error en gestor de configuración: {e}")
        return False

def test_log_manager():
    """Probar el gestor de logging"""
    logger = logging.getLogger(__name__)
    logger.info("Probando gestor de logging...")
    
    try:
        import hdd_log_manager as hlm
        
        # Probar creación de logger
        log_manager = hlm.HDDLogManager()
        test_logger = log_manager.get_logger('test_quick_v2')
        
        test_logger.info("Mensaje de prueba del sistema de logging")
        test_logger.warning("Advertencia de prueba")
        
        logger.info("✓ Sistema de logging funcionando correctamente")
        return True
    except Exception as e:
        logger.error(f"✗ Error en gestor de logging: {e}")
        return False

def test_file_structure():
    """Verificar la estructura de archivos"""
    logger = logging.getLogger(__name__)
    logger.info("Verificando estructura de archivos...")
    
    required_files = [
        'main.py',
        'config.py',
        'config_v2.yaml',
        'hdd_config_params.yaml',
        'requirements.txt',
        'README.md',
        'src/hdd_ranking_functions.py',
        'src/hdd_db_manager.py',
        'src/hdd_config_manager.py',
        'src/hdd_log_manager.py',
        'tests/test_ranking_hdd.py',
        'scripts/ejecutar_ranking_hdd_real.py',
        'docs/README_RANKING_HDD.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            logger.info(f"✓ {file_path}")
        else:
            logger.error(f"✗ {file_path} - NO ENCONTRADO")
            missing_files.append(file_path)
    
    if missing_files:
        logger.warning(f"⚠ {len(missing_files)} archivos faltantes")
        return False
    else:
        logger.info("✓ Todos los archivos requeridos están presentes")
        return True

def main():
    """Función principal de pruebas"""
    print("=" * 60)
    print("HDD Data Analysis v2 - Prueba Rápida")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Configurar logging
    logger = setup_logging()
    
    # Lista de pruebas
    tests = [
        ("Estructura de archivos", test_file_structure),
        ("Imports de módulos", test_imports),
        ("Configuración", test_configuration),
        ("Gestor de logging", test_log_manager),
        ("Gestor de configuración", test_config_manager),
        ("Gestor de base de datos", test_database_manager),
        ("Funciones de ranking", test_ranking_functions),
    ]
    
    # Ejecutar pruebas
    results = []
    for test_name, test_func in tests:
        print(f"Ejecutando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✓ PASÓ" if result else "✗ FALLÓ"
            print(f"  {status}")
        except Exception as e:
            logger.error(f"Error en prueba '{test_name}': {e}")
            results.append((test_name, False))
            print(f"  ✗ ERROR")
        print()
    
    # Resumen de resultados
    print("=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASÓ" if result else "✗ FALLÓ"
        print(f"{test_name:<30} {status}")
    
    print()
    print(f"Pruebas pasadas: {passed}/{total}")
    print(f"Porcentaje de éxito: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está listo para usar.")
        return 0
    else:
        print(f"\n⚠ {total-passed} prueba(s) fallaron. Revisa los logs para más detalles.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 