#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

def analizar_rangos():
    """Analiza los rangos de valores de las métricas CP y HDD"""
    
    # Cargar datos
    df_cp = pd.read_csv('ranking_cp.csv')
    df_hdd = pd.read_csv('ranking_hdd.csv')
    
    print("=== ANÁLISIS DE RANGOS DE VALORES ===")
    
    print("\n📊 MÉTRICAS CP:")
    print("-" * 50)
    
    print("\n1. CP LLENADO:")
    print(f"   Min: {df_cp['cp_llenado'].min():.2f}")
    print(f"   Max: {df_cp['cp_llenado'].max():.2f}")
    print(f"   Promedio: {df_cp['cp_llenado'].mean():.2f}")
    print(f"   Mediana: {df_cp['cp_llenado'].median():.2f}")
    print(f"   Q1: {df_cp['cp_llenado'].quantile(0.25):.2f}")
    print(f"   Q3: {df_cp['cp_llenado'].quantile(0.75):.2f}")
    
    print("\n2. CP INESTABILIDAD:")
    print(f"   Min: {df_cp['cp_inestabilidad'].min():.2f}")
    print(f"   Max: {df_cp['cp_inestabilidad'].max():.2f}")
    print(f"   Promedio: {df_cp['cp_inestabilidad'].mean():.2f}")
    print(f"   Mediana: {df_cp['cp_inestabilidad'].median():.2f}")
    print(f"   Q1: {df_cp['cp_inestabilidad'].quantile(0.25):.2f}")
    print(f"   Q3: {df_cp['cp_inestabilidad'].quantile(0.75):.2f}")
    
    print("\n3. CP TASA CAMBIO:")
    print(f"   Min: {df_cp['cp_tasa_cambio'].min():.2f}")
    print(f"   Max: {df_cp['cp_tasa_cambio'].max():.2f}")
    print(f"   Promedio: {df_cp['cp_tasa_cambio'].mean():.2f}")
    print(f"   Mediana: {df_cp['cp_tasa_cambio'].median():.2f}")
    print(f"   Q1: {df_cp['cp_tasa_cambio'].quantile(0.25):.2f}")
    print(f"   Q3: {df_cp['cp_tasa_cambio'].quantile(0.75):.2f}")
    
    print("\n💾 MÉTRICAS HDD:")
    print("-" * 50)
    
    print("\n1. HDD USO (%):")
    print(f"   Min: {df_hdd['hdd_uso'].min():.2f}%")
    print(f"   Max: {df_hdd['hdd_uso'].max():.2f}%")
    print(f"   Promedio: {df_hdd['hdd_uso'].mean():.2f}%")
    print(f"   Mediana: {df_hdd['hdd_uso'].median():.2f}%")
    print(f"   Q1: {df_hdd['hdd_uso'].quantile(0.25):.2f}%")
    print(f"   Q3: {df_hdd['hdd_uso'].quantile(0.75):.2f}%")
    
    print("\n2. HDD INESTABILIDAD:")
    print(f"   Min: {df_hdd['hdd_inestabilidad'].min():.6f}")
    print(f"   Max: {df_hdd['hdd_inestabilidad'].max():.6f}")
    print(f"   Promedio: {df_hdd['hdd_inestabilidad'].mean():.6f}")
    print(f"   Mediana: {df_hdd['hdd_inestabilidad'].median():.6f}")
    print(f"   Q1: {df_hdd['hdd_inestabilidad'].quantile(0.25):.6f}")
    print(f"   Q3: {df_hdd['hdd_inestabilidad'].quantile(0.75):.6f}")
    
    print("\n3. HDD TASA CAMBIO:")
    print(f"   Min: {df_hdd['hdd_tasa_cambio'].min():.2f}")
    print(f"   Max: {df_hdd['hdd_tasa_cambio'].max():.2f}")
    print(f"   Promedio: {df_hdd['hdd_tasa_cambio'].mean():.2f}")
    print(f"   Mediana: {df_hdd['hdd_tasa_cambio'].median():.2f}")
    print(f"   Q1: {df_hdd['hdd_tasa_cambio'].quantile(0.25):.2f}")
    print(f"   Q3: {df_hdd['hdd_tasa_cambio'].quantile(0.75):.2f}")
    
    print("\n🔍 ANÁLISIS DE CONFIGURACIÓN ACTUAL:")
    print("-" * 50)
    
    print("\nCP - Configuración actual:")
    print("   cp_llenado: higher_better (mayor = mejor)")
    print("   cp_inestabilidad: lower_better (menor = mejor)")
    print("   cp_tasa_cambio: lower_better (menor = mejor)")
    
    print("\nHDD - Configuración actual:")
    print("   hdd_uso: lower_better (menor = mejor)")
    print("   hdd_inestabilidad: lower_better (menor = mejor)")
    print("   hdd_tasa_cambio: lower_better (menor = mejor)")
    
    print("\n❓ PREGUNTAS PARA VALIDAR:")
    print("-" * 50)
    print("1. ¿Es correcto que CP_LLENADO sea 'higher_better'?")
    print("   - Valores típicos: 0.76 a 562,708")
    print("   - ¿Mayor ocupación = mejor rendimiento?")
    
    print("\n2. ¿Es correcto que HDD_USO sea 'lower_better'?")
    print("   - Valores típicos: 4.76% a 75.63%")
    print("   - ¿Menor uso = mejor rendimiento?")
    
    print("\n3. ¿Los valores extremos son normales?")
    print("   - CP_TASA_CAMBIO: hasta 2,034,856")
    print("   - HDD_TASA_CAMBIO: hasta 89,776")
    
    # Mostrar algunos ejemplos extremos
    print("\n📋 EJEMPLOS EXTREMOS:")
    print("-" * 50)
    
    print("\nCP - Valores más altos de llenado:")
    top_cp_llenado = df_cp.nlargest(5, 'cp_llenado')[['equipo', 'cp_llenado', 'score_final']]
    print(top_cp_llenado.to_string(index=False))
    
    print("\nCP - Valores más altos de inestabilidad:")
    top_cp_inest = df_cp.nlargest(5, 'cp_inestabilidad')[['equipo', 'cp_inestabilidad', 'score_final']]
    print(top_cp_inest.to_string(index=False))
    
    print("\nHDD - Valores más altos de uso:")
    top_hdd_uso = df_hdd.nlargest(5, 'hdd_uso')[['equipo', 'hdd_uso', 'score_final']]
    print(top_hdd_uso.to_string(index=False))

if __name__ == "__main__":
    analizar_rangos() 