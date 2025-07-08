#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CP Data Analysis v2 - Sistema de Análisis de Datos con Ranking
=============================================================

Este módulo principal ejecuta el análisis de datos de equipos con funcionalidad
de ranking basado en tres métricas clave: llenado, inestabilidad y tasa de cambio.

Autor: Sistema de Análisis CP
Fecha: 2025
"""

import sys
import os
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from cp_config_manager import ConfigManager
from cp_log_manager import LogManager
from cp_upload_data_deploy import DataUploader
from cp_db_manager import DatabaseManager
from cp_ranking_functions import (
    generar_ranking_llenado,
    generar_ranking_inestabilidad,
    generar_ranking_tasa_cambio,
    generar_ranking_combinado
)

class CPDataAnalysisV2:
    """
    Clase principal para el análisis de datos CP v2 con funcionalidad de ranking.
    """
    
    def __init__(self):
        """Inicializar el sistema de análisis."""
        self.config_manager = ConfigManager()
        self.log_manager = LogManager()
        self.db_manager = DatabaseManager()
        self.data_uploader = DataUploader()
        
        # Configurar logging
        self.logger = self.log_manager.get_logger('cp_data_analysis_v2')
        
    def ejecutar_analisis_completo(self):
        """
        Ejecutar el análisis completo incluyendo ranking de equipos.
        """
        try:
            self.logger.info("=== INICIANDO ANÁLISIS CP DATA v2 ===")
            
            # 1. Cargar datos históricos
            self.logger.info("1. Cargando datos históricos...")
            datos_historicos = self.cargar_datos_historicos()
            
            if datos_historicos.empty:
                self.logger.warning("No se encontraron datos históricos para procesar")
                return
            
            self.logger.info(f"Datos cargados: {len(datos_historicos)} registros")
            
            # 2. Generar análisis básico (máximo, mínimo, inestabilidad, tasa de cambio)
            self.logger.info("2. Generando análisis básico...")
            self.generar_analisis_basico(datos_historicos)
            
            # 3. Generar rankings
            self.logger.info("3. Generando rankings de equipos...")
            self.generar_rankings(datos_historicos)
            
            # 4. Guardar resultados
            self.logger.info("4. Guardando resultados...")
            self.guardar_resultados()
            
            self.logger.info("=== ANÁLISIS COMPLETADO EXITOSAMENTE ===")
            
        except Exception as e:
            self.logger.error(f"Error en el análisis: {str(e)}")
            raise
    
    def cargar_datos_historicos(self):
        """
        Cargar datos históricos de los últimos 7 días.
        """
        try:
            # Calcular fecha de inicio (7 días atrás)
            fecha_fin = datetime.now()
            fecha_inicio = fecha_fin - timedelta(days=7)
            
            # Cargar datos usando el uploader
            datos = self.data_uploader.cargar_datos_historicos(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            
            return datos
            
        except Exception as e:
            self.logger.error(f"Error cargando datos históricos: {str(e)}")
            return pd.DataFrame()
    
    def generar_analisis_basico(self, datos):
        """
        Generar análisis básico (máximo, mínimo, inestabilidad, tasa de cambio).
        """
        try:
            # Usar las funciones existentes del sistema original
            from cp_functions_deploy import (
                calcular_maximos,
                calcular_minimos,
                calcular_inestabilidad,
                calcular_tasa_cambio
            )
            
            # Calcular métricas
            maximos = calcular_maximos(datos)
            minimos = calcular_minimos(datos)
            inestabilidad = calcular_inestabilidad(datos)
            tasa_cambio = calcular_tasa_cambio(datos)
            
            # Guardar resultados básicos
            self.db_manager.guardar_resultados_basicos(
                maximos, minimos, inestabilidad, tasa_cambio
            )
            
            self.logger.info("Análisis básico completado")
            
        except Exception as e:
            self.logger.error(f"Error en análisis básico: {str(e)}")
            raise
    
    def generar_rankings(self, datos):
        """
        Generar rankings de equipos basados en las tres métricas principales.
        """
        try:
            # Generar rankings individuales
            ranking_llenado = generar_ranking_llenado(datos)
            ranking_inestabilidad = generar_ranking_inestabilidad(datos)
            ranking_tasa_cambio = generar_ranking_tasa_cambio(datos)
            
            # Generar ranking combinado
            ranking_combinado = generar_ranking_combinado(datos)
            
            # Guardar rankings en la base de datos
            self.db_manager.guardar_rankings(
                ranking_llenado=ranking_llenado,
                ranking_inestabilidad=ranking_inestabilidad,
                ranking_tasa_cambio=ranking_tasa_cambio,
                ranking_combinado=ranking_combinado
            )
            
            self.logger.info("Rankings generados y guardados exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error generando rankings: {str(e)}")
            raise
    
    def guardar_resultados(self):
        """
        Guardar todos los resultados en la base de datos.
        """
        try:
            # Los resultados ya se guardan en los métodos anteriores
            self.logger.info("Todos los resultados han sido guardados")
            
        except Exception as e:
            self.logger.error(f"Error guardando resultados: {str(e)}")
            raise

def main():
    """
    Función principal del programa.
    """
    try:
        # Crear instancia del análisis
        analizador = CPDataAnalysisV2()
        
        # Ejecutar análisis completo
        analizador.ejecutar_analisis_completo()
        
        print("Análisis completado exitosamente. Revisa los logs para más detalles.")
        
    except Exception as e:
        print(f"Error en la ejecución: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 