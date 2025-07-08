#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Rápido - CP Data Analysis v2
=================================

Script para verificar que todos los componentes del sistema funcionan correctamente.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Probar que todos los módulos se pueden importar correctamente."""
    print("🔍 Probando imports...")
    
    try:
        from cp_config_manager import ConfigManager
        from cp_log_manager import LogManager
        from cp_upload_data_deploy import DataUploader
        from cp_db_manager import DatabaseManager
        from cp_ranking_functions import (
            generar_ranking_llenado,
            generar_ranking_inestabilidad,
            generar_ranking_tasa_cambio,
            generar_ranking_combinado
        )
        print("✅ Todos los imports exitosos")
        return True
    except Exception as e:
        print(f"❌ Error en imports: {str(e)}")
        return False

def test_config_manager():
    """Probar el gestor de configuración."""
    print("\n🔧 Probando ConfigManager...")
    
    try:
        from cp_config_manager import ConfigManager
        config = ConfigManager()
        print("✅ ConfigManager inicializado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error en ConfigManager: {str(e)}")
        return False

def test_log_manager():
    """Probar el gestor de logs."""
    print("\n📝 Probando LogManager...")
    
    try:
        from cp_log_manager import LogManager
        log_manager = LogManager()
        logger = log_manager.get_logger('test_quick')
        logger.info("Test de logging exitoso")
        print("✅ LogManager funcionando correctamente")
        return True
    except Exception as e:
        print(f"❌ Error en LogManager: {str(e)}")
        return False

def test_ranking_functions():
    """Probar las funciones de ranking con datos simulados."""
    print("\n📊 Probando funciones de ranking...")
    
    try:
        from cp_ranking_functions import (
            generar_ranking_llenado,
            generar_ranking_inestabilidad,
            generar_ranking_tasa_cambio,
            generar_ranking_combinado
        )
        
        # Crear datos simulados
        np.random.seed(42)
        fechas = pd.date_range(start='2025-01-01', end='2025-01-07', freq='H')
        equipos = ['EQUIPO001', 'EQUIPO002', 'EQUIPO003']
        areas = ['AREA1', 'AREA2', 'AREA1']
        
        datos = []
        for fecha in fechas:
            for i, equipo in enumerate(equipos):
                datos.append({
                    'fecha': fecha,
                    'equipo': equipo,
                    'area': areas[i],
                    'valor': np.random.normal(50, 10),
                    'tasa_cambio': np.random.normal(0, 2)
                })
        
        df = pd.DataFrame(datos)
        
        # Probar funciones de ranking
        ranking_llenado = generar_ranking_llenado(df)
        ranking_inestabilidad = generar_ranking_inestabilidad(df)
        ranking_tasa_cambio = generar_ranking_tasa_cambio(df)
        ranking_combinado = generar_ranking_combinado(df)
        
        print(f"✅ Rankings generados:")
        print(f"   - Llenado: {len(ranking_llenado)} registros")
        print(f"   - Inestabilidad: {len(ranking_inestabilidad)} registros")
        print(f"   - Tasa de cambio: {len(ranking_tasa_cambio)} registros")
        print(f"   - Combinado: {len(ranking_combinado)} registros")
        
        return True
    except Exception as e:
        print(f"❌ Error en funciones de ranking: {str(e)}")
        return False

def test_database_connection():
    """Probar conexión a base de datos."""
    print("\n🗄️ Probando conexión a base de datos...")
    
    try:
        from cp_db_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Intentar conectar
        connection = db_manager.get_connection()
        if connection:
            connection.close()
            print("✅ Conexión a base de datos exitosa")
            return True
        else:
            print("⚠️ No se pudo establecer conexión a la base de datos")
            return False
    except Exception as e:
        print(f"❌ Error en conexión a base de datos: {str(e)}")
        return False

def main():
    """Función principal de pruebas."""
    print("🚀 Iniciando pruebas rápidas de CP Data Analysis v2")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("ConfigManager", test_config_manager),
        ("LogManager", test_log_manager),
        ("Funciones de Ranking", test_ranking_functions),
        ("Conexión a BD", test_database_connection)
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error inesperado en {nombre}: {str(e)}")
            resultados.append((nombre, False))
    
    # Resumen de resultados
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    exitos = 0
    total = len(resultados)
    
    for nombre, resultado in resultados:
        status = "✅ EXITOSO" if resultado else "❌ FALLIDO"
        print(f"{nombre:<25} {status}")
        if resultado:
            exitos += 1
    
    print(f"\nResultado: {exitos}/{total} pruebas exitosas")
    
    if exitos == total:
        print("🎉 ¡Todas las pruebas pasaron! El sistema está listo para usar.")
        return 0
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores antes de usar el sistema.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 