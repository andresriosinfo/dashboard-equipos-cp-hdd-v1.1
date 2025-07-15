#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import ast

def test_explicaciones_por_area():
    """Prueba las explicaciones por área usando datos existentes"""
    
    # Cargar datos existentes
    df_cp = pd.read_csv('ranking_cp.csv')
    df_hdd = pd.read_csv('ranking_hdd.csv')
    
    print("=== PRUEBA DE EXPLICACIONES POR ÁREA ===")
    print("=" * 60)
    
    # Configuración de áreas CP con sus significados
    areas_cp_significado = {
        'PP_NFD': 'Archivos no encontrados',
        'IOLOAD': 'Carga de entrada/salida',
        'totmem': 'Memoria total utilizada',
        'CUMOVR': 'Sobrecarga acumulativa',
        'OMOVRN': 'Overhead de memoria',
        'TLCONS': 'Tiempo de respuesta de consola',
        'OMLDAV': 'Carga promedio de memoria',
        'CPLOAD': 'Carga del procesador',
        'MAXMEM': 'Memoria máxima utilizada'
    }
    
    def calculate_percentile_score(value, all_values, direction='lower_better'):
        """Calcula el puntaje basado en percentiles"""
        if pd.isna(value) or len(all_values) == 0:
            return 0.0
        
        valid_values = [v for v in all_values if not pd.isna(v)]
        if len(valid_values) == 0:
            return 0.0
        
        percentile = (sum(1 for x in valid_values if x < value) / len(valid_values)) * 100
        
        if direction == 'lower_better':
            percentile = 100 - percentile
        
        return percentile
    
    def generate_area_explanation(equipo, area, valor, all_values, area_nombre):
        """Genera explicación específica por área"""
        score = calculate_percentile_score(valor, all_values, 'lower_better')
        
        if score >= 80:
            return f"**{area_nombre} Excelente ({score:.1f}pts)**: El equipo mantiene una carga de {valor:.1f} en {area}, lo que indica un rendimiento excepcional."
        elif score >= 60:
            return f"**{area_nombre} Buena ({score:.1f}pts)**: Con una carga de {valor:.1f} en {area}, el equipo tiene un rendimiento aceptable."
        elif score >= 40:
            return f"**{area_nombre} Regular ({score:.1f}pts)**: La carga de {valor:.1f} en {area} sugiere que el equipo podría estar experimentando problemas de rendimiento."
        else:
            return f"**{area_nombre} Crítica ({score:.1f}pts)**: Con una carga de {valor:.1f} en {area}, el equipo está experimentando problemas significativos de rendimiento."
    
    # Procesar algunos equipos de ejemplo
    equipos_ejemplo = df_cp.head(5)
    
    for idx, equipo in equipos_ejemplo.iterrows():
        print(f"\n🔍 EQUIPO: {equipo['equipo']}")
        print("-" * 50)
        
        # Obtener áreas del equipo
        areas_equipo = equipo['areas_cp']
        try:
            if isinstance(areas_equipo, str):
                areas_list = ast.literal_eval(areas_equipo)
                if not isinstance(areas_list, list):
                    areas_list = [areas_list]
            else:
                areas_list = [areas_equipo]
        except:
            areas_list = [str(areas_equipo)]
        
        print(f"📋 Áreas CP: {', '.join(areas_list)}")
        print(f"📊 Puntuación actual: {equipo['score_final']:.1f}")
        
        # Generar explicaciones por área
        explicaciones_por_area = []
        
        for area in areas_list:
            if area in areas_cp_significado:
                area_nombre = areas_cp_significado[area]
                
                # Simular valores por área (en realidad necesitaríamos datos originales)
                # Por ahora usamos los valores agregados como aproximación
                llenado_valor = equipo['cp_llenado']
                inestabilidad_valor = equipo['cp_inestabilidad']
                tasa_cambio_valor = equipo['cp_tasa_cambio']
                
                # Obtener todos los valores para calcular percentiles
                todos_llenado = df_cp['cp_llenado'].dropna()
                todos_inestabilidad = df_cp['cp_inestabilidad'].dropna()
                todos_tasa_cambio = df_cp['cp_tasa_cambio'].dropna()
                
                # Generar explicaciones para cada métrica
                explicacion_llenado = generate_area_explanation(
                    equipo['equipo'], area, llenado_valor, todos_llenado, 
                    f"Llenado en {area_nombre}"
                )
                
                explicacion_inestabilidad = generate_area_explanation(
                    equipo['equipo'], area, inestabilidad_valor, todos_inestabilidad,
                    f"Estabilidad en {area_nombre}"
                )
                
                explicacion_tasa_cambio = generate_area_explanation(
                    equipo['equipo'], area, tasa_cambio_valor, todos_tasa_cambio,
                    f"Cambios en {area_nombre}"
                )
                
                explicaciones_por_area.extend([
                    explicacion_llenado,
                    explicacion_inestabilidad,
                    explicacion_tasa_cambio
                ])
        
        # Mostrar explicaciones
        print(f"\n📝 EXPLICACIONES POR ÁREA:")
        for i, explicacion in enumerate(explicaciones_por_area, 1):
            print(f"  {i}. {explicacion}")
        
        # Generar recomendaciones
        recomendaciones = []
        if equipo['score_final'] < 50:
            recomendaciones.append("Revisión completa del equipo requerida")
        
        for explicacion in explicaciones_por_area:
            if "Crítica" in explicacion:
                area = explicacion.split()[1]
                recomendaciones.append(f"Intervención inmediata en {area}")
            elif "Regular" in explicacion:
                area = explicacion.split()[1]
                recomendaciones.append(f"Optimizar rendimiento en {area}")
        
        if not recomendaciones:
            if equipo['score_final'] >= 80:
                recomendaciones.append("Mantener estándares actuales")
            else:
                recomendaciones.append("Monitorear rendimiento continuamente")
        
        print(f"\n💡 RECOMENDACIONES:")
        for i, rec in enumerate(recomendaciones, 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "="*60)
    
    # Mostrar comparación con sistema anterior
    print(f"\n🔄 COMPARACIÓN CON SISTEMA ANTERIOR:")
    print("-" * 50)
    
    print(f"📊 Cambios principales:")
    print(f"  1. CP_LLENADO ahora es 'lower_better' (menor = mejor)")
    print(f"  2. Explicaciones específicas por cada área CP")
    print(f"  3. Recomendaciones basadas en áreas problemáticas")
    print(f"  4. Consideración de equipos sin todas las áreas")
    
    # Ejemplo de cómo cambiaría la puntuación
    print(f"\n📈 EJEMPLO DE CAMBIO DE PUNTUACIÓN:")
    print("-" * 50)
    
    equipo_ejemplo = df_cp.iloc[0]
    llenado_anterior = equipo_ejemplo['cp_llenado']
    
    # Simular puntuación anterior (higher_better)
    todos_llenado = df_cp['cp_llenado'].dropna()
    score_anterior = (sum(1 for x in todos_llenado if x < llenado_anterior) / len(todos_llenado)) * 100
    
    # Puntuación nueva (lower_better)
    score_nuevo = 100 - score_anterior
    
    print(f"Equipo: {equipo_ejemplo['equipo']}")
    print(f"Valor CP_LLENADO: {llenado_anterior:.2f}")
    print(f"Puntuación anterior (higher_better): {score_anterior:.1f}")
    print(f"Puntuación nueva (lower_better): {score_nuevo:.1f}")
    print(f"Diferencia: {score_nuevo - score_anterior:.1f} puntos")

if __name__ == "__main__":
    test_explicaciones_por_area() 