#!/usr/bin/env python
# coding: utf-8

"""
Script de prueba para verificar las funciones de ranking de equipos.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def crear_datos_prueba():
    """
    Crea datos de prueba para simular los datos reales de equipos.
    
    Returns:
        dict: Diccionario con DataFrames de prueba
    """
    logger.info("Creando datos de prueba...")
    
    # Crear fechas para los últimos 7 días
    fecha_fin = datetime.now()
    fechas = [fecha_fin - timedelta(days=i) for i in range(7)]
    fechas.reverse()  # Ordenar de más antigua a más reciente
    
    # Crear datos de prueba para diferentes áreas
    datos_prueba = []
    
    # Área 1: Equipos con diferentes niveles de llenado
    equipos_area1 = ['Equipo_A1', 'Equipo_A2', 'Equipo_A3']
    for equipo in equipos_area1:
        for fecha in fechas:
            # Generar valores con diferentes patrones
            if equipo == 'Equipo_A1':  # Alto llenado, estable
                valor = np.random.normal(800, 50)
            elif equipo == 'Equipo_A2':  # Medio llenado, inestable
                valor = np.random.normal(500, 150)
            else:  # Bajo llenado, muy inestable
                valor = np.random.normal(200, 200)
            
            datos_prueba.append({
                'codigo': f'COD_{equipo}',
                'fecha': fecha,
                'equipo': equipo,
                'area': 'Area_1',
                'valor': max(0, int(valor)),  # Asegurar valores positivos
                'actualizacion': datetime.now()
            })
    
    # Área 2: Equipos con diferentes tasas de cambio
    equipos_area2 = ['Equipo_B1', 'Equipo_B2', 'Equipo_B3']
    for equipo in equipos_area2:
        valor_base = 400
        for i, fecha in enumerate(fechas):
            # Generar valores con diferentes tasas de cambio
            if equipo == 'Equipo_B1':  # Cambio gradual
                valor = valor_base + (i * 20) + np.random.normal(0, 10)
            elif equipo == 'Equipo_B2':  # Cambio moderado
                valor = valor_base + (i * 50) + np.random.normal(0, 30)
            else:  # Cambio brusco
                valor = valor_base + (i * 100) + np.random.normal(0, 80)
            
            datos_prueba.append({
                'codigo': f'COD_{equipo}',
                'fecha': fecha,
                'equipo': equipo,
                'area': 'Area_2',
                'valor': max(0, int(valor)),
                'actualizacion': datetime.now()
            })
    
    # Crear DataFrame
    df = pd.DataFrame(datos_prueba)
    
    # Agrupar por área
    df_dict = {}
    for area in df['area'].unique():
        df_dict[f'df_{area}'] = df[df['area'] == area].copy()
    
    logger.info(f"Datos de prueba creados: {len(df_dict)} áreas, {len(df)} registros totales")
    return df_dict

def probar_funciones_ranking():
    """
    Prueba las funciones de ranking con datos de prueba.
    """
    logger.info("Iniciando pruebas de funciones de ranking...")
    
    try:
        # Crear datos de prueba
        df_dict = crear_datos_prueba()
        
        # Importar funciones de ranking
        from cp_ranking_functions import (
            calcular_ranking_llenado,
            calcular_ranking_inestabilidad,
            calcular_ranking_tasa_cambio,
            generar_ranking_completo
        )
        
        # Probar ranking por llenado
        logger.info("Probando ranking por llenado...")
        df_llenado = calcular_ranking_llenado(df_dict)
        if not df_llenado.empty:
            logger.info(f"✓ Ranking por llenado: {len(df_llenado)} registros")
            logger.info("Top 3 equipos por llenado:")
            for _, row in df_llenado.head(3).iterrows():
                logger.info(f"  Posición {row['posicion']}: {row['equipo']} (Área: {row['area']}) - Valor: {row['valor_metrico']}")
        else:
            logger.warning("✗ Ranking por llenado no generó resultados")
        
        # Probar ranking por inestabilidad
        logger.info("Probando ranking por inestabilidad...")
        df_inestabilidad = calcular_ranking_inestabilidad(df_dict)
        if not df_inestabilidad.empty:
            logger.info(f"✓ Ranking por inestabilidad: {len(df_inestabilidad)} registros")
            logger.info("Top 3 equipos por inestabilidad:")
            for _, row in df_inestabilidad.head(3).iterrows():
                logger.info(f"  Posición {row['posicion']}: {row['equipo']} (Área: {row['area']}) - Desviación: {row['valor_metrico']}")
        else:
            logger.warning("✗ Ranking por inestabilidad no generó resultados")
        
        # Probar ranking por tasa de cambio
        logger.info("Probando ranking por tasa de cambio...")
        df_tasa_cambio = calcular_ranking_tasa_cambio(df_dict)
        if not df_tasa_cambio.empty:
            logger.info(f"✓ Ranking por tasa de cambio: {len(df_tasa_cambio)} registros")
            logger.info("Top 3 equipos por tasa de cambio:")
            for _, row in df_tasa_cambio.head(3).iterrows():
                logger.info(f"  Posición {row['posicion']}: {row['equipo']} (Área: {row['area']}) - Variabilidad: {row['valor_metrico']}")
        else:
            logger.warning("✗ Ranking por tasa de cambio no generó resultados")
        
        # Probar ranking completo
        logger.info("Probando ranking completo...")
        df_ranking_completo = generar_ranking_completo(df_dict)
        if not df_ranking_completo.empty:
            logger.info(f"✓ Ranking completo: {len(df_ranking_completo)} registros")
            
            # Mostrar resumen por métrica
            for metrica in df_ranking_completo['metrica'].unique():
                df_metrica = df_ranking_completo[df_ranking_completo['metrica'] == metrica]
                logger.info(f"  {metrica.capitalize()}: {len(df_metrica)} equipos")
        else:
            logger.warning("✗ Ranking completo no generó resultados")
        
        logger.info("✓ Todas las pruebas completadas exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error en las pruebas: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def probar_guardado_bd():
    """
    Prueba el guardado en la base de datos (solo si está disponible).
    """
    logger.info("Probando guardado en base de datos...")
    
    try:
        # Importar componentes de base de datos
        from cp_db_manager import get_db_manager
        from cp_ranking_functions import generar_ranking_completo
        
        # Crear datos de prueba
        df_dict = crear_datos_prueba()
        
        # Generar ranking
        df_ranking = generar_ranking_completo(df_dict)
        
        if df_ranking.empty:
            logger.warning("No hay datos de ranking para guardar")
            return False
        
        # Obtener manager de base de datos
        db_manager = get_db_manager()
        
        if not db_manager.is_connected:
            logger.warning("No se pudo conectar a la base de datos - omitiendo prueba de guardado")
            return False
        
        # Guardar resultados
        success = db_manager.save_results(df_ranking, 'ranking_completo')
        
        if success:
            logger.info("✓ Datos guardados exitosamente en la base de datos")
            return True
        else:
            logger.error("✗ Error al guardar datos en la base de datos")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error en prueba de guardado: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("=== INICIANDO PRUEBAS DE RANKING DE EQUIPOS ===")
    
    # Probar funciones de ranking
    success_ranking = probar_funciones_ranking()
    
    # Probar guardado en BD (opcional)
    success_bd = probar_guardado_bd()
    
    logger.info("=== RESUMEN DE PRUEBAS ===")
    logger.info(f"Funciones de ranking: {'✓ EXITOSO' if success_ranking else '✗ FALLIDO'}")
    logger.info(f"Guardado en BD: {'✓ EXITOSO' if success_bd else '⚠ OMITIDO/ERROR'}")
    
    if success_ranking:
        logger.info("✓ Las funciones de ranking están funcionando correctamente")
    else:
        logger.error("✗ Hay problemas con las funciones de ranking") 