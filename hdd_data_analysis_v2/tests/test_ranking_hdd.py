#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Ranking HDD - Pruebas de funciones de ranking para HDD
==========================================================

Este script prueba las funciones de ranking de unidades de disco duro
usando datos simulados para verificar su funcionamiento correcto.

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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('test_ranking_hdd')

# Importar funciones de ranking
from hdd_ranking_functions import (
    generar_ranking_uso,
    generar_ranking_inestabilidad,
    generar_ranking_tasa_cambio,
    generar_ranking_combinado,
    generar_rankings_completos,
    obtener_resumen_rankings
)

def crear_datos_simulados_hdd():
    """
    Crea datos simulados de unidades de disco duro para pruebas.
    
    Returns:
        DataFrame con datos simulados de HDD
    """
    try:
        logger.info("Creando datos simulados de HDD...")
        
        # Configurar semilla para reproducibilidad
        np.random.seed(42)
        
        # Parámetros de simulación
        unidades = ['HDD_001', 'HDD_002', 'HDD_003', 'HDD_004', 'HDD_005']
        equipos = ['EQUIPO_A', 'EQUIPO_B', 'EQUIPO_C', 'EQUIPO_D', 'EQUIPO_E']
        
        # Generar fechas (últimos 7 días)
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=7)
        fechas = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='H')
        
        # Crear datos simulados
        datos = []
        
        for fecha in fechas:
            for unidad in unidades:
                for equipo in equipos:
                    # Simular diferentes patrones de uso
                    if unidad == 'HDD_001':
                        # HDD con uso alto y estable
                        uso = np.random.normal(85, 5)
                    elif unidad == 'HDD_002':
                        # HDD con uso medio y algo inestable
                        uso = np.random.normal(60, 15)
                    elif unidad == 'HDD_003':
                        # HDD con uso bajo y muy inestable
                        uso = np.random.normal(30, 25)
                    elif unidad == 'HDD_004':
                        # HDD con uso variable
                        uso = np.random.normal(50, 20)
                    else:  # HDD_005
                        # HDD con uso muy bajo y estable
                        uso = np.random.normal(20, 3)
                    
                    # Asegurar que el uso esté en rango válido (0-100)
                    uso = max(0, min(100, uso))
                    
                    datos.append({
                        'codigo': f'CODE_{unidad}_{equipo}',
                        'fecha': fecha,
                        'equipo': equipo,
                        'unidad': unidad,
                        'uso': uso
                    })
        
        # Crear DataFrame
        df = pd.DataFrame(datos)
        
        logger.info(f"Datos simulados creados: {len(df)} registros")
        logger.info(f"Unidades: {df['unidad'].nunique()}")
        logger.info(f"Equipos: {df['equipo'].nunique()}")
        logger.info(f"Rango de fechas: {df['fecha'].min()} a {df['fecha'].max()}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error creando datos simulados: {str(e)}")
        return pd.DataFrame()

def probar_ranking_uso(datos):
    """
    Prueba la función de ranking de uso.
    
    Args:
        datos: DataFrame con datos simulados
    """
    try:
        logger.info("\n" + "="*50)
        logger.info("PROBANDO RANKING DE USO")
        logger.info("="*50)
        
        ranking = generar_ranking_uso(datos)
        
        if ranking.empty:
            logger.error("❌ Ranking de uso está vacío")
            return False
        
        logger.info(f"✅ Ranking de uso generado: {len(ranking)} unidades")
        
        # Mostrar resultados
        logger.info("\nTop 5 parejas equipo-unidad por uso:")
        for _, row in ranking.head(5).iterrows():
            logger.info(f"  {row['posicion']:2d}. {row['equipo']:<10} - {row['unidad']:<10} - Uso: {row['valor_metrico']:6.2f}%")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en ranking de uso: {str(e)}")
        return False

def probar_ranking_inestabilidad(datos):
    """
    Prueba la función de ranking de inestabilidad.
    
    Args:
        datos: DataFrame con datos simulados
    """
    try:
        logger.info("\n" + "="*50)
        logger.info("PROBANDO RANKING DE INESTABILIDAD")
        logger.info("="*50)
        
        ranking = generar_ranking_inestabilidad(datos)
        
        if ranking.empty:
            logger.error("❌ Ranking de inestabilidad está vacío")
            return False
        
        logger.info(f"✅ Ranking de inestabilidad generado: {len(ranking)} unidades")
        
        # Mostrar resultados (menor valor = más estable)
        logger.info("\nTop 5 parejas equipo-unidad más estables:")
        for _, row in ranking.head(5).iterrows():
            logger.info(f"  {row['posicion']:2d}. {row['equipo']:<10} - {row['unidad']:<10} - Inestabilidad: {row['valor_metrico']:8.2f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en ranking de inestabilidad: {str(e)}")
        return False

def probar_ranking_tasa_cambio(datos):
    """
    Prueba la función de ranking de tasa de cambio.
    
    Args:
        datos: DataFrame con datos simulados
    """
    try:
        logger.info("\n" + "="*50)
        logger.info("PROBANDO RANKING DE TASA DE CAMBIO")
        logger.info("="*50)
        
        ranking = generar_ranking_tasa_cambio(datos)
        
        if ranking.empty:
            logger.error("❌ Ranking de tasa de cambio está vacío")
            return False
        
        logger.info(f"✅ Ranking de tasa de cambio generado: {len(ranking)} unidades")
        
        # Mostrar resultados (menor valor = más estable)
        logger.info("\nTop 5 parejas equipo-unidad con cambios más predecibles:")
        for _, row in ranking.head(5).iterrows():
            logger.info(f"  {row['posicion']:2d}. {row['equipo']:<10} - {row['unidad']:<10} - Tasa cambio: {row['valor_metrico']:10.2f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en ranking de tasa de cambio: {str(e)}")
        return False

def probar_ranking_combinado(datos):
    """
    Prueba la función de ranking combinado.
    
    Args:
        datos: DataFrame con datos simulados
    """
    try:
        logger.info("\n" + "="*50)
        logger.info("PROBANDO RANKING COMBINADO")
        logger.info("="*50)
        
        ranking = generar_ranking_combinado(datos)
        
        if ranking.empty:
            logger.error("❌ Ranking combinado está vacío")
            return False
        
        logger.info(f"✅ Ranking combinado generado: {len(ranking)} parejas equipo-unidad")
        
        # Mostrar resultados
        logger.info("\nTop 5 parejas equipo-unidad en ranking combinado:")
        for _, row in ranking.head(5).iterrows():
            logger.info(f"  {row['posicion']:2d}. {row['equipo']:<10} - {row['unidad']:<10} - Puntuación: {row['valor_metrico']:6.4f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en ranking combinado: {str(e)}")
        return False

def probar_rankings_completos(datos):
    """
    Prueba la generación de todos los rankings.
    
    Args:
        datos: DataFrame con datos simulados
    """
    try:
        logger.info("\n" + "="*50)
        logger.info("PROBANDO RANKINGS COMPLETOS")
        logger.info("="*50)
        
        rankings = generar_rankings_completos(datos)
        
        if not rankings:
            logger.error("❌ No se pudieron generar rankings completos")
            return False
        
        logger.info(f"✅ Rankings completos generados: {len(rankings)} tipos")
        
        # Mostrar resumen
        resumen = obtener_resumen_rankings(rankings)
        logger.info("\nResumen de rankings:")
        for key, value in resumen.items():
            logger.info(f"  {key}: {value}")
        
        # Mostrar estadísticas por tipo
        for tipo, df in rankings.items():
            if not df.empty:
                logger.info(f"\n{tipo.upper()}:")
                logger.info(f"  Total parejas equipo-unidad: {len(df)}")
                logger.info(f"  Mejor pareja: {df.iloc[0]['equipo']} - {df.iloc[0]['unidad']} (valor: {df.iloc[0]['valor_metrico']:.4f})")
                logger.info(f"  Peor pareja: {df.iloc[-1]['equipo']} - {df.iloc[-1]['unidad']} (valor: {df.iloc[-1]['valor_metrico']:.4f})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en rankings completos: {str(e)}")
        return False

def main():
    """
    Función principal de pruebas.
    """
    try:
        logger.info("🚀 INICIANDO PRUEBAS DE RANKING HDD")
        logger.info("="*60)
        
        # Crear datos simulados
        datos = crear_datos_simulados_hdd()
        
        if datos.empty:
            logger.error("No se pudieron crear datos simulados")
            return False
        
        # Ejecutar pruebas
        pruebas = [
            ("Ranking de Uso", lambda: probar_ranking_uso(datos)),
            ("Ranking de Inestabilidad", lambda: probar_ranking_inestabilidad(datos)),
            ("Ranking de Tasa de Cambio", lambda: probar_ranking_tasa_cambio(datos)),
            ("Ranking Combinado", lambda: probar_ranking_combinado(datos)),
            ("Rankings Completos", lambda: probar_rankings_completos(datos))
        ]
        
        resultados = []
        
        for nombre_prueba, funcion_prueba in pruebas:
            try:
                resultado = funcion_prueba()
                resultados.append((nombre_prueba, resultado))
                status = "✅ EXITOSA" if resultado else "❌ FALLIDA"
                logger.info(f"{nombre_prueba}: {status}")
            except Exception as e:
                logger.error(f"Error en {nombre_prueba}: {str(e)}")
                resultados.append((nombre_prueba, False))
        
        # Resumen final
        logger.info("\n" + "="*60)
        logger.info("RESUMEN DE PRUEBAS")
        logger.info("="*60)
        
        exitos = sum(1 for _, resultado in resultados if resultado)
        total = len(resultados)
        
        for nombre, resultado in resultados:
            status = "✅ EXITOSA" if resultado else "❌ FALLIDA"
            logger.info(f"{nombre:<25} {status}")
        
        logger.info(f"\nResultado: {exitos}/{total} pruebas exitosas")
        
        if exitos == total:
            logger.info("🎉 ¡Todas las pruebas pasaron! Las funciones de ranking funcionan correctamente.")
            return True
        else:
            logger.warning("⚠️ Algunas pruebas fallaron. Revisa los errores.")
            return False
        
    except Exception as e:
        logger.error(f"Error en la ejecución principal: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Pruebas de ranking HDD completadas exitosamente")
    else:
        print("\n❌ Algunas pruebas de ranking HDD fallaron")
        sys.exit(1) 