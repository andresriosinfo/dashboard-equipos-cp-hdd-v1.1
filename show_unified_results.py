#!/usr/bin/env python
# coding: utf-8

"""
Script para mostrar y analizar los resultados del sistema de puntuación unificado.
"""

import pandas as pd
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_latest_results():
    """
    Obtiene los resultados más recientes del sistema de puntuación unificado.
    
    Returns:
        pd.DataFrame: DataFrame con los resultados
    """
    try:
        # Importar componentes CP para acceder a la base de datos
        import sys
        sys.path.append('cp_data_analysis_v2/src')
        from cp_db_manager import get_db_manager
        
        db_manager = get_db_manager()
        
        # Consultar resultados más recientes
        query = """
        SELECT TOP 1000
            equipo, area_cp, unidades_hdd, puntuacion_final, posicion_ranking,
            categoria_final, cp_llenado, cp_llenado_score, cp_inestabilidad, cp_inestabilidad_score,
            cp_tasa_cambio, cp_tasa_cambio_score, hdd_uso, hdd_uso_score, hdd_inestabilidad,
            hdd_inestabilidad_score, hdd_tasa_cambio, hdd_tasa_cambio_score,
            explicacion_detallada, recomendaciones, registros_cp, registros_hdd, fecha_ejecucion
        FROM nv_unified_scoring 
        WHERE fecha_ejecucion = (
            SELECT MAX(fecha_ejecucion) 
            FROM nv_unified_scoring
        )
        ORDER BY posicion_ranking
        """
        
        resultados = db_manager.execute_query(query)
        
        if not resultados:
            logger.warning("No se encontraron resultados en la tabla nv_unified_scoring")
            return pd.DataFrame()
        
        df = pd.DataFrame(resultados)
        logger.info(f"Resultados obtenidos: {len(df)} equipos")
        return df
        
    except Exception as e:
        logger.error(f"Error obteniendo resultados: {str(e)}")
        return pd.DataFrame()

def show_summary_statistics(df):
    """
    Muestra estadísticas resumidas de los resultados.
    
    Args:
        df: DataFrame con resultados
    """
    if df.empty:
        print("❌ No hay datos para mostrar")
        return
    
    print("\n" + "="*80)
    print("📊 ESTADÍSTICAS GENERALES - SISTEMA DE PUNTUACIÓN UNIFICADO")
    print("="*80)
    
    # Información básica
    print(f"📅 Fecha de análisis: {df['fecha_ejecucion'].iloc[0]}")
    print(f"⚙️  Total de equipos: {len(df)}")
    print(f"🏭 Equipos con datos CP: {df['registros_cp'].gt(0).sum()}")
    print(f"💾 Equipos con datos HDD: {df['registros_hdd'].gt(0).sum()}")
    print(f"🔄 Equipos con ambos datos: {(df['registros_cp'].gt(0) & df['registros_hdd'].gt(0)).sum()}")
    
    # Estadísticas de puntuación
    print(f"\n🎯 ESTADÍSTICAS DE PUNTUACIÓN:")
    print(f"   - Puntuación promedio: {df['puntuacion_final'].mean():.2f}")
    print(f"   - Puntuación máxima: {df['puntuacion_final'].max():.2f}")
    print(f"   - Puntuación mínima: {df['puntuacion_final'].min():.2f}")
    print(f"   - Desviación estándar: {df['puntuacion_final'].std():.2f}")
    
    # Distribución por categorías
    print(f"\n📈 DISTRIBUCIÓN POR CATEGORÍAS:")
    categoria_counts = df['categoria_final'].value_counts()
    for categoria, count in categoria_counts.items():
        porcentaje = (count / len(df)) * 100
        print(f"   - {categoria}: {count} equipos ({porcentaje:.1f}%)")
    
    # Top áreas
    if 'area_cp' in df.columns and df['area_cp'].notna().any():
        print(f"\n🏭 TOP 5 ÁREAS CP POR PUNTUACIÓN PROMEDIO:")
        areas_avg = df.groupby('area_cp')['puntuacion_final'].agg(['mean', 'count']).sort_values('mean', ascending=False)
        for area, (avg_score, count) in areas_avg.head(5).iterrows():
            print(f"   - {area}: {avg_score:.2f}pts ({count} equipos)")

def show_top_performers(df, top_n=10):
    """
    Muestra los mejores equipos.
    
    Args:
        df: DataFrame con resultados
        top_n: Número de equipos a mostrar
    """
    if df.empty:
        return
    
    print(f"\n" + "="*80)
    print(f"🏆 TOP {top_n} EQUIPOS - MEJOR PUNTUACIÓN")
    print("="*80)
    
    top_equipos = df.head(top_n)
    
    for _, row in top_equipos.iterrows():
        print(f"\n🥇 Posición {row['posicion_ranking']:2d}: {row['equipo']}")
        print(f"   📊 Puntuación: {row['puntuacion_final']:.2f}pts ({row['categoria_final']})")
        print(f"   🏭 Área CP: {row['area_cp'] or 'N/A'}")
        print(f"   💾 Unidades HDD: {len(row['unidades_hdd'].split(',')) if row['unidades_hdd'] else 0}")
        
        # Mostrar puntuaciones individuales
        scores = []
        if pd.notna(row['cp_llenado_score']):
            scores.append(f"CP Llenado: {row['cp_llenado_score']:.1f}pts")
        if pd.notna(row['cp_inestabilidad_score']):
            scores.append(f"CP Estabilidad: {row['cp_inestabilidad_score']:.1f}pts")
        if pd.notna(row['cp_tasa_cambio_score']):
            scores.append(f"CP Cambios: {row['cp_tasa_cambio_score']:.1f}pts")
        if pd.notna(row['hdd_uso_score']):
            scores.append(f"HDD Uso: {row['hdd_uso_score']:.1f}pts")
        if pd.notna(row['hdd_inestabilidad_score']):
            scores.append(f"HDD Estabilidad: {row['hdd_inestabilidad_score']:.1f}pts")
        if pd.notna(row['hdd_tasa_cambio_score']):
            scores.append(f"HDD Cambios: {row['hdd_tasa_cambio_score']:.1f}pts")
        
        print(f"   📈 Puntuaciones: {' | '.join(scores)}")
        print(f"   💡 Recomendación: {row['recomendaciones']}")

def show_bottom_performers(df, bottom_n=10):
    """
    Muestra los equipos con menor puntuación.
    
    Args:
        df: DataFrame con resultados
        bottom_n: Número de equipos a mostrar
    """
    if df.empty:
        return
    
    print(f"\n" + "="*80)
    print(f"⚠️  TOP {bottom_n} EQUIPOS - MENOR PUNTUACIÓN")
    print("="*80)
    
    bottom_equipos = df.tail(bottom_n)
    
    for _, row in bottom_equipos.iterrows():
        print(f"\n🔴 Posición {row['posicion_ranking']:2d}: {row['equipo']}")
        print(f"   📊 Puntuación: {row['puntuacion_final']:.2f}pts ({row['categoria_final']})")
        print(f"   🏭 Área CP: {row['area_cp'] or 'N/A'}")
        print(f"   💾 Unidades HDD: {len(row['unidades_hdd'].split(',')) if row['unidades_hdd'] else 0}")
        
        # Mostrar puntuaciones individuales bajas
        low_scores = []
        if pd.notna(row['cp_llenado_score']) and row['cp_llenado_score'] < 50:
            low_scores.append(f"CP Llenado: {row['cp_llenado_score']:.1f}pts")
        if pd.notna(row['cp_inestabilidad_score']) and row['cp_inestabilidad_score'] < 50:
            low_scores.append(f"CP Estabilidad: {row['cp_inestabilidad_score']:.1f}pts")
        if pd.notna(row['cp_tasa_cambio_score']) and row['cp_tasa_cambio_score'] < 50:
            low_scores.append(f"CP Cambios: {row['cp_tasa_cambio_score']:.1f}pts")
        if pd.notna(row['hdd_uso_score']) and row['hdd_uso_score'] < 50:
            low_scores.append(f"HDD Uso: {row['hdd_uso_score']:.1f}pts")
        if pd.notna(row['hdd_inestabilidad_score']) and row['hdd_inestabilidad_score'] < 50:
            low_scores.append(f"HDD Estabilidad: {row['hdd_inestabilidad_score']:.1f}pts")
        if pd.notna(row['hdd_tasa_cambio_score']) and row['hdd_tasa_cambio_score'] < 50:
            low_scores.append(f"HDD Cambios: {row['hdd_tasa_cambio_score']:.1f}pts")
        
        if low_scores:
            print(f"   ⚠️  Puntuaciones bajas: {' | '.join(low_scores)}")
        
        print(f"   💡 Recomendación: {row['recomendaciones']}")

def show_equipment_details(df, equipo_name):
    """
    Muestra detalles específicos de un equipo.
    
    Args:
        df: DataFrame con resultados
        equipo_name: Nombre del equipo a analizar
    """
    if df.empty:
        return
    
    equipo_data = df[df['equipo'] == equipo_name]
    
    if equipo_data.empty:
        print(f"❌ No se encontró información para el equipo: {equipo_name}")
        return
    
    row = equipo_data.iloc[0]
    
    print(f"\n" + "="*80)
    print(f"🔍 DETALLES DEL EQUIPO: {equipo_name}")
    print("="*80)
    
    print(f"📊 PUNTUACIÓN GENERAL:")
    print(f"   - Puntuación final: {row['puntuacion_final']:.2f}pts")
    print(f"   - Posición en ranking: {row['posicion_ranking']}")
    print(f"   - Categoría: {row['categoria_final']}")
    
    print(f"\n🏭 INFORMACIÓN GENERAL:")
    print(f"   - Área CP: {row['area_cp'] or 'N/A'}")
    print(f"   - Unidades HDD: {row['unidades_hdd'] or 'N/A'}")
    print(f"   - Registros CP: {row['registros_cp']}")
    print(f"   - Registros HDD: {row['registros_hdd']}")
    
    print(f"\n📈 PUNTUACIONES POR MÉTRICA:")
    
    # Métricas CP
    if pd.notna(row['cp_llenado']):
        print(f"   🔧 CP Llenado:")
        print(f"      - Valor: {row['cp_llenado']:.2f}")
        print(f"      - Puntuación: {row['cp_llenado_score']:.1f}pts")
    
    if pd.notna(row['cp_inestabilidad']):
        print(f"   🔧 CP Inestabilidad:")
        print(f"      - Valor: {row['cp_inestabilidad']:.2f}")
        print(f"      - Puntuación: {row['cp_inestabilidad_score']:.1f}pts")
    
    if pd.notna(row['cp_tasa_cambio']):
        print(f"   🔧 CP Tasa de Cambio:")
        print(f"      - Valor: {row['cp_tasa_cambio']:.2f}")
        print(f"      - Puntuación: {row['cp_tasa_cambio_score']:.1f}pts")
    
    # Métricas HDD
    if pd.notna(row['hdd_uso']):
        print(f"   💾 HDD Uso:")
        print(f"      - Valor: {row['hdd_uso']:.2f}%")
        print(f"      - Puntuación: {row['hdd_uso_score']:.1f}pts")
    
    if pd.notna(row['hdd_inestabilidad']):
        print(f"   💾 HDD Inestabilidad:")
        print(f"      - Valor: {row['hdd_inestabilidad']:.2f}")
        print(f"      - Puntuación: {row['hdd_inestabilidad_score']:.1f}pts")
    
    if pd.notna(row['hdd_tasa_cambio']):
        print(f"   💾 HDD Tasa de Cambio:")
        print(f"      - Valor: {row['hdd_tasa_cambio']:.2f}")
        print(f"      - Puntuación: {row['hdd_tasa_cambio_score']:.1f}pts")
    
    print(f"\n💡 RECOMENDACIONES:")
    print(f"   {row['recomendaciones']}")
    
    print(f"\n📝 EXPLICACIÓN DETALLADA:")
    print(f"   {row['explicacion_detallada']}")

def show_area_analysis(df):
    """
    Muestra análisis por área.
    
    Args:
        df: DataFrame con resultados
    """
    if df.empty or 'area_cp' not in df.columns:
        return
    
    areas_with_data = df[df['area_cp'].notna()]
    
    if areas_with_data.empty:
        print("❌ No hay datos de áreas para analizar")
        return
    
    print(f"\n" + "="*80)
    print("🏭 ANÁLISIS POR ÁREA CP")
    print("="*80)
    
    # Agrupar por área
    area_stats = areas_with_data.groupby('area_cp').agg({
        'puntuacion_final': ['mean', 'std', 'count', 'min', 'max'],
        'categoria_final': lambda x: x.value_counts().to_dict()
    }).round(2)
    
    for area in area_stats.index:
        stats = area_stats.loc[area]
        print(f"\n🏭 ÁREA: {area}")
        print(f"   📊 Estadísticas:")
        print(f"      - Equipos: {stats[('puntuacion_final', 'count')]}")
        print(f"      - Puntuación promedio: {stats[('puntuacion_final', 'mean')]:.2f}pts")
        print(f"      - Desviación estándar: {stats[('puntuacion_final', 'std')]:.2f}")
        print(f"      - Rango: {stats[('puntuacion_final', 'min')]:.2f} - {stats[('puntuacion_final', 'max')]:.2f}pts")
        
        # Mostrar distribución de categorías
        categorias = stats[('categoria_final', '')]
        if categorias:
            print(f"   📈 Distribución de categorías:")
            for categoria, count in categorias.items():
                print(f"      - {categoria}: {count} equipos")

def main():
    """
    Función principal para mostrar resultados.
    """
    print("🔍 SISTEMA DE PUNTUACIÓN UNIFICADO - VISUALIZADOR DE RESULTADOS")
    print("="*80)
    
    # Obtener resultados
    df = get_latest_results()
    
    if df.empty:
        print("❌ No se encontraron resultados. Ejecuta primero el análisis unificado.")
        return
    
    # Mostrar estadísticas generales
    show_summary_statistics(df)
    
    # Mostrar mejores equipos
    show_top_performers(df, top_n=10)
    
    # Mostrar equipos con menor puntuación
    show_bottom_performers(df, bottom_n=5)
    
    # Mostrar análisis por área
    show_area_analysis(df)
    
    # Interactivo: buscar equipo específico
    print(f"\n" + "="*80)
    print("🔍 BÚSQUEDA DE EQUIPO ESPECÍFICO")
    print("="*80)
    
    while True:
        equipo = input("\nIngresa el nombre del equipo (o 'salir' para terminar): ").strip()
        
        if equipo.lower() in ['salir', 'exit', 'quit']:
            break
        
        if equipo:
            show_equipment_details(df, equipo)
        else:
            print("❌ Por favor ingresa un nombre de equipo válido")
    
    print("\n✅ Análisis completado. ¡Gracias por usar el sistema de puntuación unificado!")

if __name__ == "__main__":
    main() 