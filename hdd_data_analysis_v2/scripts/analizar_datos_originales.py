#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analizar los datos originales de HDD y verificar su calidad.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Añadir el directorio src al sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)
sys.path.insert(0, project_root)

try:
    from hdd_upload_data_deploy import upload_data_sql
    from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
except ImportError as e:
    print(f"Error importando módulos: {e}")
    sys.exit(1)

def analizar_datos_originales():
    """Analiza los datos originales de HDD para verificar su calidad."""
    try:
        print("=" * 80)
        print("ANÁLISIS DE DATOS ORIGINALES HDD")
        print("=" * 80)
        
        # Cargar datos originales
        print("Cargando datos desde nv_hdd_history...")
        datos_dict = upload_data_sql()
        
        if datos_dict is None or not datos_dict:
            print("❌ No se pudieron cargar datos de HDD")
            return
        
        # Combinar todos los DataFrames en uno solo
        datos_list = []
        for key, df in datos_dict.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                datos_list.append(df)
        
        if not datos_list:
            print("❌ No hay DataFrames válidos en los datos cargados")
            return
        
        datos = pd.concat(datos_list, ignore_index=True)
        
        print(f"✅ Datos cargados: {len(datos)} registros")
        print(f"Columnas: {list(datos.columns)}")
        print()
        
        # Información básica
        print("INFORMACIÓN BÁSICA:")
        print("-" * 40)
        print(f"Total de registros: {len(datos)}")
        print(f"Rango de fechas: {datos['fecha'].min()} a {datos['fecha'].max()}")
        print(f"Equipos únicos: {datos['equipo'].nunique()}")
        print(f"Unidades únicas: {datos['unidad'].nunique()}")
        print()
        
        # Análisis de valores nulos
        print("ANÁLISIS DE VALORES NULOS:")
        print("-" * 40)
        nulos = datos.isnull().sum()
        for columna, cantidad in nulos.items():
            porcentaje = (cantidad / len(datos)) * 100
            print(f"{columna}: {cantidad} nulos ({porcentaje:.2f}%)")
        print()
        
        # Análisis de la columna 'uso'
        print("ANÁLISIS DE LA COLUMNA 'USO':")
        print("-" * 40)
        uso_stats = datos['uso'].describe()
        print(f"Estadísticas de uso:")
        print(f"  Mínimo: {uso_stats['min']}")
        print(f"  Máximo: {uso_stats['max']}")
        print(f"  Promedio: {uso_stats['mean']:.4f}")
        print(f"  Mediana: {uso_stats['50%']:.4f}")
        print(f"  Desviación estándar: {uso_stats['std']:.4f}")
        print()
        
        # Valores únicos en 'uso'
        valores_uso = datos['uso'].value_counts().head(10)
        print("Top 10 valores más frecuentes en 'uso':")
        for valor, cantidad in valores_uso.items():
            porcentaje = (cantidad / len(datos)) * 100
            print(f"  {valor}: {cantidad} veces ({porcentaje:.2f}%)")
        print()
        
        # Análisis por equipo
        print("ANÁLISIS POR EQUIPO:")
        print("-" * 40)
        equipos_con_datos = datos.groupby('equipo')['uso'].agg(['count', 'mean', 'std', 'min', 'max']).reset_index()
        equipos_con_datos = equipos_con_datos.sort_values('count', ascending=False)
        
        print("Top 10 equipos con más registros:")
        for _, row in equipos_con_datos.head(10).iterrows():
            print(f"  Equipo {row['equipo']}: {row['count']} registros, uso promedio: {row['mean']:.4f}")
        print()
        
        # Análisis por unidad
        print("ANÁLISIS POR UNIDAD:")
        print("-" * 40)
        unidades_con_datos = datos.groupby('unidad')['uso'].agg(['count', 'mean', 'std', 'min', 'max']).reset_index()
        unidades_con_datos = unidades_con_datos.sort_values('count', ascending=False)
        
        print("Unidades ordenadas por cantidad de registros:")
        for _, row in unidades_con_datos.iterrows():
            print(f"  {row['unidad']}: {row['count']} registros, uso promedio: {row['mean']:.4f}")
        print()
        
        # Análisis de parejas equipo-unidad
        print("ANÁLISIS DE PAREJAS EQUIPO-UNIDAD:")
        print("-" * 40)
        parejas_con_datos = datos.groupby(['equipo', 'unidad'])['uso'].agg(['count', 'mean', 'std', 'min', 'max']).reset_index()
        parejas_con_datos = parejas_con_datos.sort_values('count', ascending=False)
        
        print(f"Total de parejas equipo-unidad: {len(parejas_con_datos)}")
        print("Top 10 parejas con más registros:")
        for _, row in parejas_con_datos.head(10).iterrows():
            print(f"  Equipo {row['equipo']} - {row['unidad']}: {row['count']} registros, uso promedio: {row['mean']:.4f}")
        print()
        
        # Verificar datos de los últimos 7 días
        print("ANÁLISIS DE ÚLTIMOS 7 DÍAS:")
        print("-" * 40)
        fecha_maxima = datos['fecha'].max()
        datos_ultimos_7 = datos[datos['fecha'] >= fecha_maxima - timedelta(days=7)]
        
        print(f"Registros en últimos 7 días: {len(datos_ultimos_7)}")
        print(f"Parejas equipo-unidad en últimos 7 días: {datos_ultimos_7.groupby(['equipo', 'unidad']).size().count()}")
        
        # Parejas con suficientes datos (mínimo 5 registros)
        parejas_suficientes = datos_ultimos_7.groupby(['equipo', 'unidad']).size()
        parejas_suficientes = parejas_suficientes[parejas_suficientes >= 5]
        
        print(f"Parejas con 5+ registros en últimos 7 días: {len(parejas_suficientes)}")
        print()
        
        # Mostrar algunas parejas problemáticas
        print("EJEMPLOS DE PAREJAS PROBLEMÁTICAS:")
        print("-" * 40)
        parejas_pocos_datos = datos_ultimos_7.groupby(['equipo', 'unidad']).size()
        parejas_pocos_datos = parejas_pocos_datos[parejas_pocos_datos < 5]
        
        print(f"Parejas con menos de 5 registros en últimos 7 días: {len(parejas_pocos_datos)}")
        if len(parejas_pocos_datos) > 0:
            print("Primeras 10:")
            for (equipo, unidad), count in parejas_pocos_datos.head(10).items():
                print(f"  Equipo {equipo} - {unidad}: {count} registros")
        
        print("=" * 80)
        print("ANÁLISIS COMPLETADO")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error analizando datos: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analizar_datos_originales() 