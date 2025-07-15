#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import ast

def analizar_areas_individuales():
    """Analiza cada área CP individualmente para entender su significado"""
    
    # Cargar datos originales de CP
    try:
        # Intentar cargar datos originales de CP
        df_cp_original = pd.read_csv('cp_data_analysis_v2/data/cp_data.csv')
        print("✅ Datos originales CP cargados")
    except:
        print("❌ No se encontraron datos originales CP")
        return
    
    print("=== ANÁLISIS DE ÁREAS CP INDIVIDUALES ===")
    print("=" * 60)
    
    # Lista de áreas CP
    areas_cp = ['PP_NFD', 'IOLOAD', 'totmem', 'CUMOVR', 'OMOVRN', 'TLCONS', 'OMLDAV', 'CPLOAD', 'MAXMEM']
    
    print(f"\n📋 ÁREAS CP IDENTIFICADAS: {len(areas_cp)}")
    print("-" * 40)
    
    for i, area in enumerate(areas_cp, 1):
        print(f"{i}. {area}")
    
    print("\n🔍 ANÁLISIS POR ÁREA:")
    print("=" * 60)
    
    for area in areas_cp:
        if area in df_cp_original.columns:
            print(f"\n📊 ÁREA: {area}")
            print("-" * 30)
            
            # Estadísticas básicas
            valores = df_cp_original[area].dropna()
            print(f"   Total registros: {len(valores)}")
            print(f"   Min: {valores.min():.2f}")
            print(f"   Max: {valores.max():.2f}")
            print(f"   Promedio: {valores.mean():.2f}")
            print(f"   Mediana: {valores.median():.2f}")
            print(f"   Q1: {valores.quantile(0.25):.2f}")
            print(f"   Q3: {valores.quantile(0.75):.2f}")
            
            # Análisis de distribución
            print(f"   Desv. Estándar: {valores.std():.2f}")
            
            # Interpretación basada en el nombre
            interpretacion = interpretar_area(area)
            print(f"   📝 Interpretación: {interpretacion}")
            
            # Recomendación de evaluación
            recomendacion = recomendar_evaluacion(area, valores)
            print(f"   💡 Recomendación: {recomendacion}")
        else:
            print(f"\n❌ ÁREA: {area} - No encontrada en datos")

def interpretar_area(area):
    """Interpreta el significado de cada área basándose en su nombre"""
    
    interpretaciones = {
        'PP_NFD': "Procesamiento de archivos no encontrados (Not Found) - Menor es mejor",
        'IOLOAD': "Carga de entrada/salida (I/O Load) - Menor es mejor",
        'totmem': "Memoria total utilizada - Menor es mejor",
        'CUMOVR': "Cumulative Overhead - Sobrecarga acumulativa - Menor es mejor",
        'OMOVRN': "Overhead de memoria - Menor es mejor",
        'TLCONS': "Tiempo de respuesta de consola - Menor es mejor",
        'OMLDAV': "Carga promedio de memoria - Menor es mejor",
        'CPLOAD': "Carga del procesador (CPU Load) - Menor es mejor",
        'MAXMEM': "Memoria máxima utilizada - Menor es mejor"
    }
    
    return interpretaciones.get(area, "Significado no determinado")

def recomendar_evaluacion(area, valores):
    """Recomienda cómo evaluar cada área"""
    
    # Calcular percentiles para entender la distribución
    p25 = valores.quantile(0.25)
    p50 = valores.quantile(0.50)
    p75 = valores.quantile(0.75)
    
    recomendaciones = {
        'PP_NFD': f"Evaluar por percentiles inversos (menor=mejor). P25={p25:.2f}, P50={p50:.2f}, P75={p75:.2f}",
        'IOLOAD': f"Evaluar por percentiles inversos (menor=mejor). P25={p25:.2f}, P50={p50:.2f}, P75={p75:.2f}",
        'totmem': f"Evaluar por percentiles inversos (menor=mejor). P25={p25:.2f}, P50={p50:.2f}, P75={p75:.2f}",
        'CUMOVR': f"Evaluar por percentiles inversos (menor=mejor). P25={p25:.2f}, P50={p50:.2f}, P75={p75:.2f}",
        'OMOVRN': f"Evaluar por percentiles inversos (menor=mejor). P25={p25:.2f}, P50={p50:.2f}, P75={p75:.2f}",
        'TLCONS': f"Evaluar por percentiles inversos (menor=mejor). P25={p25:.2f}, P50={p50:.2f}, P75={p75:.2f}",
        'OMLDAV': f"Evaluar por percentiles inversos (menor=mejor). P25={p25:.2f}, P50={p50:.2f}, P75={p75:.2f}",
        'CPLOAD': f"Evaluar por percentiles inversos (menor=mejor). P25={p25:.2f}, P50={p50:.2f}, P75={p75:.2f}",
        'MAXMEM': f"Evaluar por percentiles inversos (menor=mejor). P25={p25:.2f}, P50={p50:.2f}, P75={p75:.2f}"
    }
    
    return recomendaciones.get(area, "Evaluación estándar")

if __name__ == "__main__":
    analizar_areas_individuales() 