#!/usr/bin/env python
# coding: utf-8

import os
import json
import yaml
import logging
import datetime
import sqlalchemy
from sqlalchemy import Column, String, Integer, DateTime, Text, MetaData, Table, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
from typing import Dict, Any, Optional, Union

logger = logging.getLogger('hdd_data_analysis')
Base = declarative_base()

class ConfigurationParameter(Base):
    """Model for configuration parameters stored in the database."""
    __tablename__ = 'hdd_an_configuracion'
    
    id_parametro = Column(String(50), primary_key=True)
    nombre_parametro = Column(String(100), nullable=False)
    valor_parametro = Column(Text, nullable=False)
    tipo_dato = Column(String(20), nullable=False)  # int, float, string, bool, json
    descripcion = Column(Text)
    fecha_modificacion = Column(DateTime, default=datetime.datetime.now, 
                              onupdate=datetime.datetime.now)
    
    def __repr__(self):
        return f"<ConfigParam(id='{self.id_parametro}', name='{self.nombre_parametro}', value='{self.valor_parametro}')>"

    def to_dict(self):
        """Convert the parameter to a dictionary."""
        return {
            "id_parametro": self.id_parametro,
            "nombre_parametro": self.nombre_parametro,
            "valor_parametro": self.valor_parametro,
            "tipo_dato": self.tipo_dato,
            "descripcion": self.descripcion,
            "fecha_modificacion": self.fecha_modificacion.isoformat() if self.fecha_modificacion else None
        }
    
    @property
    def value(self):
        """Return the value converted to the appropriate type."""
        if self.tipo_dato == 'int':
            return int(self.valor_parametro)
        elif self.tipo_dato == 'float':
            return float(self.valor_parametro)
        elif self.tipo_dato == 'bool':
            return self.valor_parametro.lower() in ('true', 't', 'yes', 'y', '1')
        elif self.tipo_dato == 'json':
            return json.loads(self.valor_parametro)
        else:  # string and others
            return self.valor_parametro


class ConfigManager:
    """
    Manages application configuration using a combination of database and local file storage.
    
    This class provides functionality to:
    1. Load configuration from database or fallback to a local file
    2. Create or update the configuration table in the database
    3. Export configuration to a file
    4. Reset configuration to default values
    5. Update configuration parameters
    """
    
    DEFAULT_CONFIG_PARAMETERS = {
        "dias_analisis": {
            "nombre_parametro": "Días de Análisis",
            "valor_parametro": "7",
            "tipo_dato": "int",
            "descripcion": "Número de días hacia atrás para realizar los análisis de datos HDD"
        },
        "umbral_maximo": {
            "nombre_parametro": "Umbral Máximo HDD",
            "valor_parametro": "100.0",
            "tipo_dato": "float",
            "descripcion": "Valor máximo aceptable para filtrar datos extremos de uso HDD"
        },
        "umbral_minimo": {
            "nombre_parametro": "Umbral Mínimo HDD",
            "valor_parametro": "0.0",
            "tipo_dato": "float",
            "descripcion": "Valor mínimo aceptable para filtrar datos extremos de uso HDD"
        },
        "frecuencia_ejecucion": {
            "nombre_parametro": "Frecuencia de Ejecución",
            "valor_parametro": "24",
            "tipo_dato": "int",
            "descripcion": "Frecuencia en horas para la ejecución programada"
        },
        "hora_ejecucion": {
            "nombre_parametro": "Hora de Ejecución",
            "valor_parametro": "02:00",
            "tipo_dato": "string",
            "descripcion": "Hora del día (formato HH:MM) para ejecutar el análisis programado"
        },
        "nivel_log": {
            "nombre_parametro": "Nivel de Logging",
            "valor_parametro": "INFO",
            "tipo_dato": "string",
            "descripcion": "Nivel de detalle para la generación de logs (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
        },
        "dias_retencion_logs": {
            "nombre_parametro": "Días de Retención de Logs",
            "valor_parametro": "30",
            "tipo_dato": "int",
            "descripcion": "Número de días para mantener los registros de log antes de eliminarlos"
        },
        "tamano_lote": {
            "nombre_parametro": "Tamaño de Lote",
            "valor_parametro": "1000",
            "tipo_dato": "int",
            "descripcion": "Número de registros a procesar en cada lote durante el análisis por lotes"
        },
        "max_hilos": {
            "nombre_parametro": "Máximo de Hilos",
            "valor_parametro": "4",
            "tipo_dato": "int",
            "descripcion": "Número máximo de hilos para procesamiento paralelo"
        },
        "timeout_db": {
            "nombre_parametro": "Timeout de Base de Datos",
            "valor_parametro": "30",
            "tipo_dato": "int",
            "descripcion": "Timeout en segundos para las operaciones de base de datos"
        },
        "max_reintentos": {
            "nombre_parametro": "Máximo de Reintentos",
            "valor_parametro": "3",
            "tipo_dato": "int",
            "descripcion": "Número máximo de reintentos para operaciones de base de datos fallidas"
        },
        "parametros_analisis": {
            "nombre_parametro": "Parámetros de Análisis",
            "valor_parametro": '{"max": true, "min": true, "inestabilidad": true, "tasa_cambio": true}',
            "tipo_dato": "json",
            "descripcion": "Configuración de qué análisis ejecutar (en formato JSON)"
        },
        "query_datos": {
            "nombre_parametro": "Query de Datos HDD",
            "valor_parametro": "SELECT * FROM dbo.nv_hdd_history",
            "tipo_dato": "string",
            "descripcion": "Consulta SQL para obtener datos de HDD"
        },
        "tabla_resultados": {
            "nombre_parametro": "Tabla de Resultados HDD",
            "valor_parametro": "hdd_an_resultados",
            "tipo_dato": "string",
            "descripcion": "Tabla para guardar resultados de análisis HDD"
        },
        "tabla_promedios": {
            "nombre_parametro": "Tabla de Promedios HDD",
            "valor_parametro": "hdd_an_resultados_promedios",
            "tipo_dato": "string",
            "descripcion": "Tabla para guardar promedios de análisis HDD"
        },
        "columna_agrupacion": {
            "nombre_parametro": "Columna de Agrupación",
            "valor_parametro": "unidad",
            "tipo_dato": "string",
            "descripcion": "Columna para agrupar datos de HDD (unidad)"
        }
    }
    
    def __init__(self, engine=None, config_file_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            engine: SQLAlchemy engine (optional, will be created from config.py if not provided)
            config_file_path: Path to the configuration file (optional)
        """
        self.engine = engine
        # Use HDD-specific config file by default
        if config_file_path is None:
            self.config_file_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'hdd_config_params.yaml')
        else:
            self.config_file_path = config_file_path
        self.config_values = {}
        self.session = None
        self.is_connected = False
        
    def initialize(self):
        """
        Initialize the configuration system.
        - Attempts to connect to the database
        - Creates configuration table if it doesn't exist
        - Loads configuration from DB or falls back to file
        """
        try:
            if not self.engine:
                # Import settings from config.py
                from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
                
                connection_str = f'mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes'
                self.engine = create_engine(connection_str, connect_args={'timeout': 30})
            
            # Test the connection
            with self.engine.connect() as conn:
                self.is_connected = True
                logger.info("Database connection established successfully for HDD configuration")
            
            # Create session for database operations
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
            # Create tables if they don't exist
            self._create_config_table_if_not_exists()
            
            # Load configuration
            self.load_config()
            
        except Exception as e:
            logger.error(f"Failed to initialize database configuration: {str(e)}")
            logger.info("Falling back to file-based configuration")
            self.is_connected = False
            self.load_config_from_file()
    
    def _create_config_table_if_not_exists(self):
        """Create the configuration table if it doesn't exist."""
        try:
            # Create the table
            Base.metadata.create_all(self.engine, tables=[ConfigurationParameter.__table__])
            logger.info("HDD configuration table created or verified")
            
            # Check if table is empty and populate with defaults
            count = self.session.query(ConfigurationParameter).count()
            if count == 0:
                logger.info("Populating HDD configuration table with default values")
                self._populate_config_table()
                
        except Exception as e:
            logger.error(f"Error creating HDD configuration table: {str(e)}")
            raise
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from database or fallback to file.
        
        Returns:
            Dict containing configuration values
        """
        try:
            if self.is_connected:
                return self._load_config_from_db()
            else:
                return self.load_config_from_file()
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return self.load_config_from_file()
    
    def _load_config_from_db(self) -> Dict[str, Any]:
        """Load configuration from database."""
        try:
            config_values = {}
            params = self.session.query(ConfigurationParameter).all()
            
            for param in params:
                config_values[param.id_parametro] = param.value
                
            logger.info(f"Loaded {len(config_values)} configuration parameters from database")
            self.config_values = config_values
            return config_values
            
        except Exception as e:
            logger.error(f"Error loading configuration from database: {str(e)}")
            return {}
    
    def load_config_from_file(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r', encoding='utf-8') as f:
                    config_values = yaml.safe_load(f)
                logger.info(f"Loaded configuration from file: {self.config_file_path}")
            else:
                logger.info("Configuration file not found, creating default file")
                self._create_default_config_file()
                config_values = self._get_default_config_values()
                
            self.config_values = config_values
            return config_values
            
        except Exception as e:
            logger.error(f"Error loading configuration from file: {str(e)}")
            config_values = self._get_default_config_values()
            self.config_values = config_values
            return config_values
    
    def _create_default_config_file(self):
        """Create a default configuration file."""
        try:
            config_values = self._get_default_config_values()
            
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_values, f, default_flow_style=False, allow_unicode=True)
                
            logger.info(f"Created default configuration file: {self.config_file_path}")
            
        except Exception as e:
            logger.error(f"Error creating default configuration file: {str(e)}")
    
    def _get_default_config_values(self) -> Dict[str, Any]:
        """Get default configuration values."""
        config_values = {}
        for param_id, param_info in self.DEFAULT_CONFIG_PARAMETERS.items():
            config_values[param_id] = param_info['valor_parametro']
        return config_values
    
    def _populate_config_table(self, config_values=None):
        """Populate the configuration table with default values."""
        try:
            if config_values is None:
                config_values = self.DEFAULT_CONFIG_PARAMETERS
            
            for param_id, param_info in config_values.items():
                # Check if parameter already exists
                existing = self.session.query(ConfigurationParameter).filter_by(id_parametro=param_id).first()
                
                if not existing:
                    param = ConfigurationParameter(
                        id_parametro=param_id,
                        nombre_parametro=param_info['nombre_parametro'],
                        valor_parametro=param_info['valor_parametro'],
                        tipo_dato=param_info['tipo_dato'],
                        descripcion=param_info['descripcion']
                    )
                    self.session.add(param)
            
            self.session.commit()
            logger.info("HDD configuration table populated with default values")
            
        except Exception as e:
            logger.error(f"Error populating HDD configuration table: {str(e)}")
            self.session.rollback()
            raise
    
    def export_config(self, file_path=None):
        """Export current configuration to a file."""
        try:
            if file_path is None:
                file_path = self.config_file_path
            
            config_data = {}
            for param_id, param_info in self.DEFAULT_CONFIG_PARAMETERS.items():
                value = self.get(param_id, param_info['valor_parametro'])
                config_data[param_id] = {
                    'nombre_parametro': param_info['nombre_parametro'],
                    'valor_parametro': str(value),
                    'tipo_dato': param_info['tipo_dato'],
                    'descripcion': param_info['descripcion']
                }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
                
            logger.info(f"Configuration exported to: {file_path}")
            
        except Exception as e:
            logger.error(f"Error exporting configuration: {str(e)}")
            raise
    
    def update_parameter(self, param_id, new_value, description=None):
        """
        Update a configuration parameter.
        
        Args:
            param_id: Parameter ID
            new_value: New value for the parameter
            description: Optional description update
        """
        try:
            if not self.is_connected:
                logger.warning("Not connected to database, updating file configuration only")
                self.config_values[param_id] = str(new_value)
                self.export_config()
                return
            
            # Find the parameter
            param = self.session.query(ConfigurationParameter).filter_by(id_parametro=param_id).first()
            
            if param:
                # Update existing parameter
                param.valor_parametro = str(new_value)
                if description:
                    param.descripcion = description
                param.fecha_modificacion = datetime.datetime.now()
                logger.info(f"Updated parameter {param_id} to {new_value}")
            else:
                # Create new parameter
                param_info = self.DEFAULT_CONFIG_PARAMETERS.get(param_id, {
                    'nombre_parametro': param_id,
                    'tipo_dato': 'string',
                    'descripcion': description or f'Parameter {param_id}'
                })
                
                param = ConfigurationParameter(
                    id_parametro=param_id,
                    nombre_parametro=param_info['nombre_parametro'],
                    valor_parametro=str(new_value),
                    tipo_dato=param_info['tipo_dato'],
                    descripcion=description or param_info['descripcion']
                )
                self.session.add(param)
                logger.info(f"Created new parameter {param_id} with value {new_value}")
            
            self.session.commit()
            
            # Update local cache
            self.config_values[param_id] = new_value
            
        except Exception as e:
            logger.error(f"Error updating parameter {param_id}: {str(e)}")
            self.session.rollback()
            raise
    
    def reset_to_defaults(self, param_id=None):
        """
        Reset configuration to default values.
        
        Args:
            param_id: Specific parameter to reset (if None, reset all)
        """
        try:
            if param_id:
                # Reset specific parameter
                if param_id in self.DEFAULT_CONFIG_PARAMETERS:
                    default_value = self.DEFAULT_CONFIG_PARAMETERS[param_id]['valor_parametro']
                    self.update_parameter(param_id, default_value)
                    logger.info(f"Reset parameter {param_id} to default value")
                else:
                    logger.warning(f"Parameter {param_id} not found in default configuration")
            else:
                # Reset all parameters
                for param_id, param_info in self.DEFAULT_CONFIG_PARAMETERS.items():
                    self.update_parameter(param_id, param_info['valor_parametro'])
                logger.info("Reset all parameters to default values")
                
        except Exception as e:
            logger.error(f"Error resetting configuration: {str(e)}")
            raise
    
    def get(self, param_id, default_value=None):
        """
        Get a configuration parameter value.
        
        Args:
            param_id: Parameter ID
            default_value: Default value if parameter not found
            
        Returns:
            Parameter value
        """
        if param_id in self.config_values:
            return self.config_values[param_id]
        elif default_value is not None:
            return default_value
        else:
            # Try to get from default configuration
            param_info = self.DEFAULT_CONFIG_PARAMETERS.get(param_id)
            if param_info:
                return param_info['valor_parametro']
            return None
    
    def set(self, param_id, value, description=None):
        """
        Set a configuration parameter value.
        
        Args:
            param_id: Parameter ID
            value: Parameter value
            description: Optional description
        """
        self.update_parameter(param_id, value, description)
    
    def get_all(self):
        """Get all configuration parameters."""
        return self.config_values.copy()
    
    def close(self):
        """Close the configuration manager."""
        if self.session:
            self.session.close()


# Global configuration manager instance
_config_manager = None

def get_config_manager(engine=None, config_file_path=None):
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(engine, config_file_path)
        _config_manager.initialize()
    return _config_manager

def get_config(param_id=None, default_value=None):
    """
    Get a configuration parameter.
    
    Args:
        param_id: Parameter ID
        default_value: Default value if parameter not found
        
    Returns:
        Parameter value or all parameters if param_id is None
    """
    config_manager = get_config_manager()
    if param_id is None:
        return config_manager.get_all()
    return config_manager.get(param_id, default_value)

def set_config(param_id, value, description=None):
    """
    Set a configuration parameter.
    
    Args:
        param_id: Parameter ID
        value: Parameter value
        description: Optional description
    """
    config_manager = get_config_manager()
    config_manager.set(param_id, value, description) 