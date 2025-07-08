#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mostrar Resultados Ranking HDD - Visualización de rankings de unidades HDD
==========================================================================

Este script muestra los resultados de los rankings de unidades de disco duro
guardados en la tabla nv_hdd_analisis_datos_v2.

Autor: Sistema de Análisis HDD
Fecha: 2025
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('mostrar_ranking_hdd')

# Añadir el directorio src al sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)
sys.path.insert(0, project_root)

try:
    from hdd_db_manager import get_db_manager
    from hdd_ranking_functions import obtener_resumen_rankings
except ImportError as e:
    print(f"Error importando módulos: {e}")
    sys.exit(1)

def obtener_rankings_guardados():
    """
    Obtiene los rankings guardados en la base de datos.
    
    Returns:
        DataFrame con los rankings
    """
    try:
        logger.info("Obteniendo rankings guardados en la base de datos...")
        
        db_manager = get_db_manager()
        rankings = db_manager.obtener_rankings()
        
        if rankings.empty:
            logger.warning("No se encontraron rankings guardados en la base de datos")
            return pd.DataFrame()
        
        logger.info(f"Rankings obtenidos: {len(rankings)} registros")
        return rankings
        
    except Exception as e:
        logger.error(f"Error obteniendo rankings: {str(e)}")
        return pd.DataFrame()

def mostrar_resumen_general(rankings):
    """
    Muestra un resumen general de los rankings.
    
    Args:
        rankings: DataFrame con los rankings
    """
    try:
        print("\n" + "="*80)
        print("RESUMEN GENERAL DE RANKINGS HDD")
        print("="*80)
        
        # Información básica
        print(f"Total de registros: {len(rankings)}")
        print(f"Tipos de ranking: {rankings['tipo_ranking'].nunique()}")
        print(f"Parejas equipo-unidad únicas: {rankings.groupby(['equipo', 'unidad']).size().shape[0]}")
        print(f"Equipos únicos: {rankings['equipo'].nunique()}")
        print(f"Unidades únicas: {rankings['unidad'].nunique()}")
        
        # Fechas de análisis
        if 'fecha_analisis' in rankings.columns:
            fechas_unicas = rankings['fecha_analisis'].dt.date.unique()
            print(f"Fechas de análisis: {len(fechas_unicas)}")
            for fecha in sorted(fechas_unicas)[-3:]:  # Últimas 3 fechas
                print(f"  - {fecha}")
        
        # Resumen por tipo de ranking
        print("\nResumen por tipo de ranking:")
        for tipo in sorted(rankings['tipo_ranking'].unique()):
            df_tipo = rankings[rankings['tipo_ranking'] == tipo]
            print(f"  {tipo.upper()}: {len(df_tipo)} registros")
        
        print("="*80)
        
    except Exception as e:
        logger.error(f"Error mostrando resumen general: {str(e)}")

def mostrar_ranking_detallado(rankings, tipo_ranking):
    """
    Muestra un ranking específico de forma detallada.
    
    Args:
        rankings: DataFrame con los rankings
        tipo_ranking: Tipo de ranking a mostrar
    """
    try:
        df_tipo = rankings[rankings['tipo_ranking'] == tipo_ranking].copy()
        
        if df_tipo.empty:
            print(f"\n❌ No hay datos para el ranking '{tipo_ranking}'")
            return
        
        # Ordenar por posición
        df_tipo = df_tipo.sort_values('posicion')
        
        print(f"\n" + "="*60)
        print(f"RANKING DE {tipo_ranking.upper()}")
        print("="*60)
        
        # Mostrar top 10
        print(f"\nTOP 10 PAREJAS EQUIPO-UNIDAD:")
        print("-" * 60)
        for _, row in df_tipo.head(10).iterrows():
            print(f"{row['posicion']:2d}. {row['equipo']:<15} - {row['unidad']:<15} - Valor: {row['valor_metrico']:10.4f}")
        
        # Mostrar bottom 10 si hay más de 10 registros
        if len(df_tipo) > 10:
            print(f"\nÚLTIMAS 10 PAREJAS EQUIPO-UNIDAD:")
            print("-" * 60)
            for _, row in df_tipo.tail(10).iterrows():
                print(f"{row['posicion']:2d}. {row['equipo']:<15} - {row['unidad']:<15} - Valor: {row['valor_metrico']:10.4f}")
        
        # Estadísticas
        print(f"\nESTADÍSTICAS:")
        print("-" * 30)
        print(f"Total parejas equipo-unidad: {len(df_tipo)}")
        print(f"Mejor valor: {df_tipo['valor_metrico'].max():.4f}")
        print(f"Peor valor: {df_tipo['valor_metrico'].min():.4f}")
        print(f"Promedio: {df_tipo['valor_metrico'].mean():.4f}")
        print(f"Desviación estándar: {df_tipo['valor_metrico'].std():.4f}")
        
    except Exception as e:
        logger.error(f"Error mostrando ranking detallado: {str(e)}")

def mostrar_comparacion_rankings(rankings):
    """
    Muestra una comparación entre diferentes tipos de ranking.
    
    Args:
        rankings: DataFrame con los rankings
    """
    try:
        print(f"\n" + "="*80)
        print("COMPARACIÓN ENTRE RANKINGS")
        print("="*80)
        
        # Obtener parejas equipo-unidad que aparecen en todos los rankings
        tipos_ranking = rankings['tipo_ranking'].unique()
        parejas_comunes = set()
        
        # Obtener todas las parejas equipo-unidad
        todas_parejas = set(zip(rankings['equipo'], rankings['unidad']))
        
        for tipo in tipos_ranking:
            df_tipo = rankings[rankings['tipo_ranking'] == tipo]
            parejas_tipo = set(zip(df_tipo['equipo'], df_tipo['unidad']))
            if not parejas_comunes:
                parejas_comunes = parejas_tipo
            else:
                parejas_comunes = parejas_comunes.intersection(parejas_tipo)
        
        if not parejas_comunes:
            print("❌ No hay parejas equipo-unidad comunes en todos los rankings")
            return
        
        print(f"Parejas equipo-unidad analizadas: {len(parejas_comunes)}")
        print(f"Tipos de ranking: {len(tipos_ranking)}")
        
        # Crear tabla comparativa
        print(f"\nTABLA COMPARATIVA (TOP 5):")
        print("-" * 100)
        
        # Encabezado
        header = f"{'Equipo':<15} {'Unidad':<15}"
        for tipo in sorted(tipos_ranking):
            header += f" | {tipo.upper():<12}"
        print(header)
        print("-" * 100)
        
        # Obtener top 5 del ranking combinado
        df_combinado = rankings[rankings['tipo_ranking'] == 'combinado'].sort_values('posicion')
        top_5_parejas = list(zip(df_combinado.head(5)['equipo'], df_combinado.head(5)['unidad']))
        
        for equipo, unidad in top_5_parejas:
            row = f"{equipo:<15} {unidad:<15}"
            for tipo in sorted(tipos_ranking):
                df_tipo = rankings[(rankings['tipo_ranking'] == tipo) & 
                                 (rankings['equipo'] == equipo) & 
                                 (rankings['unidad'] == unidad)]
                if not df_tipo.empty:
                    posicion = df_tipo.iloc[0]['posicion']
                    row += f" | {posicion:>2d}° lugar"
                else:
                    row += f" | {'N/A':>12}"
            print(row)
        
    except Exception as e:
        logger.error(f"Error mostrando comparación: {str(e)}")

def mostrar_analisis_tendencias(rankings):
    """
    Muestra análisis de tendencias en los rankings.
    
    Args:
        rankings: DataFrame con los rankings
    """
    try:
        print(f"\n" + "="*80)
        print("ANÁLISIS DE TENDENCIAS")
        print("="*80)
        
        # Análisis por tipo de ranking
        for tipo in sorted(rankings['tipo_ranking'].unique()):
            df_tipo = rankings[rankings['tipo_ranking'] == tipo]
            
            print(f"\n{tipo.upper()}:")
            print("-" * 40)
            
            # Distribución de valores
            print(f"Distribución de valores:")
            print(f"  Mínimo: {df_tipo['valor_metrico'].min():.4f}")
            print(f"  Q1: {df_tipo['valor_metrico'].quantile(0.25):.4f}")
            print(f"  Mediana: {df_tipo['valor_metrico'].median():.4f}")
            print(f"  Q3: {df_tipo['valor_metrico'].quantile(0.75):.4f}")
            print(f"  Máximo: {df_tipo['valor_metrico'].max():.4f}")
            
            # Unidades destacadas
            mejor_unidad = df_tipo.loc[df_tipo['valor_metrico'].idxmax()]
            peor_unidad = df_tipo.loc[df_tipo['valor_metrico'].idxmin()]
            
            print(f"\nUnidades destacadas:")
            print(f"  Mejor: {mejor_unidad['unidad']} (valor: {mejor_unidad['valor_metrico']:.4f})")
            print(f"  Peor: {peor_unidad['unidad']} (valor: {peor_unidad['valor_metrico']:.4f})")
        
    except Exception as e:
        logger.error(f"Error mostrando análisis de tendencias: {str(e)}")

def main():
    """
    Función principal del script.
    """
    try:
        print("🔍 MOSTRANDO RESULTADOS DE RANKINGS HDD")
        print("="*60)
        
        # Obtener rankings guardados
        rankings = obtener_rankings_guardados()
        
        if rankings.empty:
            print("❌ No hay rankings para mostrar")
            return False
        
        # Mostrar resumen general
        mostrar_resumen_general(rankings)
        
        # Mostrar rankings detallados
        tipos_ranking = sorted(rankings['tipo_ranking'].unique())
        
        for tipo in tipos_ranking:
            mostrar_ranking_detallado(rankings, tipo)
        
        # Mostrar comparación
        mostrar_comparacion_rankings(rankings)
        
        # Mostrar análisis de tendencias
        mostrar_analisis_tendencias(rankings)
        
        print(f"\n" + "="*80)
        print("ANÁLISIS COMPLETADO")
        print("="*80)
        
        return True
        
    except Exception as e:
        logger.error(f"Error en la ejecución principal: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Análisis de resultados completado exitosamente")
    else:
        print("\n❌ Error en el análisis de resultados")
        sys.exit(1) 