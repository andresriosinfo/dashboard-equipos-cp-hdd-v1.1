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

logger = logging.getLogger('cp_data_analysis')
Base = declarative_base()

class ConfigurationParameter(Base):
    """Model for configuration parameters stored in the database."""
    __tablename__ = 'an_configuracion'
    
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
            "descripcion": "Número de días hacia atrás para realizar los análisis de datos"
        },
        "umbral_maximo": {
            "nombre_parametro": "Umbral Máximo",
            "valor_parametro": "1000.0",
            "tipo_dato": "float",
            "descripcion": "Valor máximo aceptable para filtrar datos extremos"
        },
        "umbral_minimo": {
            "nombre_parametro": "Umbral Mínimo",
            "valor_parametro": "0.0",
            "tipo_dato": "float",
            "descripcion": "Valor mínimo aceptable para filtrar datos extremos"
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
        self.config_file_path = config_file_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'config_params.yaml')
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
                logger.info("Database connection established successfully for configuration")
            
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
            # Check if the table exists
            inspector = sqlalchemy.inspect(self.engine)
            if 'an_configuracion' not in inspector.get_table_names():
                logger.info("Creating an_configuracion table")
                Base.metadata.create_all(self.engine)
                logger.info("an_configuracion table created successfully")
            else:
                logger.debug("an_configuracion table already exists")
        except Exception as e:
            logger.error(f"Error creating configuration table: {str(e)}")
            raise
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from the database or file.
        
        If database connection is available:
        - Load from database
        - If table is empty, load from file and populate the table
        
        If database connection is not available:
        - Load from file
        
        Returns:
            Dictionary containing configuration parameters
        """
        if self.is_connected:
            try:
                # Try to load from database
                db_params = self._load_config_from_db()
                
                if not db_params:
                    # Table is empty, load from file and populate DB
                    logger.info("Configuration table is empty, loading defaults")
                    file_params = self.load_config_from_file()
                    self._populate_config_table(file_params)
                    self.config_values = file_params
                else:
                    self.config_values = db_params
                    # Export current DB config to file for backup
                    self.export_config()
                
            except Exception as e:
                logger.error(f"Error loading configuration from database: {str(e)}")
                logger.info("Falling back to file-based configuration")
                self.config_values = self.load_config_from_file()
        else:
            # Load from file if not connected to DB
            self.config_values = self.load_config_from_file()
        
        return self.config_values
    
    def _load_config_from_db(self) -> Dict[str, Any]:
        """
        Load configuration parameters from the database.
        
        Returns:
            Dictionary of configuration parameters
        """
        try:
            # Query all parameters from the database
            params = self.session.query(ConfigurationParameter).all()
            
            # Convert to dictionary
            config_dict = {}
            for param in params:
                config_dict[param.id_parametro] = param.value
            
            if config_dict:
                logger.info(f"Loaded {len(config_dict)} configuration parameters from database")
            
            return config_dict
            
        except Exception as e:
            logger.error(f"Error loading configuration from database: {str(e)}")
            raise
    
    def load_config_from_file(self) -> Dict[str, Any]:
        """
        Load configuration from a file.
        
        If the file doesn't exist, it creates one with default values.
        
        Returns:
            Dictionary containing configuration parameters
        """
        if not os.path.exists(self.config_file_path):
            logger.info(f"Configuration file {self.config_file_path} not found, creating with defaults")
            self._create_default_config_file()
        
        try:
            # Determine file type (JSON or YAML) based on extension
            file_ext = os.path.splitext(self.config_file_path)[1].lower()
            
            with open(self.config_file_path, 'r') as file:
                if file_ext in ['.yaml', '.yml']:
                    config_data = yaml.safe_load(file)
                else:  # Default to JSON
                    config_data = json.load(file)
            
            # Process the loaded data
            result = {}
            for key, param_dict in config_data.items():
                # Convert based on tipo_dato
                if param_dict.get('tipo_dato') == 'int':
                    result[key] = int(param_dict['valor_parametro'])
                elif param_dict.get('tipo_dato') == 'float':
                    result[key] = float(param_dict['valor_parametro'])
                elif param_dict.get('tipo_dato') == 'bool':
                    result[key] = param_dict['valor_parametro'].lower() in ('true', 't', 'yes', 'y', '1')
                elif param_dict.get('tipo_dato') == 'json':
                    if isinstance(param_dict['valor_parametro'], str):
                        result[key] = json.loads(param_dict['valor_parametro'])
                    else:
                        result[key] = param_dict['valor_parametro']
                else:  # string and others
                    result[key] = param_dict['valor_parametro']
            
            logger.info(f"Loaded {len(result)} configuration parameters from file")
            return result
            
        except Exception as e:
            logger.error(f"Error loading configuration from file: {str(e)}")
            logger.info("Falling back to default configuration")
            # If there's an error loading the file, use defaults
            return self._get_default_config_values()
    
    def _create_default_config_file(self):
        """Create a default configuration file."""
        try:
            file_ext = os.path.splitext(self.config_file_path)[1].lower()
            
            with open(self.config_file_path, 'w') as file:
                if file_ext in ['.yaml', '.yml']:
                    yaml.dump(self.DEFAULT_CONFIG_PARAMETERS, file, default_flow_style=False)
                else:  # Default to JSON
                    json.dump(self.DEFAULT_CONFIG_PARAMETERS, file, indent=2)
            
            logger.info(f"Created default configuration file at {self.config_file_path}")
            
        except Exception as e:
            logger.error(f"Error creating default configuration file: {str(e)}")
    
    def _get_default_config_values(self) -> Dict[str, Any]:
        """
        Get default configuration values converted to their appropriate types.
        
        Returns:
            Dictionary of default configuration values
        """
        defaults = {}
        for key, param_dict in self.DEFAULT_CONFIG_PARAMETERS.items():
            if param_dict['tipo_dato'] == 'int':
                defaults[key] = int(param_dict['valor_parametro'])
            elif param_dict['tipo_dato'] == 'float':
                defaults[key] = float(param_dict['valor_parametro'])
            elif param_dict['tipo_dato'] == 'bool':
                defaults[key] = param_dict['valor_parametro'].lower() in ('true', 't', 'yes', 'y', '1')
            elif param_dict['tipo_dato'] == 'json':
                if isinstance(param_dict['valor_parametro'], str):
                    defaults[key] = json.loads(param_dict['valor_parametro'])
                else:
                    defaults[key] = param_dict['valor_parametro']
            else:  # string and others
                defaults[key] = param_dict['valor_parametro']
        
        return defaults
    
    def _populate_config_table(self, config_values=None):
        """
        Populate the configuration table with values (default or provided).
        
        Args:
            config_values: Dictionary of configuration values to use (optional)
                           If not provided, default values will be used
        """
        if not self.is_connected:
            logger.warning("Cannot populate configuration table: not connected to database")
            return
        
        try:
            # Use provided values or defaults
            params_data = self.DEFAULT_CONFIG_PARAMETERS
            
            # Add parameters to the database
            for param_id, param_data in params_data.items():
                # Check if parameter already exists
                existing = self.session.query(ConfigurationParameter).filter_by(
                    id_parametro=param_id).first()
                
                if existing:
                    logger.debug(f"Parameter {param_id} already exists in database")
                    continue
                
                # Create new parameter
                new_param = ConfigurationParameter(
                    id_parametro=param_id,
                    nombre_parametro=param_data['nombre_parametro'],
                    valor_parametro=param_data['valor_parametro'],
                    tipo_dato=param_data['tipo_dato'],
                    descripcion=param_data['descripcion'],
                    fecha_modificacion=datetime.datetime.now()
                )
                
                self.session.add(new_param)
            
            self.session.commit()
            logger.info(f"Added {len(params_data)} parameters to configuration table")
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error populating configuration table: {str(e)}")
    
    def export_config(self, file_path=None):
        """
        Export current configuration to a file.
        
        Args:
            file_path: Path to save the configuration (optional)
                      If not provided, the default config file path will be used
        """
        file_path = file_path or self.config_file_path
        
        try:
            # If connected to DB, get all parameters
            if self.is_connected:
                params = self.session.query(ConfigurationParameter).all()
                config_data = {p.id_parametro: p.to_dict() for p in params}
            else:
                # Create config data from current values
                config_data = {}
                for key, value in self.config_values.items():
                    if key in self.DEFAULT_CONFIG_PARAMETERS:
                        param_data = self.DEFAULT_CONFIG_PARAMETERS[key].copy()
                        param_data['valor_parametro'] = str(value)
                        config_data[key] = param_data
            
            # Determine file type based on extension
            file_ext = os.path.splitext(file_path)[1].lower()
            
            with open(file_path, 'w') as file:
                if file_ext in ['.yaml', '.yml']:
                    yaml.dump(config_data, file, default_flow_style=False)
                else:  # Default to JSON
                    json.dump(config_data, file, indent=2)
            
            logger.info(f"Exported configuration to {file_path}")
            
        except Exception as e:
            logger.error(f"Error exporting configuration: {str(e)}")
    
    def update_parameter(self, param_id, new_value, description=None):
        """
        Update a configuration parameter.
        
        Args:
            param_id: ID of the parameter to update
            new_value: New value for the parameter
            description: New description (optional)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            logger.warning("Cannot update parameter: not connected to database")
            # Update in-memory configuration
            self.config_values[param_id] = new_value
            # Try to update file
            self.export_config()
            return True
        
        try:
            # Find parameter in database
            param = self.session.query(ConfigurationParameter).filter_by(
                id_parametro=param_id).first()
            
            if not param:
                logger.warning(f"Parameter {param_id} not found in database")
                return False
            
            # Convert value to string for storage
            if param.tipo_dato == 'json' and not isinstance(new_value, str):
                param.valor_parametro = json.dumps(new_value)
            else:
                param.valor_parametro = str(new_value)
            
            # Update description if provided
            if description:
                param.descripcion = description
            
            param.fecha_modificacion = datetime.datetime.now()
            
            self.session.commit()
            
            # Update in-memory configuration
            if param.tipo_dato == 'int':
                self.config_values[param_id] = int(param.valor_parametro)
            elif param.tipo_dato == 'float':
                self.config_values[param_id] = float(param.valor_parametro)
            elif param.tipo_dato == 'bool':
                self.config_values[param_id] = param.valor_parametro.lower() in ('true', 't', 'yes', 'y', '1')
            elif param.tipo_dato == 'json':
                self.config_values[param_id] = json.loads(param.valor_parametro)
            else:  # string and others
                self.config_values[param_id] = param.valor_parametro
            
            # Export to file for backup
            self.export_config()
            
            logger.info(f"Updated parameter {param_id} to {new_value}")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating parameter {param_id}: {str(e)}")
            return False
    
    def reset_to_defaults(self, param_id=None):
        """
        Reset configuration to default values.
        
        Args:
            param_id: Specific parameter to reset (optional)
                      If not provided, all parameters will be reset
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            logger.warning("Cannot reset parameters: not connected to database")
            # Reset in-memory configuration
            if param_id:
                if param_id in self.DEFAULT_CONFIG_PARAMETERS:
                    param_data = self.DEFAULT_CONFIG_PARAMETERS[param_id]
                    if param_data['tipo_dato'] == 'int':
                        self.config_values[param_id] = int(param_data['valor_parametro'])
                    elif param_data['tipo_dato'] == 'float':
                        self.config_values[param_id] = float(param_data['valor_parametro'])
                    elif param_data['tipo_dato'] == 'bool':
                        self.config_values[param_id] = param_data['valor_parametro'].lower() in ('true', 't', 'yes', 'y', '1')
                    elif param_data['tipo_dato'] == 'json':
                        self.config_values[param_id] = json.loads(param_data['valor_parametro'])
                    else:  # string and others
                        self.config_values[param_id] = param_data['valor_parametro']
            else:
                self.config_values = self._get_default_config_values()
            
            # Update file
            self.export_config()
            return True
        
        try:
            if param_id:
                # Reset specific parameter
                if param_id in self.DEFAULT_CONFIG_PARAMETERS:
                    param_data = self.DEFAULT_CONFIG_PARAMETERS[param_id]
                    param = self.session.query(ConfigurationParameter).filter_by(
                        id_parametro=param_id).first()
                    
                    if param:
                        param.valor_parametro = param_data['valor_parametro']
                        param.fecha_modificacion = datetime.datetime.now()
                    else:
                        # Parameter doesn't exist, create it
                        new_param = ConfigurationParameter(
                            id_parametro=param_id,
                            nombre_parametro=param_data['nombre_parametro'],
                            valor_parametro=param_data['valor_parametro'],
                            tipo_dato=param_data['tipo_dato'],
                            descripcion=param_data['descripcion'],
                            fecha_modificacion=datetime.datetime.now()
                        )
                        self.session.add(new_param)
                
                    self.session.commit()
                    logger.info(f"Reset parameter {param_id} to default value")
                else:
                    logger.warning(f"Parameter {param_id} not found in defaults")
                    return False
            else:
                # Reset all parameters
                # Delete all existing parameters
                self.session.query(ConfigurationParameter).delete()
                self.session.commit()
                
                # Repopulate with defaults
                self._populate_config_table()
                logger.info("Reset all parameters to default values")
            
            # Reload configuration
            self.load_config()
            
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error resetting parameters: {str(e)}")
            return False
    
    def get(self, param_id, default_value=None):
        """
        Get a configuration parameter value.
        
        Args:
            param_id: ID of the parameter to get
            default_value: Default value to return if parameter not found
        
        Returns:
            Parameter value or default value if not found
        """
        return self.config_values.get(param_id, default_value)
    
    def set(self, param_id, value, description=None):
        """
        Set a configuration parameter value.
        
        Args:
            param_id: ID of the parameter to set
            value: Value to set
            description: Description of the parameter (optional)
        
        Returns:
            True if successful, False otherwise
        """
        return self.update_parameter(param_id, value, description)
    
    def get_all(self):
        """
        Get all configuration parameters.
        
        Returns:
            Dictionary of all configuration parameters
        """
        return self.config_values.copy()
    
    def close(self):
        """Close database connections."""
        if self.session:
            self.session.close()


# Create a singleton instance
config_manager = None

def get_config_manager(engine=None, config_file_path=None):
    """
    Get the configuration manager singleton instance.
    
    Args:
        engine: SQLAlchemy engine (optional)
        config_file_path: Path to configuration file (optional)
    
    Returns:
        ConfigManager instance
    """
    global config_manager
    if config_manager is None:
        config_manager = ConfigManager(engine, config_file_path)
        config_manager.initialize()
    return config_manager

def get_config(param_id=None, default_value=None):
    """
    Get a configuration parameter or all parameters.
    
    Args:
        param_id: ID of the parameter to get (optional)
                  If not provided, all parameters will be returned
        default_value: Default value to return if parameter not found (optional)
    
    Returns:
        Parameter value, default value, or dictionary of all parameters
    """
    manager = get_config_manager()
    if param_id is None:
        return manager.get_all()
    return manager.get(param_id, default_value)

def set_config(param_id, value, description=None):
    """
    Set a configuration parameter.
    
    Args:
        param_id: ID of the parameter to set
        value: Value to set
        description: Description of the parameter (optional)
    
    Returns:
        True if successful, False otherwise
    """
    manager = get_config_manager()
    return manager.set(param_id, value, description)

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    manager = get_config_manager()
    print("Configuration:", manager.get_all())