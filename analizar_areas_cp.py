#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import ast

def analizar_areas_cp():
    """Analiza las variables CP por área específica"""
    
    # Cargar datos
    df_cp = pd.read_csv('ranking_cp.csv')
    
    print("=== ANÁLISIS DE VARIABLES CP POR ÁREA ===")
    print("=" * 60)
    
    # Extraer áreas únicas
    areas_unicas = set()
    for areas_str in df_cp['areas_cp']:
        try:
            if isinstance(areas_str, str):
                areas = ast.literal_eval(areas_str)
                if isinstance(areas, list):
                    areas_unicas.update(areas)
                else:
                    areas_unicas.add(areas)
            else:
                areas_unicas.add(areas_str)
        except:
            areas_unicas.add(str(areas_str))
    
    print(f"\n📊 ÁREAS CP ENCONTRADAS: {len(areas_unicas)}")
    print("-" * 40)
    for area in sorted(areas_unicas):
        print(f"  • {area}")
    
    print(f"\n🔍 ANÁLISIS DETALLADO POR ÁREA:")
    print("=" * 60)
    
    # Analizar cada área
    for area in sorted(areas_unicas):
        print(f"\n📋 ÁREA: {area}")
        print("-" * 40)
        
        # Filtrar equipos que tienen esta área
        equipos_area = []
        for idx, row in df_cp.iterrows():
            areas_equipo = row['areas_cp']
            try:
                if isinstance(areas_equipo, str):
                    areas_list = ast.literal_eval(areas_equipo)
                    if isinstance(areas_list, list) and area in areas_list:
                        equipos_area.append(row)
                    elif areas_list == area:
                        equipos_area.append(row)
                elif areas_equipo == area:
                    equipos_area.append(row)
            except:
                if str(areas_equipo) == area:
                    equipos_area.append(row)
        
        if not equipos_area:
            print(f"  ❌ No se encontraron equipos para esta área")
            continue
        
        df_area = pd.DataFrame(equipos_area)
        print(f"  📊 Equipos en esta área: {len(df_area)}")
        
        # Estadísticas por área
        print(f"\n  📈 ESTADÍSTICAS CP_LLENADO:")
        print(f"    Min: {df_area['cp_llenado'].min():.2f}")
        print(f"    Max: {df_area['cp_llenado'].max():.2f}")
        print(f"    Promedio: {df_area['cp_llenado'].mean():.2f}")
        print(f"    Mediana: {df_area['cp_llenado'].median():.2f}")
        print(f"    Q1: {df_area['cp_llenado'].quantile(0.25):.2f}")
        print(f"    Q3: {df_area['cp_llenado'].quantile(0.75):.2f}")
        
        print(f"\n  📈 ESTADÍSTICAS CP_INESTABILIDAD:")
        print(f"    Min: {df_area['cp_inestabilidad'].min():.2f}")
        print(f"    Max: {df_area['cp_inestabilidad'].max():.2f}")
        print(f"    Promedio: {df_area['cp_inestabilidad'].mean():.2f}")
        print(f"    Mediana: {df_area['cp_inestabilidad'].median():.2f}")
        
        print(f"\n  📈 ESTADÍSTICAS CP_TASA_CAMBIO:")
        print(f"    Min: {df_area['cp_tasa_cambio'].min():.2f}")
        print(f"    Max: {df_area['cp_tasa_cambio'].max():.2f}")
        print(f"    Promedio: {df_area['cp_tasa_cambio'].mean():.2f}")
        print(f"    Mediana: {df_area['cp_tasa_cambio'].median():.2f}")
        
        # Top 5 equipos por área
        print(f"\n  🏆 TOP 5 EQUIPOS EN {area}:")
        top_equipos = df_area.nlargest(5, 'score_final')[['equipo', 'cp_llenado', 'cp_inestabilidad', 'cp_tasa_cambio', 'score_final']]
        print(top_equipos.to_string(index=False))
        
        # Peores 5 equipos por área
        print(f"\n  ⚠️  PEORES 5 EQUIPOS EN {area}:")
        peores_equipos = df_area.nsmallest(5, 'score_final')[['equipo', 'cp_llenado', 'cp_inestabilidad', 'cp_tasa_cambio', 'score_final']]
        print(peores_equipos.to_string(index=False))
        
        # Análisis de distribución de puntajes
        print(f"\n  📊 DISTRIBUCIÓN DE PUNTAJES:")
        categorias = df_area['categoria'].value_counts()
        for cat, count in categorias.items():
            porcentaje = (count / len(df_area)) * 100
            print(f"    {cat}: {count} equipos ({porcentaje:.1f}%)")
    
    # Análisis de equipos con múltiples áreas
    print(f"\n🔍 ANÁLISIS DE EQUIPOS CON MÚLTIPLES ÁREAS:")
    print("=" * 60)
    
    equipos_multiples_areas = []
    for idx, row in df_cp.iterrows():
        areas_equipo = row['areas_cp']
        try:
            if isinstance(areas_equipo, str):
                areas_list = ast.literal_eval(areas_equipo)
                if isinstance(areas_list, list) and len(areas_list) > 1:
                    equipos_multiples_areas.append(row)
        except:
            pass
    
    if equipos_multiples_areas:
        df_multiples = pd.DataFrame(equipos_multiples_areas)
        print(f"  📊 Equipos con múltiples áreas: {len(df_multiples)}")
        print(f"  📈 Puntaje promedio: {df_multiples['score_final'].mean():.2f}")
        print(f"  📈 Puntaje mediano: {df_multiples['score_final'].median():.2f}")
        
        print(f"\n  📋 EJEMPLOS DE EQUIPOS CON MÚLTIPLES ÁREAS:")
        for idx, row in df_multiples.head(5).iterrows():
            print(f"    Equipo {row['equipo']}: {row['areas_cp']} - Puntaje: {row['score_final']:.2f}")
    else:
        print("  ❌ No se encontraron equipos con múltiples áreas")
    
    # Recomendaciones por área
    print(f"\n💡 RECOMENDACIONES POR ÁREA:")
    print("=" * 60)
    
    for area in sorted(areas_unicas):
        equipos_area = []
        for idx, row in df_cp.iterrows():
            areas_equipo = row['areas_cp']
            try:
                if isinstance(areas_equipo, str):
                    areas_list = ast.literal_eval(areas_equipo)
                    if isinstance(areas_list, list) and area in areas_list:
                        equipos_area.append(row)
                    elif areas_list == area:
                        equipos_area.append(row)
                elif areas_equipo == area:
                    equipos_area.append(row)
            except:
                if str(areas_equipo) == area:
                    equipos_area.append(row)
        
        if not equipos_area:
            continue
            
        df_area = pd.DataFrame(equipos_area)
        
        print(f"\n📋 ÁREA: {area}")
        print(f"  📊 Total equipos: {len(df_area)}")
        
        # Analizar si higher_better es apropiado para CP_LLENADO
        llenado_mediana = df_area['cp_llenado'].median()
        llenado_promedio = df_area['cp_llenado'].mean()
        
        print(f"  📈 CP_LLENADO - Mediana: {llenado_mediana:.2f}, Promedio: {llenado_promedio:.2f}")
        
        # Verificar si hay valores extremos que distorsionen el análisis
        q1_llenado = df_area['cp_llenado'].quantile(0.25)
        q3_llenado = df_area['cp_llenado'].quantile(0.75)
        iqr_llenado = q3_llenado - q1_llenado
        
        print(f"  📊 Rango normal (Q1-Q3): {q1_llenado:.2f} - {q3_llenado:.2f}")
        
        # Identificar outliers
        outliers_superiores = df_area[df_area['cp_llenado'] > q3_llenado + 1.5 * iqr_llenado]
        outliers_inferiores = df_area[df_area['cp_llenado'] < q1_llenado - 1.5 * iqr_llenado]
        
        if len(outliers_superiores) > 0:
            print(f"  ⚠️  Outliers superiores: {len(outliers_superiores)} equipos")
            print(f"     Valores: {outliers_superiores['cp_llenado'].tolist()}")
        
        if len(outliers_inferiores) > 0:
            print(f"  ⚠️  Outliers inferiores: {len(outliers_inferiores)} equipos")
            print(f"     Valores: {outliers_inferiores['cp_llenado'].tolist()}")
        
        # Recomendación para la dirección de puntuación
        if len(outliers_superiores) > len(outliers_inferiores):
            print(f"  💡 RECOMENDACIÓN: Considerar 'lower_better' para CP_LLENADO en {area}")
            print(f"     Razón: Más outliers superiores, posible distorsión")
        else:
            print(f"  💡 RECOMENDACIÓN: 'higher_better' puede ser apropiado para {area}")
            print(f"     Razón: Distribución más equilibrada")

if __name__ == "__main__":
    analizar_areas_cp() 