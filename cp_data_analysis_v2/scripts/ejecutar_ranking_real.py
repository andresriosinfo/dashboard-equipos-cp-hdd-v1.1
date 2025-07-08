#!/usr/bin/env python
# coding: utf-8

"""
Script para ejecutar el ranking de equipos con datos reales de nv_cp_history.
"""

import pandas as pd
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ejecutar_ranking_con_datos_reales():
    """
    Ejecuta el ranking completo con datos reales de la base de datos.
    """
    try:
        logger.info("🚀 INICIANDO RANKING CON DATOS REALES")
        logger.info("="*60)
        
        # Importar componentes necesarios
        from cp_upload_data_deploy import upload_data_sql
        from cp_ranking_functions import generar_ranking_completo
        from cp_db_manager import get_db_manager
        
        # Paso 1: Obtener datos reales de la base de datos
        logger.info("📊 PASO 1: Obteniendo datos reales de nv_cp_history...")
        df_dict = upload_data_sql()
        
        if not df_dict:
            logger.error("❌ No se pudieron obtener datos de la base de datos")
            return False
        
        logger.info(f"✅ Datos obtenidos exitosamente: {len(df_dict)} DataFrames")
        
        # Mostrar información de los datos obtenidos
        total_registros = 0
        for nombre_df, df in df_dict.items():
            logger.info(f"  📋 {nombre_df}: {len(df)} registros, {len(df.columns)} columnas")
            total_registros += len(df)
            
            # Mostrar algunas estadísticas básicas
            if not df.empty:
                logger.info(f"    - Rango de fechas: {df['fecha'].min()} a {df['fecha'].max()}")
                logger.info(f"    - Equipos únicos: {df['equipo'].nunique()}")
                logger.info(f"    - Áreas únicas: {df['area'].nunique()}")
                logger.info(f"    - Rango de valores: {df['valor'].min()} a {df['valor'].max()}")
        
        logger.info(f"📈 Total de registros procesados: {total_registros}")
        
        # Paso 2: Generar ranking completo
        logger.info("\n📊 PASO 2: Generando ranking completo...")
        df_ranking = generar_ranking_completo(df_dict)
        
        if df_ranking.empty:
            logger.error("❌ No se generaron resultados del ranking")
            return False
        
        logger.info(f"✅ Ranking generado exitosamente: {len(df_ranking)} registros")
        
        # Mostrar resumen del ranking generado
        for metrica in df_ranking['metrica'].unique():
            df_metrica = df_ranking[df_ranking['metrica'] == metrica]
            logger.info(f"  🎯 {metrica.capitalize()}: {len(df_metrica)} equipos")
        
        # Paso 3: Guardar en base de datos
        logger.info("\n📊 PASO 3: Guardando resultados en la base de datos...")
        db_manager = get_db_manager()
        
        if not db_manager.is_connected:
            logger.error("❌ No se pudo conectar a la base de datos")
            return False
        
        success = db_manager.save_results(df_ranking, 'ranking_completo')
        
        if success:
            logger.info("✅ Resultados guardados exitosamente en nv_cp_analisis_datos_v2")
        else:
            logger.error("❌ Error al guardar resultados en la base de datos")
            return False
        
        # Paso 4: Mostrar resultados
        logger.info("\n📊 PASO 4: Mostrando resultados del ranking...")
        mostrar_resultados_reales()
        
        logger.info("\n🎉 ¡RANKING CON DATOS REALES COMPLETADO EXITOSAMENTE!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error ejecutando ranking con datos reales: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def mostrar_resultados_reales():
    """
    Muestra los resultados del ranking con datos reales.
    """
    try:
        from cp_db_manager import get_db_manager
        
        db_manager = get_db_manager()
        
        # Consultar resultados más recientes
        query = """
        SELECT TOP 30
            area, equipo, metrica, posicion, valor_metrico,
            valor_1, valor_2, valor_3, valor_4, valor_5, valor_6, valor_7,
            fecha_ejecucion_del_codigo
        FROM nv_cp_analisis_datos_v2 
        WHERE fecha_ejecucion_del_codigo = (
            SELECT MAX(fecha_ejecucion_del_codigo) 
            FROM nv_cp_analisis_datos_v2
        )
        ORDER BY metrica, posicion
        """
        
        resultados = db_manager.execute_query(query)
        
        if not resultados:
            logger.warning("No se encontraron resultados recientes")
            return
        
        df = pd.DataFrame(resultados)
        
        print("\n" + "="*80)
        print("🏆 RANKING REAL DE EQUIPOS - DATOS DE nv_cp_history")
        print("="*80)
        print(f"📅 Fecha de ejecución: {df['fecha_ejecucion_del_codigo'].iloc[0]}")
        print(f"📊 Total de registros: {len(df)}")
        print(f"🏭 Áreas analizadas: {df['area'].nunique()}")
        print(f"⚙️  Equipos analizados: {df['equipo'].nunique()}")
        
        # Mostrar top 5 de cada métrica
        for metrica in df['metrica'].unique():
            df_metrica = df[df['metrica'] == metrica].head(5)
            
            print(f"\n🎯 TOP 5 - {metrica.upper()}")
            print("-" * 60)
            
            for _, row in df_metrica.iterrows():
                print(f"  Posición {row['posicion']:2d}: {row['equipo']:20s} "
                      f"(Área: {row['area']:15s}) - Valor: {row['valor_metrico']}")
        
        # Mostrar equipos destacados
        print(f"\n🏆 EQUIPOS DESTACADOS")
        print("-" * 60)
        
        # Equipos en el top 3 de cualquier métrica
        equipos_destacados = df[df['posicion'] <= 3]['equipo'].unique()
        for equipo in equipos_destacados:
            metricas_equipo = df[(df['equipo'] == equipo) & (df['posicion'] <= 3)]
            metricas_str = ', '.join([f"{row['metrica']}(#{row['posicion']})" 
                                    for _, row in metricas_equipo.iterrows()])
            print(f"  ⭐ {equipo}: {metricas_str}")
        
        print("\n" + "="*80)
        print("✅ ANÁLISIS COMPLETADO")
        print("="*80)
        
    except Exception as e:
        logger.error(f"Error mostrando resultados: {str(e)}")

def consultar_datos_originales():
    """
    Muestra información sobre los datos originales de nv_cp_history.
    """
    try:
        from cp_db_manager import get_db_manager
        
        db_manager = get_db_manager()
        
        # Consultar información básica de la tabla original
        query_info = """
        SELECT 
            COUNT(*) as total_registros,
            COUNT(DISTINCT equipo) as equipos_unicos,
            COUNT(DISTINCT area) as areas_unicas,
            MIN(fecha) as fecha_minima,
            MAX(fecha) as fecha_maxima,
            MIN(valor) as valor_minimo,
            MAX(valor) as valor_maximo,
            AVG(CAST(valor AS FLOAT)) as valor_promedio
        FROM nv_cp_history
        """
        
        resultado = db_manager.execute_query(query_info)
        
        if resultado:
            info = resultado[0]
            
            print("\n" + "="*80)
            print("📋 INFORMACIÓN DE LA TABLA ORIGINAL nv_cp_history")
            print("="*80)
            print(f"📊 Total de registros: {info['total_registros']:,}")
            print(f"⚙️  Equipos únicos: {info['equipos_unicos']}")
            print(f"🏭 Áreas únicas: {info['areas_unicas']}")
            print(f"📅 Rango de fechas: {info['fecha_minima']} a {info['fecha_maxima']}")
            print(f"📈 Rango de valores: {info['valor_minimo']} a {info['valor_maximo']}")
            print(f"📊 Valor promedio: {info['valor_promedio']:.2f}")
            
            # Mostrar algunos equipos de ejemplo
            query_equipos = """
            SELECT TOP 10 
                equipo, area, 
                COUNT(*) as registros,
                AVG(CAST(valor AS FLOAT)) as promedio_valor
            FROM nv_cp_history 
            GROUP BY equipo, area 
            ORDER BY registros DESC
            """
            
            equipos = db_manager.execute_query(query_equipos)
            
            if equipos:
                print(f"\n🔍 TOP 10 EQUIPOS CON MÁS DATOS:")
                print("-" * 60)
                for equipo in equipos:
                    print(f"  {equipo['equipo']:20s} ({equipo['area']:15s}) - "
                          f"{equipo['registros']:4d} registros, promedio: {equipo['promedio_valor']:.1f}")
        
    except Exception as e:
        logger.error(f"Error consultando datos originales: {str(e)}")

if __name__ == "__main__":
    print("🚀 EJECUTANDO RANKING CON DATOS REALES DE nv_cp_history")
    print("="*80)
    
    # Mostrar información de los datos originales
    consultar_datos_originales()
    
    # Ejecutar ranking con datos reales
    success = ejecutar_ranking_con_datos_reales()
    
    if success:
        print("\n🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!")
        print("📊 Los rankings están disponibles en la tabla nv_cp_analisis_datos_v2")
    else:
        print("\n❌ HUBO ERRORES EN EL PROCESO")
        print("🔍 Revisa los logs para más detalles") 