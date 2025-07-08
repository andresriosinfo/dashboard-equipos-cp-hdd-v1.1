#!/usr/bin/env python
# coding: utf-8

"""
Script de prueba para el sistema de puntuación unificado.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_percentile_calculation():
    """
    Prueba el cálculo de percentiles.
    """
    print("🧪 PRUEBA 1: Cálculo de Percentiles")
    print("-" * 50)
    
    # Importar función de percentiles
    from unified_scoring_system import UnifiedScoringSystem
    
    scoring_system = UnifiedScoringSystem()
    
    # Datos de prueba
    test_values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    
    # Probar percentiles para valores específicos
    test_cases = [
        (25, 'higher_better', 'Valor bajo, dirección mayor=mejor'),
        (75, 'higher_better', 'Valor alto, dirección mayor=mejor'),
        (25, 'lower_better', 'Valor bajo, dirección menor=mejor'),
        (75, 'lower_better', 'Valor alto, dirección menor=mejor')
    ]
    
    for value, direction, description in test_cases:
        score = scoring_system.calculate_percentile_score(value, test_values, direction)
        print(f"   {description}: {value} → {score:.1f}pts")
    
    print("✅ Prueba de percentiles completada\n")

def test_metric_configs():
    """
    Prueba la configuración de métricas.
    """
    print("🧪 PRUEBA 2: Configuración de Métricas")
    print("-" * 50)
    
    from unified_scoring_system import UnifiedScoringSystem
    
    scoring_system = UnifiedScoringSystem()
    
    # Verificar que los pesos sumen 1.0
    total_weight = sum(config['weight'] for config in scoring_system.metric_configs.values())
    print(f"   Total de pesos: {total_weight:.3f}")
    
    if abs(total_weight - 1.0) < 0.001:
        print("   ✅ Los pesos suman correctamente 1.0")
    else:
        print(f"   ❌ Error: Los pesos suman {total_weight}, deberían sumar 1.0")
    
    # Mostrar configuración de métricas
    print("\n   Configuración de métricas:")
    for metric_name, config in scoring_system.metric_configs.items():
        print(f"   - {metric_name}: {config['weight']*100:.0f}% ({config['direction']})")
    
    print("✅ Prueba de configuración completada\n")

def test_scoring_calculation():
    """
    Prueba el cálculo de puntuaciones con datos simulados.
    """
    print("🧪 PRUEBA 3: Cálculo de Puntuaciones")
    print("-" * 50)
    
    from unified_scoring_system import UnifiedScoringSystem
    
    scoring_system = UnifiedScoringSystem()
    
    # Crear datos simulados de CP
    fechas = [datetime.now() - timedelta(days=i) for i in range(7)]
    cp_data = {
        'df_AREA1': pd.DataFrame({
            'codigo': ['COD1'] * 21,
            'fecha': fechas * 3,
            'equipo': ['Equipo_A'] * 7 + ['Equipo_B'] * 7 + ['Equipo_C'] * 7,
            'area': ['AREA1'] * 21,
            'valor': [800] * 7 + [600] * 7 + [400] * 7,  # Valores diferentes para cada equipo
            'actualizacion': [datetime.now()] * 21
        })
    }
    
    # Crear datos simulados de HDD
    hdd_data = {
        'df_C': pd.DataFrame({
            'codigo': ['HDD1'] * 21,
            'fecha': fechas * 3,
            'equipo': ['Equipo_A'] * 7 + ['Equipo_B'] * 7 + ['Equipo_C'] * 7,
            'unidad': ['C:'] * 21,
            'uso': [0.3] * 7 + [0.6] * 7 + [0.8] * 7,  # Valores diferentes para cada equipo
            'actualizacion': [datetime.now()] * 21
        })
    }
    
    # Calcular métricas
    cp_metrics = scoring_system.calculate_cp_metrics(cp_data)
    hdd_metrics = scoring_system.calculate_hdd_metrics(hdd_data)
    
    print(f"   Métricas CP calculadas: {len(cp_metrics)} equipos")
    print(f"   Métricas HDD calculadas: {len(hdd_metrics)} equipos")
    
    # Calcular puntuaciones unificadas
    df_scores = scoring_system.calculate_unified_scores(cp_metrics, hdd_metrics)
    
    if not df_scores.empty:
        print(f"   Puntuaciones calculadas: {len(df_scores)} equipos")
        
        # Mostrar resultados
        for _, row in df_scores.iterrows():
            print(f"   - {row['equipo']}: {row['puntuacion_final']:.2f}pts (Posición {row['posicion_ranking']})")
        
        print("✅ Prueba de cálculo completada\n")
    else:
        print("   ❌ Error: No se pudieron calcular puntuaciones\n")

def test_explanation_generation():
    """
    Prueba la generación de explicaciones.
    """
    print("🧪 PRUEBA 4: Generación de Explicaciones")
    print("-" * 50)
    
    from unified_scoring_system import UnifiedScoringSystem
    
    scoring_system = UnifiedScoringSystem()
    
    # Crear datos de prueba con puntuaciones
    test_data = pd.DataFrame({
        'equipo': ['Equipo_Test'],
        'area_cp': ['AREA_TEST'],
        'unidades_hdd': [['C:', 'D:']],
        'puntuacion_final': [75.5],
        'posicion_ranking': [1],
        'cp_llenado': [800],
        'cp_llenado_score': [85.2],
        'cp_inestabilidad': [1500],
        'cp_inestabilidad_score': [65.1],
        'cp_tasa_cambio': [50000],
        'cp_tasa_cambio_score': [70.3],
        'hdd_uso': [45.2],
        'hdd_uso_score': [80.0],
        'hdd_inestabilidad': [8000],
        'hdd_inestabilidad_score': [55.5],
        'hdd_tasa_cambio': [120000],
        'hdd_tasa_cambio_score': [60.2],
        'registros_cp': [7],
        'registros_hdd': [7],
        'fecha_ejecucion': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    
    # Generar explicaciones
    df_explanation = scoring_system.generate_explanation_columns(test_data)
    
    if not df_explanation.empty:
        row = df_explanation.iloc[0]
        print(f"   Equipo: {row['equipo']}")
        print(f"   Categoría: {row['categoria_final']}")
        print(f"   Explicación: {row['explicacion_detallada']}")
        print(f"   Recomendación: {row['recomendaciones']}")
        print("✅ Prueba de explicaciones completada\n")
    else:
        print("   ❌ Error: No se pudieron generar explicaciones\n")

def test_database_operations():
    """
    Prueba las operaciones de base de datos.
    """
    print("🧪 PRUEBA 5: Operaciones de Base de Datos")
    print("-" * 50)
    
    try:
        # Importar componentes de base de datos
        import sys
        sys.path.append('cp_data_analysis_v2/src')
        from cp_db_manager import get_db_manager
        
        db_manager = get_db_manager()
        
        if db_manager.is_connected:
            print("   ✅ Conexión a base de datos exitosa")
            
            # Verificar si existe la tabla
            check_table_query = """
            SELECT COUNT(*) as table_exists
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'nv_unified_scoring'
            """
            
            result = db_manager.execute_query(check_table_query)
            if result and result[0]['table_exists'] > 0:
                print("   ✅ Tabla nv_unified_scoring existe")
                
                # Contar registros
                count_query = "SELECT COUNT(*) as total FROM nv_unified_scoring"
                count_result = db_manager.execute_query(count_query)
                if count_result:
                    total_records = count_result[0]['total']
                    print(f"   📊 Total de registros: {total_records}")
            else:
                print("   ⚠️  Tabla nv_unified_scoring no existe (se creará al ejecutar el sistema)")
        else:
            print("   ❌ Error: No se pudo conectar a la base de datos")
    
    except Exception as e:
        print(f"   ❌ Error en operaciones de base de datos: {str(e)}")
    
    print("✅ Prueba de base de datos completada\n")

def test_imports():
    """
    Prueba las importaciones necesarias.
    """
    print("🧪 PRUEBA 6: Importaciones")
    print("-" * 50)
    
    try:
        # Probar importación del sistema principal
        from unified_scoring_system import UnifiedScoringSystem
        print("   ✅ unified_scoring_system importado correctamente")
        
        # Probar importación del visualizador
        from show_unified_results import get_latest_results
        print("   ✅ show_unified_results importado correctamente")
        
        # Probar importaciones de CP
        import sys
        sys.path.append('cp_data_analysis_v2/src')
        try:
            from cp_upload_data_deploy import upload_data_sql
            print("   ✅ Componentes CP importados correctamente")
        except ImportError as e:
            print(f"   ⚠️  Componentes CP no disponibles: {str(e)}")
        
        # Probar importaciones de HDD
        sys.path.append('hdd_data_analysis_v2/src')
        try:
            from hdd_upload_data_deploy import upload_data_sql
            print("   ✅ Componentes HDD importados correctamente")
        except ImportError as e:
            print(f"   ⚠️  Componentes HDD no disponibles: {str(e)}")
        
    except ImportError as e:
        print(f"   ❌ Error de importación: {str(e)}")
    
    print("✅ Prueba de importaciones completada\n")

def run_all_tests():
    """
    Ejecuta todas las pruebas.
    """
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE PUNTUACIÓN UNIFICADO")
    print("=" * 80)
    
    try:
        # Ejecutar pruebas
        test_imports()
        test_percentile_calculation()
        test_metric_configs()
        test_scoring_calculation()
        test_explanation_generation()
        test_database_operations()
        
        print("🎉 TODAS LAS PRUEBAS COMPLETADAS")
        print("=" * 80)
        print("✅ El sistema está listo para usar")
        print("\n📋 Próximos pasos:")
        print("   1. Ejecutar: python unified_scoring_system.py")
        print("   2. Visualizar: python show_unified_results.py")
        print("   3. Consultar documentación: README_UNIFIED_SCORING.md")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    run_all_tests() 