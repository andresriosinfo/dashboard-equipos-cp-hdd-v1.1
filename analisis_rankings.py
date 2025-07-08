#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

def analizar_ranking(df, nombre):
    print(f"\n{'='*60}")
    print(f"ANÁLISIS COMPLETO - RANKING {nombre}")
    print(f"{'='*60}")
    
    # Estadísticas básicas
    print(f"\n📊 ESTADÍSTICAS BÁSICAS:")
    print(f"   Total equipos: {len(df)}")
    print(f"   Score máximo: {df['score_final'].max():.2f}")
    print(f"   Score mínimo: {df['score_final'].min():.2f}")
    print(f"   Score promedio: {df['score_final'].mean():.2f}")
    print(f"   Desviación estándar: {df['score_final'].std():.2f}")
    print(f"   Mediana: {df['score_final'].median():.2f}")
    print(f"   Q1 (25%): {df['score_final'].quantile(0.25):.2f}")
    print(f"   Q3 (75%): {df['score_final'].quantile(0.75):.2f}")
    print(f"   Rango intercuartil: {(df['score_final'].quantile(0.75) - df['score_final'].quantile(0.25)):.2f}")
    
    # Distribución por categorías
    print(f"\n📈 DISTRIBUCIÓN POR CATEGORÍAS:")
    cat_counts = df['categoria'].value_counts()
    for cat, count in cat_counts.items():
        porcentaje = (count / len(df)) * 100
        print(f"   {cat}: {count} equipos ({porcentaje:.1f}%)")
    
    # Top 10 equipos
    print(f"\n🏆 TOP 10 EQUIPOS:")
    top_10 = df.head(10)
    for _, row in top_10.iterrows():
        print(f"   {row['posicion']:2d}. Equipo {row['equipo']:4s} - {row['score_final']:6.2f}pts ({row['categoria']})")
    
    # Peores 10 equipos
    print(f"\n⚠️  PEORES 10 EQUIPOS:")
    peores_10 = df.tail(10)
    for _, row in peores_10.iterrows():
        print(f"   {row['posicion']:2d}. Equipo {row['equipo']:4s} - {row['score_final']:6.2f}pts ({row['categoria']})")
    
    # Análisis de percentiles
    print(f"\n📊 ANÁLISIS DE PERCENTILES:")
    percentiles = [10, 25, 50, 75, 90, 95, 99]
    for p in percentiles:
        valor = df['score_final'].quantile(p/100)
        print(f"   Percentil {p:2d}%: {valor:.2f}pts")
    
    # Equipos destacados
    print(f"\n⭐ EQUIPOS DESTACADOS:")
    excelentes = df[df['categoria'] == 'Excelente']
    if not excelentes.empty:
        print(f"   Equipos Excelentes: {len(excelentes)}")
        for _, row in excelentes.iterrows():
            print(f"     - Equipo {row['equipo']}: {row['score_final']:.2f}pts")
    else:
        print("   No hay equipos en categoría Excelente")
    
    # Equipos que necesitan mejora
    print(f"\n🔧 EQUIPOS QUE NECESITAN MEJORA:")
    mejora = df[df['categoria'] == 'Necesita Mejora']
    if not mejora.empty:
        print(f"   Equipos que necesitan mejora: {len(mejora)}")
        for _, row in mejora.iterrows():
            print(f"     - Equipo {row['equipo']}: {row['score_final']:.2f}pts")
    else:
        print("   No hay equipos que necesiten mejora")

def comparar_rankings(df_cp, df_hdd):
    print(f"\n{'='*60}")
    print("COMPARACIÓN ENTRE RANKINGS CP Y HDD")
    print(f"{'='*60}")
    
    print(f"\n📊 COMPARACIÓN ESTADÍSTICA:")
    print(f"   {'Métrica':<20} {'CP':<15} {'HDD':<15} {'Diferencia':<15}")
    print(f"   {'-'*20} {'-'*15} {'-'*15} {'-'*15}")
    print(f"   {'Total equipos':<20} {len(df_cp):<15} {len(df_hdd):<15} {len(df_hdd)-len(df_cp):<15}")
    print(f"   {'Score máximo':<20} {df_cp['score_final'].max():<15.2f} {df_hdd['score_final'].max():<15.2f} {df_hdd['score_final'].max()-df_cp['score_final'].max():<15.2f}")
    print(f"   {'Score mínimo':<20} {df_cp['score_final'].min():<15.2f} {df_hdd['score_final'].min():<15.2f} {df_hdd['score_final'].min()-df_cp['score_final'].min():<15.2f}")
    print(f"   {'Score promedio':<20} {df_cp['score_final'].mean():<15.2f} {df_hdd['score_final'].mean():<15.2f} {df_hdd['score_final'].mean()-df_cp['score_final'].mean():<15.2f}")
    print(f"   {'Desv. estándar':<20} {df_cp['score_final'].std():<15.2f} {df_hdd['score_final'].std():<15.2f} {df_hdd['score_final'].std()-df_cp['score_final'].std():<15.2f}")
    
    print(f"\n📈 DISTRIBUCIÓN DE CATEGORÍAS:")
    print(f"   {'Categoría':<15} {'CP':<10} {'HDD':<10} {'Total':<10}")
    print(f"   {'-'*15} {'-'*10} {'-'*10} {'-'*10}")
    
    categorias = ['Excelente', 'Muy Bueno', 'Bueno', 'Regular', 'Necesita Mejora']
    for cat in categorias:
        cp_count = len(df_cp[df_cp['categoria'] == cat])
        hdd_count = len(df_hdd[df_hdd['categoria'] == cat])
        total = cp_count + hdd_count
        print(f"   {cat:<15} {cp_count:<10} {hdd_count:<10} {total:<10}")

def main():
    # Cargar datos
    df_cp = pd.read_csv('ranking_cp.csv')
    df_hdd = pd.read_csv('ranking_hdd.csv')
    
    # Analizar cada ranking
    analizar_ranking(df_cp, "CP")
    analizar_ranking(df_hdd, "HDD")
    
    # Comparar rankings
    comparar_rankings(df_cp, df_hdd)
    
    print(f"\n{'='*60}")
    print("RESUMEN EJECUTIVO")
    print(f"{'='*60}")
    print(f"✅ Ranking CP: {len(df_cp)} equipos analizados")
    print(f"✅ Ranking HDD: {len(df_hdd)} equipos analizados")
    print(f"📊 Ambos rankings usan escala de 0-100 puntos")
    print(f"📈 Sistema de percentiles para normalización")
    print(f"🎯 Categorías: Excelente, Muy Bueno, Bueno, Regular, Necesita Mejora")
    print(f"💾 Resultados guardados en ranking_cp.csv y ranking_hdd.csv")

if __name__ == "__main__":
    main() 