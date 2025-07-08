#!/usr/bin/env python
# coding: utf-8

"""
Test script for HDD Data Analysis application
"""

import sys
import logging
import pandas as pd
from datetime import datetime

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger('hdd_test')

def test_imports():
    """Test that all HDD modules can be imported correctly."""
    logger.info("Testing HDD module imports...")
    
    try:
        from hdd_config_manager import get_config, get_config_manager
        logger.info("✓ hdd_config_manager imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import hdd_config_manager: {e}")
        return False
    
    try:
        from hdd_log_manager import get_log_manager, setup_logging
        logger.info("✓ hdd_log_manager imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import hdd_log_manager: {e}")
        return False
    
    try:
        from hdd_db_manager import get_db_manager
        logger.info("✓ hdd_db_manager imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import hdd_db_manager: {e}")
        return False
    
    try:
        from hdd_batch_processor import get_batch_processor
        logger.info("✓ hdd_batch_processor imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import hdd_batch_processor: {e}")
        return False
    
    try:
        from hdd_functions_deploy import encontrar_maximo_por_equipo, hdd_mean_seven_days
        logger.info("✓ hdd_functions_deploy imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import hdd_functions_deploy: {e}")
        return False
    
    try:
        from hdd_upload_data_deploy import upload_data_sql
        logger.info("✓ hdd_upload_data_deploy imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import hdd_upload_data_deploy: {e}")
        return False
    
    try:
        from hdd_write_data_deploy import save_data_to_sql
        logger.info("✓ hdd_write_data_deploy imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import hdd_write_data_deploy: {e}")
        return False
    
    logger.info("All HDD modules imported successfully!")
    return True

def test_config():
    """Test configuration loading."""
    logger.info("Testing configuration...")
    
    try:
        from hdd_config_manager import get_config, get_config_manager
        
        # Initialize config manager
        config_manager = get_config_manager()
        
        # Test getting some config values
        dias_analisis = get_config('dias_analisis', 7)
        umbral_maximo = get_config('umbral_maximo', 100.0)
        
        logger.info(f"✓ Configuration loaded: dias_analisis={dias_analisis}, umbral_maximo={umbral_maximo}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Configuration test failed: {e}")
        return False

def test_sample_data():
    """Test with sample data."""
    logger.info("Testing with sample HDD data...")
    
    try:
        from hdd_functions_deploy import encontrar_maximo_por_equipo, hdd_mean_seven_days
        
        # Create sample data
        sample_data = {
            'codigo': ['HDD001', 'HDD002', 'HDD003'],
            'fecha': ['2024-01-01', '2024-01-01', '2024-01-01'],
            'equipo': ['Server1', 'Server2', 'Server3'],
            'unidad': ['U1', 'U1', 'U2'],
            'uso': [75.5, 45.2, 90.1]
        }
        
        df = pd.DataFrame(sample_data)
        df_dict = {'df_test': df}
        
        # Test analysis functions
        result_max = encontrar_maximo_por_equipo(df_dict)
        result_mean = hdd_mean_seven_days(df_dict)
        
        logger.info(f"✓ Sample analysis completed: max={len(result_max)} records, mean={len(result_mean)} records")
        return True
        
    except Exception as e:
        logger.error(f"✗ Sample data test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Run all tests."""
    logger.info("=" * 50)
    logger.info("HDD DATA ANALYSIS TEST SUITE")
    logger.info("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("Sample Data Analysis", test_sample_data)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\nRunning test: {test_name}")
        try:
            if test_func():
                passed += 1
                logger.info(f"✓ {test_name} PASSED")
            else:
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name} FAILED with exception: {e}")
    
    logger.info("\n" + "=" * 50)
    logger.info(f"TEST RESULTS: {passed}/{total} tests passed")
    logger.info("=" * 50)
    
    if passed == total:
        logger.info("🎉 All tests passed! HDD application is ready to use.")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 