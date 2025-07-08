#!/usr/bin/env python
# coding: utf-8

"""
Sistema de Puntuación Unificado - CP y HDD Data Analysis
========================================================

Este módulo implementa un sistema de puntuación basado en percentiles que combina
los datos de CP (Control Process) y HDD (Hard Disk Drive) para generar una
puntuación única de 0-100 para cada equipo.

Autor: Sistema de Análisis Unificado
Fecha: 2025
"""

import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger('unified_scoring')

class UnifiedScoringSystem:
    """
    Sistema de puntuación unificado que combina métricas de CP y HDD.
    """
    
    def __init__(self):
        """Inicializar el sistema de puntuación."""
        self.fecha_ejecucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Configuración de métricas y sus contextos
        self.metric_configs = {
            # Variables CP - Mayor valor = Mejor rendimiento
            'cp_llenado': {
                'direction': 'higher_better',
                'weight': 0.15,
                'description': 'Nivel de ocupación promedio del equipo CP'
            },
            'cp_inestabilidad': {
                'direction': 'lower_better',  # Menor inestabilidad = mejor
                'weight': 0.15,
                'description': 'Variabilidad en el rendimiento del equipo CP'
            },
            'cp_tasa_cambio': {
                'direction': 'lower_better',  # Menor tasa de cambio = mejor
                'weight': 0.15,
                'description': 'Velocidad de cambio en el rendimiento CP'
            },
            
            # Variables HDD - Menor valor = Mejor rendimiento
            'hdd_uso': {
                'direction': 'lower_better',  # Menor uso = mejor
                'weight': 0.20,
                'description': 'Nivel de uso promedio del disco duro'
            },
            'hdd_inestabilidad': {
                'direction': 'lower_better',  # Menor inestabilidad = mejor
                'weight': 0.20,
                'description': 'Variabilidad en el uso del disco duro'
            },
            'hdd_tasa_cambio': {
                'direction': 'lower_better',  # Menor tasa de cambio = mejor
                'weight': 0.15,
                'description': 'Velocidad de cambio en el uso del disco duro'
            }
        }
        
        # Verificar que los pesos sumen 1.0
        total_weight = sum(config['weight'] for config in self.metric_configs.values())
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(f"Los pesos de las métricas deben sumar 1.0, actual: {total_weight}")
    
    def calculate_percentile_score(self, value: float, all_values: List[float], 
                                 direction: str = 'higher_better') -> float:
        """
        Calcula la puntuación basada en percentiles.
        
        Args:
            value: Valor del equipo
            all_values: Lista de todos los valores para calcular percentiles
            direction: 'higher_better' o 'lower_better'
            
        Returns:
            float: Puntuación de 0 a 100
        """
        if not all_values or len(all_values) < 2:
            return 50.0  # Puntuación neutral si no hay suficientes datos
        
        # Calcular percentil
        percentile = (sum(1 for x in all_values if x < value) / len(all_values)) * 100
        
        # Ajustar según la dirección
        if direction == 'lower_better':
            # Para métricas donde menor es mejor, invertir el percentil
            percentile = 100 - percentile
        
        return percentile
    
    def get_cp_data(self) -> Dict[str, pd.DataFrame]:
        """
        Obtiene datos de CP desde la base de datos.
        
        Returns:
            Dict con DataFrames de datos CP
        """
        try:
            # Importar componentes CP
            import sys
            sys.path.append('cp_data_analysis_v2/src')
            from cp_upload_data_deploy import upload_data_sql
            
            logger.info("Obteniendo datos CP...")
            cp_data = upload_data_sql()
            
            if not cp_data:
                logger.warning("No se pudieron obtener datos CP")
                return {}
            
            logger.info(f"Datos CP obtenidos: {len(cp_data)} DataFrames")
            return cp_data
            
        except Exception as e:
            logger.error(f"Error obteniendo datos CP: {str(e)}")
            return {}
    
    def get_hdd_data(self) -> Dict[str, pd.DataFrame]:
        """
        Obtiene datos de HDD desde la base de datos.
        
        Returns:
            Dict con DataFrames de datos HDD
        """
        try:
            # Importar componentes HDD
            import sys
            sys.path.append('hdd_data_analysis_v2/src')
            from hdd_upload_data_deploy import upload_data_sql
            
            logger.info("Obteniendo datos HDD...")
            hdd_data = upload_data_sql()
            
            if not hdd_data:
                logger.warning("No se pudieron obtener datos HDD")
                return {}
            
            logger.info(f"Datos HDD obtenidos: {len(hdd_data)} DataFrames")
            return hdd_data
            
        except Exception as e:
            logger.error(f"Error obteniendo datos HDD: {str(e)}")
            return {}
    
    def calculate_cp_metrics(self, cp_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Calcula las métricas de CP para cada equipo.
        
        Args:
            cp_data: Datos de CP
            
        Returns:
            DataFrame con métricas calculadas
        """
        logger.info("Calculando métricas CP...")
        
        all_equipos_data = []
        
        for nombre_df, df in cp_data.items():
            try:
                if df.empty:
                    continue
                
                # Verificar columnas requeridas
                required_cols = {'codigo', 'fecha', 'equipo', 'area', 'valor', 'actualizacion'}
                if not required_cols.issubset(df.columns):
                    continue
                
                # Crear copia y procesar
                df = df.copy()
                df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
                df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
                df = df.dropna(subset=['fecha', 'valor'])
                
                if df.empty:
                    continue
                
                # Filtrar últimos 7 días
                fecha_maxima = df['fecha'].max()
                df_ultimos_7_dias = df[df['fecha'] >= fecha_maxima - timedelta(days=7)]
                
                if df_ultimos_7_dias.empty:
                    continue
                
                # Calcular métricas por equipo
                for equipo in df_ultimos_7_dias['equipo'].unique():
                    df_equipo = df_ultimos_7_dias[df_ultimos_7_dias['equipo'] == equipo]
                    
                    if len(df_equipo) < 3:  # Mínimo 3 registros
                        continue
                    
                    valores = df_equipo['valor'].tolist()
                    
                    # Calcular métricas
                    llenado = np.mean(valores)
                    inestabilidad = np.std(valores) * 1000  # Factor de escala
                    
                    # Calcular tasa de cambio
                    df_equipo_sorted = df_equipo.sort_values('fecha')
                    tasas_cambio = []
                    for i in range(1, len(df_equipo_sorted)):
                        if df_equipo_sorted.iloc[i-1]['valor'] != 0:
                            tasa = ((df_equipo_sorted.iloc[i]['valor'] - df_equipo_sorted.iloc[i-1]['valor']) / 
                                   df_equipo_sorted.iloc[i-1]['valor']) * 100
                            tasas_cambio.append(tasa)
                    
                    tasa_cambio = np.std(tasas_cambio) * 10000 if tasas_cambio else 0
                    
                    all_equipos_data.append({
                        'equipo': equipo,
                        'area': df_equipo['area'].iloc[0],
                        'cp_llenado': llenado,
                        'cp_inestabilidad': inestabilidad,
                        'cp_tasa_cambio': tasa_cambio,
                        'registros_cp': len(df_equipo)
                    })
                    
            except Exception as e:
                logger.error(f"Error procesando DataFrame CP '{nombre_df}': {str(e)}")
                continue
        
        if not all_equipos_data:
            logger.warning("No se pudieron calcular métricas CP")
            return pd.DataFrame()
        
        return pd.DataFrame(all_equipos_data)
    
    def calculate_hdd_metrics(self, hdd_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Calcula las métricas de HDD para cada equipo.
        
        Args:
            hdd_data: Datos de HDD
            
        Returns:
            DataFrame con métricas calculadas
        """
        logger.info("Calculando métricas HDD...")
        
        all_equipos_data = []
        
        for nombre_df, df in hdd_data.items():
            try:
                if df.empty:
                    continue
                
                # Verificar columnas requeridas
                required_cols = {'codigo', 'fecha', 'equipo', 'unidad', 'uso'}
                if not required_cols.issubset(df.columns):
                    continue
                
                # Crear copia y procesar
                df = df.copy()
                df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
                df['uso'] = pd.to_numeric(df['uso'], errors='coerce')
                df = df.dropna(subset=['fecha', 'uso'])
                
                if df.empty:
                    continue
                
                # Filtrar últimos 7 días
                fecha_maxima = df['fecha'].max()
                df_ultimos_7_dias = df[df['fecha'] >= fecha_maxima - timedelta(days=7)]
                
                if df_ultimos_7_dias.empty:
                    continue
                
                # Calcular métricas por equipo-unidad
                for (equipo, unidad) in df_ultimos_7_dias.groupby(['equipo', 'unidad']).groups.keys():
                    df_equipo_unidad = df_ultimos_7_dias[
                        (df_ultimos_7_dias['equipo'] == equipo) & 
                        (df_ultimos_7_dias['unidad'] == unidad)
                    ]
                    
                    if len(df_equipo_unidad) < 3:  # Mínimo 3 registros
                        continue
                    
                    valores = df_equipo_unidad['uso'].tolist()
                    
                    # Calcular métricas
                    uso = np.mean(valores) * 100  # Convertir a porcentaje
                    inestabilidad = np.std(valores) * 1000  # Factor de escala
                    
                    # Calcular tasa de cambio
                    df_equipo_unidad_sorted = df_equipo_unidad.sort_values('fecha')
                    tasas_cambio = []
                    for i in range(1, len(df_equipo_unidad_sorted)):
                        if df_equipo_unidad_sorted.iloc[i-1]['uso'] != 0:
                            tasa = ((df_equipo_unidad_sorted.iloc[i]['uso'] - df_equipo_unidad_sorted.iloc[i-1]['uso']) / 
                                   df_equipo_unidad_sorted.iloc[i-1]['uso']) * 100
                            tasas_cambio.append(tasa)
                    
                    tasa_cambio = np.std(tasas_cambio) * 10000 if tasas_cambio else 0
                    
                    all_equipos_data.append({
                        'equipo': equipo,
                        'unidad': unidad,
                        'hdd_uso': uso,
                        'hdd_inestabilidad': inestabilidad,
                        'hdd_tasa_cambio': tasa_cambio,
                        'registros_hdd': len(df_equipo_unidad)
                    })
                    
            except Exception as e:
                logger.error(f"Error procesando DataFrame HDD '{nombre_df}': {str(e)}")
                continue
        
        if not all_equipos_data:
            logger.warning("No se pudieron calcular métricas HDD")
            return pd.DataFrame()
        
        return pd.DataFrame(all_equipos_data)
    
    def calculate_unified_scores(self, cp_metrics: pd.DataFrame, hdd_metrics: pd.DataFrame, 
                                require_both_sources: bool = True) -> pd.DataFrame:
        """
        Calcula las puntuaciones unificadas basadas en percentiles.
        
        Args:
            cp_metrics: Métricas de CP
            hdd_metrics: Métricas de HDD
            require_both_sources: Si True, solo incluye equipos con datos CP y HDD
            
        Returns:
            DataFrame con puntuaciones unificadas
        """
        logger.info("Calculando puntuaciones unificadas...")
        
        # Combinar datos de CP y HDD
        if cp_metrics.empty and hdd_metrics.empty:
            logger.warning("No hay datos de CP ni HDD para procesar")
            return pd.DataFrame()
        
        # Crear DataFrame base con todos los equipos
        equipos_cp = set(cp_metrics['equipo'].unique()) if not cp_metrics.empty else set()
        equipos_hdd = set(hdd_metrics['equipo'].unique()) if not hdd_metrics.empty else set()
        
        if require_both_sources:
            # Solo equipos que tengan datos de AMBAS fuentes
            todos_equipos = equipos_cp.intersection(equipos_hdd)
            logger.info(f"Modo: Solo equipos con datos CP y HDD")
            logger.info(f"Equipos CP: {len(equipos_cp)}, Equipos HDD: {len(equipos_hdd)}")
            logger.info(f"Equipos con ambas fuentes: {len(todos_equipos)}")
        else:
            # Todos los equipos de cualquier fuente
            todos_equipos = equipos_cp.union(equipos_hdd)
            logger.info(f"Modo: Todos los equipos disponibles")
            logger.info(f"Equipos CP: {len(equipos_cp)}, Equipos HDD: {len(equipos_hdd)}")
            logger.info(f"Total equipos únicos: {len(todos_equipos)}")
        
        if not todos_equipos:
            logger.warning("No hay equipos que cumplan los criterios de inclusión")
            return pd.DataFrame()
        
        resultados = []
        
        for equipo in todos_equipos:
            # Obtener datos CP del equipo
            cp_equipo = cp_metrics[cp_metrics['equipo'] == equipo] if not cp_metrics.empty else pd.DataFrame()
            
            # Obtener datos HDD del equipo
            hdd_equipo = hdd_metrics[hdd_metrics['equipo'] == equipo] if not hdd_metrics.empty else pd.DataFrame()
            
            # Inicializar métricas
            metricas_equipo = {
                'equipo': equipo,
                'area_cp': cp_equipo['area'].iloc[0] if not cp_equipo.empty else None,
                'unidades_hdd': list(hdd_equipo['unidad'].unique()) if not hdd_equipo.empty else [],
                'registros_cp': len(cp_equipo),
                'registros_hdd': len(hdd_equipo)
            }
            
            # Calcular métricas CP (promedio si hay múltiples áreas)
            if not cp_equipo.empty:
                metricas_equipo.update({
                    'cp_llenado': cp_equipo['cp_llenado'].mean(),
                    'cp_inestabilidad': cp_equipo['cp_inestabilidad'].mean(),
                    'cp_tasa_cambio': cp_equipo['cp_tasa_cambio'].mean()
                })
            else:
                metricas_equipo.update({
                    'cp_llenado': None,
                    'cp_inestabilidad': None,
                    'cp_tasa_cambio': None
                })
            
            # Calcular métricas HDD (promedio si hay múltiples unidades)
            if not hdd_equipo.empty:
                metricas_equipo.update({
                    'hdd_uso': hdd_equipo['hdd_uso'].mean(),
                    'hdd_inestabilidad': hdd_equipo['hdd_inestabilidad'].mean(),
                    'hdd_tasa_cambio': hdd_equipo['hdd_tasa_cambio'].mean()
                })
            else:
                metricas_equipo.update({
                    'hdd_uso': None,
                    'hdd_inestabilidad': None,
                    'hdd_tasa_cambio': None
                })
            
            resultados.append(metricas_equipo)
        
        df_resultados = pd.DataFrame(resultados)
        
        # Calcular puntuaciones por percentiles
        for metric_name, config in self.metric_configs.items():
            if metric_name in df_resultados.columns:
                valores_validos = df_resultados[metric_name].dropna()
                
                if len(valores_validos) > 1:
                    # Calcular puntuaciones por percentiles
                    puntuaciones = []
                    for _, row in df_resultados.iterrows():
                        if pd.notna(row[metric_name]):
                            score = self.calculate_percentile_score(
                                row[metric_name], 
                                valores_validos.tolist(), 
                                config['direction']
                            )
                            puntuaciones.append(score)
                        else:
                            puntuaciones.append(50.0)  # Puntuación neutral para valores faltantes
                    
                    df_resultados[f'{metric_name}_score'] = puntuaciones
                else:
                    # Si no hay suficientes datos, asignar puntuación neutral
                    df_resultados[f'{metric_name}_score'] = 50.0
        
        # Calcular puntuación final ponderada
        df_resultados['puntuacion_final'] = 0.0
        
        for metric_name, config in self.metric_configs.items():
            score_col = f'{metric_name}_score'
            if score_col in df_resultados.columns:
                df_resultados['puntuacion_final'] += df_resultados[score_col] * config['weight']
        
        # Agregar información adicional para explicación
        df_resultados['fecha_ejecucion'] = self.fecha_ejecucion
        df_resultados['id'] = [str(uuid.uuid4()) for _ in range(len(df_resultados))]
        
        # Ordenar por puntuación final (descendente)
        df_resultados = df_resultados.sort_values('puntuacion_final', ascending=False)
        
        # Agregar posición en ranking
        df_resultados['posicion_ranking'] = range(1, len(df_resultados) + 1)
        
        logger.info(f"Puntuaciones calculadas para {len(df_resultados)} equipos")
        return df_resultados
    
    def generate_explanation_columns(self, df_scores: pd.DataFrame) -> pd.DataFrame:
        """
        Genera columnas adicionales para explicar las puntuaciones.
        
        Args:
            df_scores: DataFrame con puntuaciones
            
        Returns:
            DataFrame con columnas de explicación
        """
        logger.info("Generando columnas de explicación...")
        
        df_explanation = df_scores.copy()
        
        # Función para categorizar puntuaciones
        def categorize_score(score):
            if score >= 90:
                return "Excelente"
            elif score >= 75:
                return "Muy Bueno"
            elif score >= 50:
                return "Bueno"
            elif score >= 25:
                return "Regular"
            else:
                return "Necesita Mejora"
        
        # Categorizar puntuación final
        df_explanation['categoria_final'] = df_explanation['puntuacion_final'].apply(categorize_score)
        
        # Generar explicación detallada
        explicaciones = []
        for _, row in df_explanation.iterrows():
            explicacion_parts = []
            
            # Explicación CP
            if pd.notna(row['cp_llenado']):
                explicacion_parts.append(f"CP Llenado: {row['cp_llenado_score']:.1f}pts")
            if pd.notna(row['cp_inestabilidad']):
                explicacion_parts.append(f"CP Estabilidad: {row['cp_inestabilidad_score']:.1f}pts")
            if pd.notna(row['cp_tasa_cambio']):
                explicacion_parts.append(f"CP Cambios: {row['cp_tasa_cambio_score']:.1f}pts")
            
            # Explicación HDD
            if pd.notna(row['hdd_uso']):
                explicacion_parts.append(f"HDD Uso: {row['hdd_uso_score']:.1f}pts")
            if pd.notna(row['hdd_inestabilidad']):
                explicacion_parts.append(f"HDD Estabilidad: {row['hdd_inestabilidad_score']:.1f}pts")
            if pd.notna(row['hdd_tasa_cambio']):
                explicacion_parts.append(f"HDD Cambios: {row['hdd_tasa_cambio_score']:.1f}pts")
            
            explicacion = " | ".join(explicacion_parts)
            explicaciones.append(explicacion)
        
        df_explanation['explicacion_detallada'] = explicaciones
        
        # Generar recomendaciones
        recomendaciones = []
        for _, row in df_explanation.iterrows():
            recs = []
            
            # Recomendaciones basadas en métricas bajas
            if pd.notna(row['cp_llenado']) and row['cp_llenado_score'] < 50:
                recs.append("Mejorar ocupación CP")
            if pd.notna(row['cp_inestabilidad']) and row['cp_inestabilidad_score'] < 50:
                recs.append("Reducir variabilidad CP")
            if pd.notna(row['cp_tasa_cambio']) and row['cp_tasa_cambio_score'] < 50:
                recs.append("Estabilizar cambios CP")
            if pd.notna(row['hdd_uso']) and row['hdd_uso_score'] < 50:
                recs.append("Optimizar uso HDD")
            if pd.notna(row['hdd_inestabilidad']) and row['hdd_inestabilidad_score'] < 50:
                recs.append("Reducir variabilidad HDD")
            if pd.notna(row['hdd_tasa_cambio']) and row['hdd_tasa_cambio_score'] < 50:
                recs.append("Estabilizar cambios HDD")
            
            if not recs:
                recs.append("Mantener rendimiento actual")
            
            recomendaciones.append("; ".join(recs))
        
        df_explanation['recomendaciones'] = recomendaciones
        
        return df_explanation
    
    def save_results_to_database(self, df_results: pd.DataFrame) -> bool:
        """
        Guarda los resultados en la base de datos.
        
        Args:
            df_results: DataFrame con resultados
            
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            # Intentar guardar en la base de datos CP
            try:
                import sys
                sys.path.append('cp_data_analysis_v2/src')
                from cp_db_manager import get_db_manager
                
                db_manager = get_db_manager()
                
                # Crear tabla si no existe
                create_table_sql = """
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='nv_unified_scoring' AND xtype='U')
                CREATE TABLE nv_unified_scoring (
                    id VARCHAR(36) PRIMARY KEY,
                    equipo VARCHAR(100) NOT NULL,
                    area_cp VARCHAR(100),
                    unidades_hdd TEXT,
                    puntuacion_final DECIMAL(5,2) NOT NULL,
                    posicion_ranking INT NOT NULL,
                    categoria_final VARCHAR(20) NOT NULL,
                    cp_llenado DECIMAL(10,4),
                    cp_llenado_score DECIMAL(5,2),
                    cp_inestabilidad DECIMAL(10,4),
                    cp_inestabilidad_score DECIMAL(5,2),
                    cp_tasa_cambio DECIMAL(10,4),
                    cp_tasa_cambio_score DECIMAL(5,2),
                    hdd_uso DECIMAL(10,4),
                    hdd_uso_score DECIMAL(5,2),
                    hdd_inestabilidad DECIMAL(10,4),
                    hdd_inestabilidad_score DECIMAL(5,2),
                    hdd_tasa_cambio DECIMAL(10,4),
                    hdd_tasa_cambio_score DECIMAL(5,2),
                    explicacion_detallada TEXT,
                    recomendaciones TEXT,
                    registros_cp INT,
                    registros_hdd INT,
                    fecha_ejecucion DATETIME NOT NULL,
                    fecha_creacion DATETIME DEFAULT GETDATE()
                )
                """
                
                db_manager.execute_query(create_table_sql)
                
                # Insertar datos
                for _, row in df_results.iterrows():
                    insert_sql = """
                    INSERT INTO nv_unified_scoring (
                        id, equipo, area_cp, unidades_hdd, puntuacion_final, posicion_ranking,
                        categoria_final, cp_llenado, cp_llenado_score, cp_inestabilidad, cp_inestabilidad_score,
                        cp_tasa_cambio, cp_tasa_cambio_score, hdd_uso, hdd_uso_score, hdd_inestabilidad,
                        hdd_inestabilidad_score, hdd_tasa_cambio, hdd_tasa_cambio_score,
                        explicacion_detallada, recomendaciones, registros_cp, registros_hdd, fecha_ejecucion
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    unidades_hdd_str = ','.join(row['unidades_hdd']) if row['unidades_hdd'] else None
                    
                    params = (
                        row['id'], row['equipo'], row['area_cp'], unidades_hdd_str,
                        row['puntuacion_final'], row['posicion_ranking'], row['categoria_final'],
                        row['cp_llenado'], row.get('cp_llenado_score', None),
                        row['cp_inestabilidad'], row.get('cp_inestabilidad_score', None),
                        row['cp_tasa_cambio'], row.get('cp_tasa_cambio_score', None),
                        row['hdd_uso'], row.get('hdd_uso_score', None),
                        row['hdd_inestabilidad'], row.get('hdd_inestabilidad_score', None),
                        row['hdd_tasa_cambio'], row.get('hdd_tasa_cambio_score', None),
                        row['explicacion_detallada'], row['recomendaciones'],
                        row['registros_cp'], row['registros_hdd'], row['fecha_ejecucion']
                    )
                    
                    db_manager.execute_query(insert_sql, params)
                
                logger.info(f"Resultados guardados en base de datos CP: {len(df_results)} registros")
                return True
                
            except Exception as e:
                logger.error(f"Error guardando en base de datos CP: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"Error general guardando resultados: {str(e)}")
            return False
    
    def run_complete_analysis(self) -> pd.DataFrame:
        """
        Ejecuta el análisis completo de puntuación unificada.
        
        Returns:
            DataFrame con resultados finales
        """
        logger.info("INICIANDO ANÁLISIS DE PUNTUACIÓN UNIFICADA")
        logger.info("="*60)
        
        try:
            # 1. Obtener datos CP
            logger.info("PASO 1: Obteniendo datos CP...")
            cp_data = self.get_cp_data()
            
            # 2. Obtener datos HDD
            logger.info("PASO 2: Obteniendo datos HDD...")
            hdd_data = self.get_hdd_data()
            
            # 3. Calcular métricas CP
            logger.info("PASO 3: Calculando métricas CP...")
            cp_metrics = self.calculate_cp_metrics(cp_data)
            
            # 4. Calcular métricas HDD
            logger.info("PASO 4: Calculando métricas HDD...")
            hdd_metrics = self.calculate_hdd_metrics(hdd_data)
            
            # 5. Calcular puntuaciones unificadas
            logger.info("PASO 5: Calculando puntuaciones unificadas...")
            # Por defecto, solo equipos con datos CP y HDD
            df_scores = self.calculate_unified_scores(cp_metrics, hdd_metrics, require_both_sources=True)
            
            if df_scores.empty:
                logger.warning("No se pudieron calcular puntuaciones")
                return pd.DataFrame()
            
            # 6. Generar explicaciones
            logger.info("PASO 6: Generando explicaciones...")
            df_results = self.generate_explanation_columns(df_scores)
            
            # 7. Guardar en base de datos
            logger.info("PASO 7: Guardando resultados...")
            self.save_results_to_database(df_results)
            
            # 8. Mostrar resumen
            logger.info("RESUMEN DE RESULTADOS:")
            logger.info(f"   - Total equipos analizados: {len(df_results)}")
            logger.info(f"   - Equipos con datos CP: {df_results['registros_cp'].gt(0).sum()}")
            logger.info(f"   - Equipos con datos HDD: {df_results['registros_hdd'].gt(0).sum()}")
            logger.info(f"   - Puntuación promedio: {df_results['puntuacion_final'].mean():.2f}")
            logger.info(f"   - Mejor puntuación: {df_results['puntuacion_final'].max():.2f}")
            logger.info(f"   - Peor puntuación: {df_results['puntuacion_final'].min():.2f}")
            
            logger.info("ANÁLISIS COMPLETADO EXITOSAMENTE")
            return df_results
            
        except Exception as e:
            logger.error(f"Error en el análisis: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return pd.DataFrame()


def main():
    """
    Función principal para ejecutar el análisis de puntuación unificada.
    """
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/unified_scoring.log'),
            logging.StreamHandler()
        ]
    )
    
    # Crear y ejecutar sistema de puntuación
    scoring_system = UnifiedScoringSystem()
    resultados = scoring_system.run_complete_analysis()
    
    if not resultados.empty:
        print("\n" + "="*80)
        print("TOP 10 EQUIPOS - PUNTUACIÓN UNIFICADA")
        print("="*80)
        
        top_10 = resultados.head(10)
        for _, row in top_10.iterrows():
            print(f"Posición {row['posicion_ranking']:2d}: {str(row['equipo']):20s} - "
                  f"{row['puntuacion_final']:5.2f}pts ({row['categoria_final']})")
            print(f"           Área CP: {row['area_cp'] or 'N/A'}, "
                  f"Unidades HDD: {len(row['unidades_hdd']) if row['unidades_hdd'] else 0}")
            print(f"           Recomendación: {row['recomendaciones']}")
            print()
        
        print("Para ver todos los resultados, consulta la tabla 'nv_unified_scoring'")
    else:
        print("No se pudieron generar resultados")


if __name__ == "__main__":
    main() 