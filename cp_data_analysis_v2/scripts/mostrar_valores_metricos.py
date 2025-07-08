#!/usr/bin/env python
# coding: utf-8

"""
Script para mostrar ejemplos específicos de valor_metrico y explicar su significado.
"""

import pandas as pd
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def mostrar_ejemplos_valor_metrico():
    """
    Muestra ejemplos específicos de valor_metrico y explica su significado.
    """
    try:
        from cp_db_manager import get_db_manager
        
        db_manager = get_db_manager()
        
        # Consultar ejemplos de cada métrica
        query = """
        SELECT TOP 10
            area, equipo, metrica, posicion, valor_metrico,
            valor_1, valor_2, valor_3, valor_4, valor_5, valor_6, valor_7
        FROM nv_cp_analisis_datos_v2 
        WHERE fecha_ejecucion_del_codigo = (
            SELECT MAX(fecha_ejecucion_del_codigo) 
            FROM nv_cp_analisis_datos_v2
        )
        ORDER BY metrica, posicion
        """
        
        resultados = db_manager.execute_query(query)
        
        if not resultados:
            logger.warning("No se encontraron resultados")
            return
        
        df = pd.DataFrame(resultados)
        
        print("\n" + "="*100)
        print("🔍 EXPLICACIÓN DETALLADA DE valor_metrico")
        print("="*100)
        
        for metrica in df['metrica'].unique():
            df_metrica = df[df['metrica'] == metrica].head(3)
            
            print(f"\n📊 MÉTRICA: {metrica.upper()}")
            print("=" * 80)
            
            if metrica == 'llenado':
                print("🎯 valor_metrico = PROMEDIO de los últimos 7 días")
                print("   (Mayor valor = Mayor llenado/ocupación)")
            elif metrica == 'inestabilidad':
                print("🎯 valor_metrico = DESVIACIÓN ESTÁNDAR × 1000")
                print("   (Mayor valor = Más inestable/variable)")
            elif metrica == 'tasa_cambio':
                print("🎯 valor_metrico = DESVIACIÓN ESTÁNDAR DE TASA DE CAMBIO × 10000")
                print("   (Mayor valor = Cambios más rápidos/frecuentes)")
            
            print("\n📋 EJEMPLOS:")
            print("-" * 80)
            
            for _, row in df_metrica.iterrows():
                valores = [row[f'valor_{i}'] for i in range(1, 8) if row[f'valor_{i}'] is not None]
                valores_str = ', '.join([str(v) for v in valores])
                
                print(f"\n🏭 Equipo: {row['equipo']} (Área: {row['area']})")
                print(f"   📈 Posición: {row['posicion']}")
                print(f"   🎯 valor_metrico: {row['valor_metrico']}")
                print(f"   📊 Últimos valores: [{valores_str}]")
                
                # Explicación específica
                if metrica == 'llenado':
                    if valores:
                        promedio_real = sum(valores) / len(valores)
                        print(f"   💡 Promedio real: {promedio_real:.2f}")
                        print(f"   📝 Interpretación: Este equipo tiene un nivel de llenado promedio de {row['valor_metrico']}")
                
                elif metrica == 'inestabilidad':
                    if len(valores) > 1:
                        import numpy as np
                        desv_real = np.std(valores)
                        print(f"   💡 Desviación real: {desv_real:.2f}")
                        print(f"   📝 Interpretación: Este equipo tiene una variabilidad de {row['valor_metrico']/1000:.2f} (escala original)")
                
                elif metrica == 'tasa_cambio':
                    print(f"   📝 Interpretación: Este equipo tiene una tasa de cambio de {row['valor_metrico']/10000:.4f} (escala original)")
        
        # Mostrar estadísticas generales
        print(f"\n" + "="*100)
        print("📈 ESTADÍSTICAS GENERALES DE valor_metrico")
        print("="*100)
        
        for metrica in df['metrica'].unique():
            df_metrica = df[df['metrica'] == metrica]
            
            print(f"\n🎯 {metrica.upper()}:")
            print(f"   📊 Rango: {df_metrica['valor_metrico'].min()} a {df_metrica['valor_metrico'].max()}")
            print(f"   📈 Promedio: {df_metrica['valor_metrico'].mean():.2f}")
            print(f"   📉 Mediana: {df_metrica['valor_metrico'].median():.2f}")
            
            # Interpretación
            if metrica == 'llenado':
                print(f"   💡 Interpretación: Equipos con valores altos tienen mayor ocupación")
            elif metrica == 'inestabilidad':
                print(f"   💡 Interpretación: Equipos con valores altos son más inestables")
            elif metrica == 'tasa_cambio':
                print(f"   💡 Interpretación: Equipos con valores altos cambian más rápido")
        
        # Mostrar casos extremos
        print(f"\n" + "="*100)
        print("⚠️  CASOS EXTREMOS (POSIBLE ATENCIÓN REQUERIDA)")
        print("="*100)
        
        for metrica in df['metrica'].unique():
            df_metrica = df[df['metrica'] == metrica]
            
            # Top 3 más extremos
            top_extremos = df_metrica.nlargest(3, 'valor_metrico')
            
            print(f"\n🔥 TOP 3 MÁS EXTREMOS - {metrica.upper()}:")
            for _, row in top_extremos.iterrows():
                print(f"   🚨 {row['equipo']} (Área: {row['area']}) - Valor: {row['valor_metrico']} - Posición: {row['posicion']}")
        
        print(f"\n" + "="*100)
        print("✅ EXPLICACIÓN COMPLETADA")
        print("="*100)
        
    except Exception as e:
        logger.error(f"Error mostrando ejemplos: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    print("🔍 EXPLICANDO valor_metrico")
    print("="*100)
    mostrar_ejemplos_valor_metrico() 