#!/usr/bin/env python
# coding: utf-8

"""
Script para mostrar los resultados del ranking de equipos desde la base de datos.
"""

import pandas as pd
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def mostrar_resultados_ranking():
    """
    Muestra los resultados del ranking desde la base de datos.
    """
    try:
        # Importar componentes de base de datos
        from cp_db_manager import get_db_manager
        
        # Obtener manager de base de datos
        db_manager = get_db_manager()
        
        if not db_manager.is_connected:
            logger.error("No se pudo conectar a la base de datos")
            return
        
        # Consultar resultados del ranking
        query = """
        SELECT 
            area, equipo, metrica, posicion, valor_metrico,
            valor_1, valor_2, valor_3, valor_4, valor_5, valor_6, valor_7,
            fecha_ejecucion_del_codigo
        FROM nv_cp_analisis_datos_v2 
        ORDER BY metrica, posicion
        """
        
        logger.info("Consultando resultados del ranking...")
        resultados = db_manager.execute_query(query)
        
        if not resultados:
            logger.warning("No se encontraron resultados en la tabla de ranking")
            return
        
        # Convertir a DataFrame
        df = pd.DataFrame(resultados)
        
        logger.info(f"✓ Se encontraron {len(df)} registros de ranking")
        
        # Mostrar resumen por métrica
        print("\n" + "="*80)
        print("📊 RESUMEN DEL RANKING DE EQUIPOS")
        print("="*80)
        
        for metrica in df['metrica'].unique():
            df_metrica = df[df['metrica'] == metrica]
            print(f"\n🔸 {metrica.upper()}: {len(df_metrica)} equipos")
            print("-" * 60)
            
            # Mostrar top 5 de cada métrica
            for _, row in df_metrica.head(5).iterrows():
                print(f"  Posición {row['posicion']:2d}: {row['equipo']:15s} (Área: {row['area']:10s}) - Valor: {row['valor_metrico']}")
        
        # Mostrar detalles completos
        print("\n" + "="*80)
        print("📋 DETALLES COMPLETOS DEL RANKING")
        print("="*80)
        
        for metrica in df['metrica'].unique():
            df_metrica = df[df['metrica'] == metrica].sort_values('posicion')
            
            print(f"\n🎯 RANKING POR {metrica.upper()}")
            print("=" * 60)
            
            # Crear tabla formateada
            print(f"{'Pos':<4} {'Equipo':<15} {'Área':<10} {'Valor':<10} {'Últimos 7 valores':<50}")
            print("-" * 100)
            
            for _, row in df_metrica.iterrows():
                valores = [str(row[f'valor_{i}']) if row[f'valor_{i}'] is not None else 'None' 
                          for i in range(1, 8)]
                valores_str = ', '.join(valores)
                
                print(f"{row['posicion']:<4} {row['equipo']:<15} {row['area']:<10} "
                      f"{row['valor_metrico']:<10} {valores_str}")
        
        # Mostrar estadísticas
        print("\n" + "="*80)
        print("📈 ESTADÍSTICAS DEL RANKING")
        print("="*80)
        
        print(f"Total de registros: {len(df)}")
        print(f"Fecha de ejecución: {df['fecha_ejecucion_del_codigo'].iloc[0]}")
        print(f"Áreas analizadas: {df['area'].nunique()}")
        print(f"Equipos analizados: {df['equipo'].nunique()}")
        
        # Estadísticas por métrica
        for metrica in df['metrica'].unique():
            df_metrica = df[df['metrica'] == metrica]
            print(f"\n{metrica.capitalize()}:")
            print(f"  - Equipos: {len(df_metrica)}")
            print(f"  - Valor promedio: {df_metrica['valor_metrico'].mean():.2f}")
            print(f"  - Valor máximo: {df_metrica['valor_metrico'].max()}")
            print(f"  - Valor mínimo: {df_metrica['valor_metrico'].min()}")
        
        # Mostrar equipos que aparecen en múltiples rankings
        print("\n" + "="*80)
        print("🏆 EQUIPOS EN MÚLTIPLES RANKINGS")
        print("="*80)
        
        equipos_multiples = df.groupby('equipo')['metrica'].count()
        equipos_multiples = equipos_multiples[equipos_multiples > 1].sort_values(ascending=False)
        
        if not equipos_multiples.empty:
            for equipo, count in equipos_multiples.items():
                metricas_equipo = df[df['equipo'] == equipo]['metrica'].tolist()
                print(f"{equipo}: aparece en {count} rankings ({', '.join(metricas_equipo)})")
        else:
            print("No hay equipos que aparezcan en múltiples rankings")
        
        print("\n" + "="*80)
        print("✅ ANÁLISIS COMPLETADO")
        print("="*80)
        
    except Exception as e:
        logger.error(f"Error mostrando resultados: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

def mostrar_consultas_ejemplo():
    """
    Muestra ejemplos de consultas SQL útiles.
    """
    print("\n" + "="*80)
    print("🔍 CONSULTAS SQL ÚTILES")
    print("="*80)
    
    consultas = [
        {
            "nombre": "Top 5 equipos por llenado",
            "sql": """
SELECT TOP 5 
    area, equipo, posicion, valor_metrico,
    valor_1, valor_2, valor_3, valor_4, valor_5, valor_6, valor_7
FROM nv_cp_analisis_datos_v2 
WHERE metrica = 'llenado' 
ORDER BY posicion;
"""
        },
        {
            "nombre": "Top 5 equipos por inestabilidad",
            "sql": """
SELECT TOP 5 
    area, equipo, posicion, valor_metrico,
    valor_1, valor_2, valor_3, valor_4, valor_5, valor_6, valor_7
FROM nv_cp_analisis_datos_v2 
WHERE metrica = 'inestabilidad' 
ORDER BY posicion;
"""
        },
        {
            "nombre": "Top 5 equipos por tasa de cambio",
            "sql": """
SELECT TOP 5 
    area, equipo, posicion, valor_metrico,
    valor_1, valor_2, valor_3, valor_4, valor_5, valor_6, valor_7
FROM nv_cp_analisis_datos_v2 
WHERE metrica = 'tasa_cambio' 
ORDER BY posicion;
"""
        },
        {
            "nombre": "Ranking completo de un equipo específico",
            "sql": """
SELECT 
    metrica, posicion, valor_metrico,
    valor_1, valor_2, valor_3, valor_4, valor_5, valor_6, valor_7
FROM nv_cp_analisis_datos_v2 
WHERE equipo = 'NOMBRE_DEL_EQUIPO'
ORDER BY metrica;
"""
        },
        {
            "nombre": "Equipos en el top 3 de todas las métricas",
            "sql": """
SELECT equipo, area,
    MAX(CASE WHEN metrica = 'llenado' THEN posicion END) as pos_llenado,
    MAX(CASE WHEN metrica = 'inestabilidad' THEN posicion END) as pos_inestabilidad,
    MAX(CASE WHEN metrica = 'tasa_cambio' THEN posicion END) as pos_tasa_cambio
FROM nv_cp_analisis_datos_v2 
GROUP BY equipo, area
HAVING 
    MAX(CASE WHEN metrica = 'llenado' THEN posicion END) <= 3 OR
    MAX(CASE WHEN metrica = 'inestabilidad' THEN posicion END) <= 3 OR
    MAX(CASE WHEN metrica = 'tasa_cambio' THEN posicion END) <= 3
ORDER BY equipo;
"""
        }
    ]
    
    for i, consulta in enumerate(consultas, 1):
        print(f"\n{i}. {consulta['nombre']}")
        print("-" * 50)
        print(consulta['sql'])

if __name__ == "__main__":
    print("🚀 MOSTRANDO RESULTADOS DEL RANKING DE EQUIPOS")
    print("="*80)
    
    # Mostrar resultados
    mostrar_resultados_ranking()
    
    # Mostrar consultas de ejemplo
    mostrar_consultas_ejemplo() 