#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import ast

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedScoringSystemV2:
    """
    Sistema de puntuación unificado mejorado con explicaciones por área
    """
    
    def __init__(self):
        """Inicializar el sistema de puntuación."""
        self.fecha_ejecucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Configuración de métricas CORREGIDA
        self.metric_configs = {
            # Variables CP - TODAS lower_better (menor = mejor rendimiento)
            'cp_llenado': {
                'direction': 'lower_better',  # CORREGIDO: menor carga = mejor rendimiento
                'weight': 0.15,
                'description': 'Nivel de carga promedio del equipo CP'
            },
            'cp_inestabilidad': {
                'direction': 'lower_better',
                'weight': 0.15,
                'description': 'Variabilidad en el rendimiento del equipo CP'
            },
            'cp_tasa_cambio': {
                'direction': 'lower_better',
                'weight': 0.15,
                'description': 'Velocidad de cambio en el rendimiento CP'
            },
            
            # Variables HDD - Menor valor = Mejor rendimiento
            'hdd_uso': {
                'direction': 'lower_better',
                'weight': 0.20,
                'description': 'Nivel de uso promedio del disco duro'
            },
            'hdd_inestabilidad': {
                'direction': 'lower_better',
                'weight': 0.20,
                'description': 'Variabilidad en el uso del disco duro'
            },
            'hdd_tasa_cambio': {
                'direction': 'lower_better',
                'weight': 0.15,
                'description': 'Velocidad de cambio en el uso del disco duro'
            }
        }
        
        # Verificar que los pesos sumen 1.0
        total_weight = sum(config['weight'] for config in self.metric_configs.values())
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(f"Los pesos de las métricas deben sumar 1.0, actual: {total_weight}")
        
        # Configuración de áreas CP con sus significados
        self.areas_cp_significado = {
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
    
    def calculate_percentile_score(self, value, all_values, direction='lower_better'):
        """
        Calcula el puntaje basado en percentiles.
        
        Args:
            value: Valor del equipo
            all_values: Lista de todos los valores
            direction: 'lower_better' o 'higher_better'
            
        Returns:
            float: Puntaje de 0 a 100
        """
        if pd.isna(value) or len(all_values) == 0:
            return 0.0
        
        # Filtrar valores válidos
        valid_values = [v for v in all_values if not pd.isna(v)]
        if len(valid_values) == 0:
            return 0.0
        
        # Calcular percentil
        percentile = (sum(1 for x in valid_values if x < value) / len(valid_values)) * 100
        
        # Invertir para lower_better
        if direction == 'lower_better':
            percentile = 100 - percentile
        
        return percentile
    
    def get_cp_metrics_by_area(self):
        """Obtiene métricas CP por área individual"""
        try:
            sys.path.append('cp_data_analysis_v2/src')
            from cp_upload_data_deploy import upload_data_sql
            
            logger.info('Cargando datos CP por área...')
            cp_data = upload_data_sql()
            
            equipos_por_area = {}
            
            for nombre_df, df in cp_data.items():
                if df.empty or not set(['equipo','fecha','valor','area']).issubset(df.columns):
                    continue
                
                df = df.copy()
                df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
                df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
                df = df.dropna(subset=['fecha','valor'])
                
                if df.empty:
                    continue
                
                fecha_max = df['fecha'].max()
                df = df[df['fecha'] >= fecha_max - timedelta(days=7)]
                
                if df.empty:
                    continue
                
                # Procesar por área individual
                for area in df['area'].unique():
                    df_area = df[df['area'] == area]
                    
                    if area not in equipos_por_area:
                        equipos_por_area[area] = {}
                    
                    for equipo in df_area['equipo'].unique():
                        df_equipo = df_area[df_area['equipo'] == equipo]
                        
                        if len(df_equipo) < 3:
                            continue
                        
                        valores = df_equipo['valor'].tolist()
                        
                        # Calcular métricas por área
                        llenado = np.mean(valores)
                        inestabilidad = np.std(valores) * 1000
                        
                        # Tasa de cambio
                        df_equipo_sorted = df_equipo.sort_values('fecha')
                        tasas = []
                        for i in range(1, len(df_equipo_sorted)):
                            v0 = df_equipo_sorted.iloc[i-1]['valor']
                            v1 = df_equipo_sorted.iloc[i]['valor']
                            if v0 != 0:
                                tasas.append(((v1-v0)/v0)*100)
                        
                        tasa_cambio = np.std(tasas) * 10000 if tasas else 0
                        
                        equipos_por_area[area][equipo] = {
                            'llenado': llenado,
                            'inestabilidad': inestabilidad,
                            'tasa_cambio': tasa_cambio,
                            'registros': len(df_equipo)
                        }
            
            return equipos_por_area
            
        except Exception as e:
            logger.error(f"Error cargando datos CP: {str(e)}")
            return {}
    
    def get_hdd_metrics(self):
        """Obtiene métricas HDD"""
        try:
            sys.path.append('hdd_data_analysis_v2/src')
            from hdd_upload_data_deploy import upload_data_sql
            
            logger.info('Cargando datos HDD...')
            hdd_data = upload_data_sql()
            equipos = {}
            
            for nombre_df, df in hdd_data.items():
                if df.empty or not set(['equipo','fecha','uso','unidad']).issubset(df.columns):
                    continue
                
                df = df.copy()
                df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
                df['uso'] = pd.to_numeric(df['uso'], errors='coerce')
                df = df.dropna(subset=['fecha','uso'])
                
                if df.empty:
                    continue
                
                fecha_max = df['fecha'].max()
                df = df[df['fecha'] >= fecha_max - timedelta(days=7)]
                
                if df.empty:
                    continue
                
                for equipo in df['equipo'].unique():
                    df_eq = df[df['equipo']==equipo]
                    if len(df_eq) < 3:
                        continue
                    
                    if equipo not in equipos:
                        equipos[equipo] = {'uso':[],'inestabilidad':[],'tasa_cambio':[],'unidades':set(),'registros':0}
                    
                    valores = df_eq['uso'].tolist()
                    equipos[equipo]['uso'].append(np.mean(valores)*100)
                    equipos[equipo]['inestabilidad'].append(np.std(valores)*1000)
                    
                    # Tasa de cambio
                    df_eq_sorted = df_eq.sort_values('fecha')
                    tasas = []
                    for i in range(1,len(df_eq_sorted)):
                        v0 = df_eq_sorted.iloc[i-1]['uso']
                        v1 = df_eq_sorted.iloc[i]['uso']
                        if v0 != 0:
                            tasas.append(((v1-v0)/v0)*100)
                    
                    equipos[equipo]['tasa_cambio'].append(np.std(tasas)*10000 if tasas else 0)
                    equipos[equipo]['unidades'].add(df_eq['unidad'].iloc[0])
                    equipos[equipo]['registros'] += len(df_eq)
            
            # Consolidar métricas promedio por equipo
            rows = []
            for eq, vals in equipos.items():
                rows.append({
                    'equipo': eq,
                    'hdd_uso': np.mean(vals['uso']) if vals['uso'] else np.nan,
                    'hdd_inestabilidad': np.mean(vals['inestabilidad']) if vals['inestabilidad'] else np.nan,
                    'hdd_tasa_cambio': np.mean(vals['tasa_cambio']) if vals['tasa_cambio'] else np.nan,
                    'unidades_hdd': list(vals['unidades']),
                    'registros_hdd': vals['registros']
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.error(f"Error cargando datos HDD: {str(e)}")
            return pd.DataFrame()
    
    def generate_area_specific_explanation(self, equipo, area, metricas_area, all_equipos_area):
        """Genera explicación específica por área"""
        explicacion = []
        
        # Obtener valores del equipo para esta área
        if equipo in metricas_area:
            equipo_data = metricas_area[equipo]
            
            # Llenado
            llenado_valor = equipo_data['llenado']
            llenado_score = self.calculate_percentile_score(
                llenado_valor, 
                [eq['llenado'] for eq in metricas_area.values()], 
                'lower_better'
            )
            
            area_nombre = self.areas_cp_significado.get(area, area)
            
            if llenado_score >= 80:
                explicacion.append(f"**{area_nombre} Excelente ({llenado_score:.1f}pts)**: El equipo mantiene una carga de {llenado_valor:.1f} en {area}, lo que indica un rendimiento excepcional. Esto significa que el sistema está funcionando de manera muy eficiente en esta área.")
            elif llenado_score >= 60:
                explicacion.append(f"**{area_nombre} Buena ({llenado_score:.1f}pts)**: Con una carga de {llenado_valor:.1f} en {area}, el equipo tiene un rendimiento aceptable, aunque hay margen para optimización.")
            elif llenado_score >= 40:
                explicacion.append(f"**{area_nombre} Regular ({llenado_score:.1f}pts)**: La carga de {llenado_valor:.1f} en {area} sugiere que el equipo podría estar experimentando problemas de rendimiento en esta área.")
            else:
                explicacion.append(f"**{area_nombre} Crítica ({llenado_score:.1f}pts)**: Con una carga de {llenado_valor:.1f} en {area}, el equipo está experimentando problemas significativos de rendimiento que requieren atención inmediata.")
            
            # Inestabilidad
            inestabilidad_valor = equipo_data['inestabilidad']
            inestabilidad_score = self.calculate_percentile_score(
                inestabilidad_valor,
                [eq['inestabilidad'] for eq in metricas_area.values()],
                'lower_better'
            )
            
            if inestabilidad_score >= 80:
                explicacion.append(f"**Estabilidad en {area_nombre} Excelente ({inestabilidad_score:.1f}pts)**: El equipo muestra una variabilidad muy baja ({inestabilidad_valor:.1f}), indicando un funcionamiento muy estable.")
            elif inestabilidad_score >= 60:
                explicacion.append(f"**Estabilidad en {area_nombre} Buena ({inestabilidad_score:.1f}pts)**: La variabilidad de {inestabilidad_valor:.1f} indica un funcionamiento estable con algunas fluctuaciones menores.")
            elif inestabilidad_score >= 40:
                explicacion.append(f"**Estabilidad en {area_nombre} Regular ({inestabilidad_score:.1f}pts)**: La variabilidad de {inestabilidad_valor:.1f} sugiere inestabilidad que puede afectar el rendimiento.")
            else:
                explicacion.append(f"**Estabilidad en {area_nombre} Crítica ({inestabilidad_score:.1f}pts)**: La alta variabilidad de {inestabilidad_valor:.1f} indica problemas graves de estabilidad que requieren intervención.")
        
        return explicacion
    
    def calculate_unified_score(self):
        """Calcula la puntuación unificada con explicaciones por área"""
        logger.info("Iniciando cálculo de puntuación unificada...")
        
        # Cargar datos
        cp_metrics_by_area = self.get_cp_metrics_by_area()
        hdd_metrics = self.get_hdd_metrics()
        
        if not cp_metrics_by_area and hdd_metrics.empty:
            logger.error("No se pudieron cargar datos de CP ni HDD")
            return pd.DataFrame()
        
        # Obtener todos los equipos únicos
        todos_equipos = set()
        
        # Equipos CP
        for area, equipos in cp_metrics_by_area.items():
            todos_equipos.update(equipos.keys())
        
        # Equipos HDD
        if not hdd_metrics.empty:
            todos_equipos.update(hdd_metrics['equipo'].tolist())
        
        logger.info(f"Total equipos encontrados: {len(todos_equipos)}")
        
        # Calcular puntuaciones
        resultados = []
        
        for equipo in todos_equipos:
            logger.info(f"Procesando equipo: {equipo}")
            
            # Inicializar métricas
            metricas_equipo = {
                'equipo': equipo,
                'areas_cp': [],
                'unidades_hdd': [],
                'registros_cp': 0,
                'registros_hdd': 0,
                'explicaciones_por_area': []
            }
            
            # Procesar métricas CP por área
            puntuaciones_cp = []
            explicaciones_cp = []
            
            for area, equipos_area in cp_metrics_by_area.items():
                if equipo in equipos_area:
                    metricas_equipo['areas_cp'].append(area)
                    metricas_equipo['registros_cp'] += equipos_area[equipo]['registros']
                    
                    # Generar explicación específica por área
                    explicacion_area = self.generate_area_specific_explanation(
                        equipo, area, equipos_area, equipos_area
                    )
                    explicaciones_cp.extend(explicacion_area)
                    
                    # Calcular puntuaciones por área
                    llenado = equipos_area[equipo]['llenado']
                    inestabilidad = equipos_area[equipo]['inestabilidad']
                    tasa_cambio = equipos_area[equipo]['tasa_cambio']
                    
                    # Obtener todos los valores para calcular percentiles
                    todos_llenado = [eq['llenado'] for eq in equipos_area.values()]
                    todos_inestabilidad = [eq['inestabilidad'] for eq in equipos_area.values()]
                    todos_tasa_cambio = [eq['tasa_cambio'] for eq in equipos_area.values()]
                    
                    # Calcular puntuaciones
                    llenado_score = self.calculate_percentile_score(llenado, todos_llenado, 'lower_better')
                    inestabilidad_score = self.calculate_percentile_score(inestabilidad, todos_inestabilidad, 'lower_better')
                    tasa_cambio_score = self.calculate_percentile_score(tasa_cambio, todos_tasa_cambio, 'lower_better')
                    
                    # Puntuación promedio por área
                    area_score = (llenado_score * 0.4 + inestabilidad_score * 0.3 + tasa_cambio_score * 0.3)
                    puntuaciones_cp.append(area_score)
            
            # Procesar métricas HDD
            puntuaciones_hdd = []
            explicaciones_hdd = []
            
            if not hdd_metrics.empty:
                hdd_equipo = hdd_metrics[hdd_metrics['equipo'] == equipo]
                if not hdd_equipo.empty:
                    row = hdd_equipo.iloc[0]
                    metricas_equipo['unidades_hdd'] = row['unidades_hdd']
                    metricas_equipo['registros_hdd'] = row['registros_hdd']
                    
                    # Calcular puntuaciones HDD
                    hdd_uso = row['hdd_uso']
                    hdd_inestabilidad = row['hdd_inestabilidad']
                    hdd_tasa_cambio = row['hdd_tasa_cambio']
                    
                    if not pd.isna(hdd_uso):
                        hdd_uso_score = self.calculate_percentile_score(hdd_uso, hdd_metrics['hdd_uso'].dropna(), 'lower_better')
                        if hdd_uso_score >= 80:
                            explicaciones_hdd.append(f"**Uso HDD Excelente ({hdd_uso_score:.1f}pts)**: El disco está siendo utilizado eficientemente al {hdd_uso:.1f}%.")
                        elif hdd_uso_score >= 60:
                            explicaciones_hdd.append(f"**Uso HDD Bueno ({hdd_uso_score:.1f}pts)**: El uso del {hdd_uso:.1f}% es aceptable.")
                        elif hdd_uso_score >= 40:
                            explicaciones_hdd.append(f"**Uso HDD Regular ({hdd_uso_score:.1f}pts)**: El uso del {hdd_uso:.1f}% sugiere que el disco podría estar sobrecargado.")
                        else:
                            explicaciones_hdd.append(f"**Uso HDD Crítico ({hdd_uso_score:.1f}pts)**: El uso del {hdd_uso:.1f}% indica problemas graves de espacio en disco.")
                    
                    if not pd.isna(hdd_inestabilidad):
                        hdd_inestabilidad_score = self.calculate_percentile_score(hdd_inestabilidad, hdd_metrics['hdd_inestabilidad'].dropna(), 'lower_better')
                        if hdd_inestabilidad_score >= 80:
                            explicaciones_hdd.append(f"**Estabilidad HDD Excelente ({hdd_inestabilidad_score:.1f}pts)**: El uso del disco es muy estable.")
                        elif hdd_inestabilidad_score >= 60:
                            explicaciones_hdd.append(f"**Estabilidad HDD Buena ({hdd_inestabilidad_score:.1f}pts)**: El uso del disco es relativamente estable.")
                        elif hdd_inestabilidad_score >= 40:
                            explicaciones_hdd.append(f"**Estabilidad HDD Regular ({hdd_inestabilidad_score:.1f}pts)**: El uso del disco muestra variabilidad que puede afectar el rendimiento.")
                        else:
                            explicaciones_hdd.append(f"**Estabilidad HDD Crítica ({hdd_inestabilidad_score:.1f}pts)**: El uso del disco es muy inestable, requiriendo atención inmediata.")
                    
                    if not pd.isna(hdd_tasa_cambio):
                        hdd_tasa_cambio_score = self.calculate_percentile_score(hdd_tasa_cambio, hdd_metrics['hdd_tasa_cambio'].dropna(), 'lower_better')
                        if hdd_tasa_cambio_score >= 80:
                            explicaciones_hdd.append(f"**Cambios HDD Predecibles ({hdd_tasa_cambio_score:.1f}pts)**: Los cambios en el uso del disco son muy predecibles.")
                        elif hdd_tasa_cambio_score >= 60:
                            explicaciones_hdd.append(f"**Cambios HDD Estables ({hdd_tasa_cambio_score:.1f}pts)**: Los cambios en el uso del disco son relativamente estables.")
                        elif hdd_tasa_cambio_score >= 40:
                            explicaciones_hdd.append(f"**Cambios HDD Variables ({hdd_tasa_cambio_score:.1f}pts)**: Los cambios en el uso del disco son impredecibles.")
                        else:
                            explicaciones_hdd.append(f"**Cambios HDD Caóticos ({hdd_tasa_cambio_score:.1f}pts)**: Los cambios en el uso del disco son muy impredecibles.")
                    
                    # Puntuación HDD
                    hdd_score = (hdd_uso_score * 0.4 + hdd_inestabilidad_score * 0.4 + hdd_tasa_cambio_score * 0.2)
                    puntuaciones_hdd.append(hdd_score)
            
            # Calcular puntuación final
            puntuacion_final = 0
            total_peso = 0
            
            if puntuaciones_cp:
                cp_promedio = np.mean(puntuaciones_cp)
                puntuacion_final += cp_promedio * 0.45  # 45% para CP
                total_peso += 0.45
            
            if puntuaciones_hdd:
                hdd_promedio = np.mean(puntuaciones_hdd)
                puntuacion_final += hdd_promedio * 0.55  # 55% para HDD
                total_peso += 0.55
            
            # Normalizar si es necesario
            if total_peso > 0:
                puntuacion_final = puntuacion_final / total_peso
            
            # Categorizar
            if puntuacion_final >= 90:
                categoria = "Excelente"
            elif puntuacion_final >= 75:
                categoria = "Muy Bueno"
            elif puntuacion_final >= 50:
                categoria = "Bueno"
            elif puntuacion_final >= 25:
                categoria = "Regular"
            else:
                categoria = "Necesita Mejora"
            
            # Generar recomendaciones
            recomendaciones = self.generate_recommendations(puntuacion_final, explicaciones_cp, explicaciones_hdd)
            
            # Consolidar resultados
            metricas_equipo.update({
                'puntuacion_final': puntuacion_final,
                'categoria': categoria,
                'explicacion_detallada': ' | '.join(explicaciones_cp + explicaciones_hdd),
                'recomendaciones': recomendaciones,
                'fecha_ejecucion': self.fecha_ejecucion
            })
            
            resultados.append(metricas_equipo)
        
        # Crear DataFrame y ordenar por puntuación
        df_resultados = pd.DataFrame(resultados)
        if not df_resultados.empty:
            df_resultados = df_resultados.sort_values('puntuacion_final', ascending=False)
            df_resultados['posicion_ranking'] = range(1, len(df_resultados) + 1)
        
        return df_resultados
    
    def generate_recommendations(self, puntuacion_final, explicaciones_cp, explicaciones_hdd):
        """Genera recomendaciones basadas en las explicaciones"""
        recomendaciones = []
        
        if puntuacion_final < 50:
            recomendaciones.append("Revisión completa del equipo requerida")
        
        # Analizar explicaciones CP
        for explicacion in explicaciones_cp:
            if "Crítica" in explicacion:
                area = explicacion.split()[1]
                recomendaciones.append(f"Intervención inmediata en {area}")
            elif "Regular" in explicacion:
                area = explicacion.split()[1]
                recomendaciones.append(f"Optimizar rendimiento en {area}")
        
        # Analizar explicaciones HDD
        for explicacion in explicaciones_hdd:
            if "Crítico" in explicacion or "Crítica" in explicacion:
                if "Uso HDD" in explicacion:
                    recomendaciones.append("Liberar espacio en disco inmediatamente")
                elif "Estabilidad HDD" in explicacion:
                    recomendaciones.append("Revisar configuración de disco")
                elif "Cambios HDD" in explicacion:
                    recomendaciones.append("Analizar patrones de uso de disco")
        
        if not recomendaciones:
            if puntuacion_final >= 80:
                recomendaciones.append("Mantener estándares actuales")
            else:
                recomendaciones.append("Monitorear rendimiento continuamente")
        
        return '; '.join(recomendaciones)

def main():
    """Función principal"""
    try:
        logger.info("Iniciando sistema de puntuación unificado v2...")
        
        # Crear instancia del sistema
        scoring_system = UnifiedScoringSystemV2()
        
        # Calcular puntuaciones
        resultados = scoring_system.calculate_unified_score()
        
        if not resultados.empty:
            # Guardar resultados
            resultados.to_csv('ranking_unificado_v2.csv', index=False)
            logger.info(f"Resultados guardados en ranking_unificado_v2.csv")
            
            # Mostrar resumen
            print(f"\n=== RESUMEN DE PUNTUACIÓN UNIFICADA V2 ===")
            print(f"Total equipos procesados: {len(resultados)}")
            print(f"Puntuación promedio: {resultados['puntuacion_final'].mean():.2f}")
            print(f"Mejor equipo: {resultados.iloc[0]['equipo']} ({resultados.iloc[0]['puntuacion_final']:.2f} pts)")
            print(f"Peor equipo: {resultados.iloc[-1]['equipo']} ({resultados.iloc[-1]['puntuacion_final']:.2f} pts)")
            
            # Distribución por categorías
            print(f"\nDistribución por categorías:")
            categorias = resultados['categoria'].value_counts()
            for cat, count in categorias.items():
                porcentaje = (count / len(resultados)) * 100
                print(f"  {cat}: {count} equipos ({porcentaje:.1f}%)")
            
            # Mostrar algunos ejemplos de explicaciones
            print(f"\n=== EJEMPLOS DE EXPLICACIONES POR ÁREA ===")
            for i in range(min(3, len(resultados))):
                equipo = resultados.iloc[i]
                print(f"\nEquipo: {equipo['equipo']} (Puntuación: {equipo['puntuacion_final']:.2f})")
                print(f"Áreas CP: {equipo['areas_cp']}")
                print(f"Explicación: {equipo['explicacion_detallada'][:200]}...")
                print(f"Recomendaciones: {equipo['recomendaciones']}")
        
        else:
            logger.error("No se generaron resultados")
            
    except Exception as e:
        logger.error(f"Error en el sistema de puntuación: {str(e)}")
        raise

if __name__ == "__main__":
    main() 