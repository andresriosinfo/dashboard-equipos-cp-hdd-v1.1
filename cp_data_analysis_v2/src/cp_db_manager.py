#!/usr/bin/env python
# coding: utf-8

import json
import logging
import datetime
from typing import Dict, Any, List, Optional, Union

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, MetaData, Table, ForeignKey, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import text

# Import configuration and logging
from cp_config_manager import get_config, get_config_manager
from cp_log_manager import get_log_manager, time_execution

logger = logging.getLogger('cp_data_analysis')
Base = declarative_base()

class DatabaseMetadata(Base):
    """Model for database metadata information."""
    __tablename__ = 'an_metadata'
    
    id_metadata = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String(50), nullable=False, index=True)  # 'schema', 'version', 'stats', etc.
    nombre = Column(String(100), nullable=False, index=True)
    valor = Column(Text, nullable=False)
    descripcion = Column(Text)
    fecha_actualizacion = Column(DateTime, default=datetime.datetime.now, 
                              onupdate=datetime.datetime.now)
    
    def __repr__(self):
        return f"<Metadata(id={self.id_metadata}, type='{self.tipo}', name='{self.nombre}')>"


class ResultadoAnalisis(Base):
    """Base model for analysis results."""
    __tablename__ = 'an_resultados'
    
    id = Column(String(36), primary_key=True)  # UUID
    area = Column(String(100), nullable=False, index=True)
    equipo = Column(String(100), nullable=False, index=True)
    fecha_ejecucion_del_codigo = Column(DateTime, nullable=False, index=True)
    metrica = Column(String(50), nullable=False, index=True)  # 'max', 'min', 'inestabilidad', 'tasa_cambio'
    valor_1 = Column(Integer)
    valor_2 = Column(Integer)
    valor_3 = Column(Integer)
    valor_4 = Column(Integer)
    valor_5 = Column(Integer)
    valor_6 = Column(Integer)
    valor_7 = Column(Integer)
    
    def __repr__(self):
        return f"<ResultadoAnalisis(id='{self.id}', metrica='{self.metrica}', equipo='{self.equipo}')>"


class ResultadoPromedios(Base):
    """Model for average results."""
    __tablename__ = 'an_resultados_promedios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_df = Column(String(100), nullable=False, index=True)
    fecha_creacion = Column(DateTime, nullable=False, index=True)
    promedio_1 = Column(Integer)
    fecha_1 = Column(String(10))
    promedio_2 = Column(Integer)
    fecha_2 = Column(String(10))
    promedio_3 = Column(Integer)
    fecha_3 = Column(String(10))
    promedio_4 = Column(Integer)
    fecha_4 = Column(String(10))
    promedio_5 = Column(Integer)
    fecha_5 = Column(String(10))
    promedio_6 = Column(Integer)
    fecha_6 = Column(String(10))
    promedio_7 = Column(Integer)
    fecha_7 = Column(String(10))
    
    def __repr__(self):
        return f"<ResultadoPromedios(id={self.id}, nombre_df='{self.nombre_df}')>"


class ResultadoRankingCompleto(Base):
    """Model for complete equipment ranking analysis results."""
    __tablename__ = 'nv_cp_analisis_datos_v2'
    
    id = Column(String(36), primary_key=True)  # UUID
    area = Column(String(100), nullable=False, index=True)
    equipo = Column(String(100), nullable=False, index=True)
    fecha_ejecucion_del_codigo = Column(DateTime, nullable=False, index=True)
    metrica = Column(String(50), nullable=False, index=True)  # 'llenado', 'inestabilidad', 'tasa_cambio'
    posicion = Column(Integer, nullable=False, index=True)
    valor_metrico = Column(Integer)  # Using Integer for SQL Server compatibility
    valor_1 = Column(Integer)  # Using Integer for SQL Server compatibility
    valor_2 = Column(Integer)  # Using Integer for SQL Server compatibility
    valor_3 = Column(Integer)  # Using Integer for SQL Server compatibility
    valor_4 = Column(Integer)  # Using Integer for SQL Server compatibility
    valor_5 = Column(Integer)  # Using Integer for SQL Server compatibility
    valor_6 = Column(Integer)  # Using Integer for SQL Server compatibility
    valor_7 = Column(Integer)  # Using Integer for SQL Server compatibility
    
    def __repr__(self):
        return f"<ResultadoRankingCompleto(id={self.id}, equipo='{self.equipo}', metrica='{self.metrica}', posicion={self.posicion})>"


class DatabaseManager:
    """
    Manages database operations, schema creation, and upgrades.
    
    This class provides functionality to:
    1. Create and check required tables
    2. Update table schemas as needed
    3. Save and update metadata about the database
    4. Execute basic database operations with error handling
    """
    
    def __init__(self, engine=None):
        """
        Initialize the database manager.
        
        Args:
            engine: SQLAlchemy engine (optional, will be created from config if not provided)
        """
        self.engine = engine
        self.session = None
        self.is_connected = False
        self.metadata = {}
        
        # Current version information
        self.current_version = "1.0.0"
        self.min_compatible_version = "1.0.0"
        
        # Schema definitions for tables
        self.schema_definitions = {
            'an_metadata': {
                'description': 'Database metadata information',
                'columns': {
                    'id_metadata': {'type': 'Integer', 'primary_key': True, 'autoincrement': True},
                    'tipo': {'type': 'String(50)', 'nullable': False, 'index': True},
                    'nombre': {'type': 'String(100)', 'nullable': False, 'index': True},
                    'valor': {'type': 'Text', 'nullable': False},
                    'descripcion': {'type': 'Text'},
                    'fecha_actualizacion': {'type': 'DateTime', 'default': 'now()'}
                }
            },
            'an_resultados': {
                'description': 'Analysis results for equipment metrics',
                'columns': {
                    'id': {'type': 'String(36)', 'primary_key': True},
                    'area': {'type': 'String(100)', 'nullable': False, 'index': True},
                    'equipo': {'type': 'String(100)', 'nullable': False, 'index': True},
                    'fecha_ejecucion_del_codigo': {'type': 'DateTime', 'nullable': False, 'index': True},
                    'metrica': {'type': 'String(50)', 'nullable': False, 'index': True},
                    'valor_1': {'type': 'Integer'},
                    'valor_2': {'type': 'Integer'},
                    'valor_3': {'type': 'Integer'},
                    'valor_4': {'type': 'Integer'},
                    'valor_5': {'type': 'Integer'},
                    'valor_6': {'type': 'Integer'},
                    'valor_7': {'type': 'Integer'}
                }
            },
            'an_resultados_promedios': {
                'description': 'Daily average results',
                'columns': {
                    'id': {'type': 'Integer', 'primary_key': True, 'autoincrement': True},
                    'nombre_df': {'type': 'String(100)', 'nullable': False, 'index': True},
                    'fecha_creacion': {'type': 'DateTime', 'nullable': False, 'index': True},
                    'promedio_1': {'type': 'Integer'},
                    'fecha_1': {'type': 'String(10)'},
                    'promedio_2': {'type': 'Integer'},
                    'fecha_2': {'type': 'String(10)'},
                    'promedio_3': {'type': 'Integer'},
                    'fecha_3': {'type': 'String(10)'},
                    'promedio_4': {'type': 'Integer'},
                    'fecha_4': {'type': 'String(10)'},
                    'promedio_5': {'type': 'Integer'},
                    'fecha_5': {'type': 'String(10)'},
                    'promedio_6': {'type': 'Integer'},
                    'fecha_6': {'type': 'String(10)'},
                    'promedio_7': {'type': 'Integer'},
                    'fecha_7': {'type': 'String(10)'}
                }
            },
            'nv_cp_analisis_datos_v2': {
                'description': 'Complete equipment ranking analysis results',
                'columns': {
                    'id': {'type': 'String(36)', 'primary_key': True},
                    'area': {'type': 'String(100)', 'nullable': False, 'index': True},
                    'equipo': {'type': 'String(100)', 'nullable': False, 'index': True},
                    'fecha_ejecucion_del_codigo': {'type': 'DateTime', 'nullable': False, 'index': True},
                    'metrica': {'type': 'String(50)', 'nullable': False, 'index': True},
                    'posicion': {'type': 'Integer', 'nullable': False, 'index': True},
                    'valor_metrico': {'type': 'Float', 'nullable': True},
                    'valor_1': {'type': 'Float'},
                    'valor_2': {'type': 'Float'},
                    'valor_3': {'type': 'Float'},
                    'valor_4': {'type': 'Float'},
                    'valor_5': {'type': 'Float'},
                    'valor_6': {'type': 'Float'},
                    'valor_7': {'type': 'Float'}
                }
            }
        }
        
        # Try to connect to the database
        self._connect_to_db()
    
    def _connect_to_db(self):
        """Connect to the database."""
        try:
            if not self.engine:
                # Import settings from config.py
                from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
                
                connection_str = f'mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes'
                self.engine = create_engine(connection_str, connect_args={'timeout': 30})
            
            # Test the connection
            with self.engine.connect() as conn:
                self.is_connected = True
                logger.info("Database connection established successfully for database manager")
            
            # Create session for database operations
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
            # Check and create tables if needed
            self.check_and_create_tables()
            
            # Load metadata
            self.load_metadata()
            
        except Exception as e:
            self.is_connected = False
            self.engine = None
            logger.error(f"Failed to connect to database for database manager: {str(e)}")
    
    @time_execution('db_management')
    def check_and_create_tables(self):
        """Check if required tables exist and create them if needed."""
        if not self.is_connected or not self.session:
            logger.warning("Cannot check tables: not connected to database")
            return False
        
        try:
            # Get existing tables
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names()
            logger.debug(f"Existing tables: {existing_tables}")
            
            # Check and create metadata table first
            if 'an_metadata' not in existing_tables:
                logger.info("Creating metadata table")
                Base.metadata.create_all(self.engine, tables=[DatabaseMetadata.__table__])
                self._initialize_metadata()
            
            # Check and create results tables
            if 'an_resultados' not in existing_tables:
                logger.info("Creating analysis results table")
                Base.metadata.create_all(self.engine, tables=[ResultadoAnalisis.__table__])
            
            if 'an_resultados_promedios' not in existing_tables:
                logger.info("Creating average results table")
                Base.metadata.create_all(self.engine, tables=[ResultadoPromedios.__table__])
            
            if 'nv_cp_analisis_datos_v2' not in existing_tables:
                logger.info("Creating complete ranking analysis table")
                Base.metadata.create_all(self.engine, tables=[ResultadoRankingCompleto.__table__])
            
            # Check and update schemas if needed
            self._check_and_update_schemas()
            
            logger.info("All required tables have been checked and created if needed")
            return True
            
        except Exception as e:
            logger.error(f"Error checking and creating tables: {str(e)}")
            return False
    
    def _initialize_metadata(self):
        """Initialize metadata in the database."""
        try:
            # Add version information
            version_metadata = DatabaseMetadata(
                tipo='version',
                nombre='app_version',
                valor=self.current_version,
                descripcion='Current application version',
                fecha_actualizacion=datetime.datetime.now()
            )
            self.session.add(version_metadata)
            
            # Add schema information
            for table_name, schema_info in self.schema_definitions.items():
                schema_metadata = DatabaseMetadata(
                    tipo='schema',
                    nombre=table_name,
                    valor=json.dumps(schema_info),
                    descripcion=f'Schema definition for {table_name}',
                    fecha_actualizacion=datetime.datetime.now()
                )
                self.session.add(schema_metadata)
            
            self.session.commit()
            logger.info("Metadata initialized successfully")
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error initializing metadata: {str(e)}")
    
    def _check_and_update_schemas(self):
        """Check if table schemas need to be updated and make the necessary changes."""
        try:
            inspector = inspect(self.engine)
            
            # Check each table
            for table_name, schema_info in self.schema_definitions.items():
                # Skip if table doesn't exist yet
                if not inspector.has_table(table_name):
                    continue
                
                # Get existing columns
                existing_columns = {col['name']: col for col in inspector.get_columns(table_name)}
                
                # Check if columns need to be added
                schema_columns = schema_info['columns']
                missing_columns = set(schema_columns.keys()) - set(existing_columns.keys())
                
                if missing_columns:
                    logger.info(f"Missing columns found in {table_name}: {missing_columns}")
                    
                    # Add missing columns using SQL
                    for col_name in missing_columns:
                        col_def = schema_columns[col_name]
                        col_type_str = col_def['type']
                        
                        # Convert SQLAlchemy type syntax to SQL Server syntax
                        if col_type_str.startswith('String'):
                            length = col_type_str.split('(')[1].split(')')[0]
                            sql_type = f"NVARCHAR({length})"
                        elif col_type_str == 'Text':
                            sql_type = "NVARCHAR(MAX)"
                        elif col_type_str == 'Integer':
                            sql_type = "INT"
                        elif col_type_str == 'DateTime':
                            sql_type = "DATETIME"
                        else:
                            sql_type = col_type_str
                        
                        # Nullable clause
                        nullable_clause = "NULL" if col_def.get('nullable', True) else "NOT NULL"
                        
                        # Create ALTER TABLE statement
                        alter_statement = f"ALTER TABLE {table_name} ADD {col_name} {sql_type} {nullable_clause}"
                        
                        # Execute the statement
                        with self.engine.connect() as connection:
                            connection.execute(text(alter_statement))
                        
                        logger.info(f"Added column {col_name} to {table_name}")
            
            # Update schema metadata
            for table_name, schema_info in self.schema_definitions.items():
                # Get current schema metadata
                current_schema = self.session.query(DatabaseMetadata).filter_by(
                    tipo='schema', nombre=table_name).first()
                
                if current_schema:
                    # Update the metadata
                    current_schema.valor = json.dumps(schema_info)
                    current_schema.fecha_actualizacion = datetime.datetime.now()
                else:
                    # Create new metadata
                    new_schema = DatabaseMetadata(
                        tipo='schema',
                        nombre=table_name,
                        valor=json.dumps(schema_info),
                        descripcion=f'Schema definition for {table_name}',
                        fecha_actualizacion=datetime.datetime.now()
                    )
                    self.session.add(new_schema)
            
            self.session.commit()
            logger.info("Schema check and update completed successfully")
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error checking and updating schemas: {str(e)}")
    
    def load_metadata(self):
        """Load metadata from the database."""
        if not self.is_connected or not self.session:
            logger.warning("Cannot load metadata: not connected to database")
            return
        
        try:
            # Query all metadata
            metadata_records = self.session.query(DatabaseMetadata).all()
            
            # Convert to dictionary
            for record in metadata_records:
                key = f"{record.tipo}:{record.nombre}"
                self.metadata[key] = record.valor
            
            logger.debug(f"Loaded {len(metadata_records)} metadata records")
            
        except Exception as e:
            logger.error(f"Error loading metadata: {str(e)}")
    
    def get_metadata(self, tipo, nombre, default=None):
        """
        Get a metadata value.
        
        Args:
            tipo: Type of metadata
            nombre: Name of metadata
            default: Default value if not found
        
        Returns:
            Metadata value or default
        """
        key = f"{tipo}:{nombre}"
        return self.metadata.get(key, default)
    
    def set_metadata(self, tipo, nombre, valor, descripcion=None):
        """
        Set a metadata value.
        
        Args:
            tipo: Type of metadata
            nombre: Name of metadata
            valor: Value to set
            descripcion: Description (optional)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected or not self.session:
            logger.warning("Cannot set metadata: not connected to database")
            return False
        
        try:
            # Check if metadata exists
            record = self.session.query(DatabaseMetadata).filter_by(
                tipo=tipo, nombre=nombre).first()
            
            if record:
                # Update existing record
                record.valor = valor
                record.fecha_actualizacion = datetime.datetime.now()
                if descripcion:
                    record.descripcion = descripcion
            else:
                # Create new record
                new_record = DatabaseMetadata(
                    tipo=tipo,
                    nombre=nombre,
                    valor=valor,
                    descripcion=descripcion,
                    fecha_actualizacion=datetime.datetime.now()
                )
                self.session.add(new_record)
            
            self.session.commit()
            
            # Update in-memory metadata
            key = f"{tipo}:{nombre}"
            self.metadata[key] = valor
            
            logger.debug(f"Set metadata {tipo}:{nombre} = {valor}")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error setting metadata: {str(e)}")
            return False
    
    @time_execution('db_query')
    def execute_query(self, query, params=None):
        """
        Execute a SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
        
        Returns:
            Result of the query
        """
        if not self.is_connected or not self.engine:
            logger.warning("Cannot execute query: not connected to database")
            return None
        
        try:
            with self.engine.connect() as connection:
                if params:
                    result = connection.execute(text(query), params)
                else:
                    result = connection.execute(text(query))
                
                # Convert to list of dictionaries
                if result.returns_rows:
                    keys = result.keys()
                    return [dict(zip(keys, row)) for row in result]
                return None
                
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            logger.debug(f"Query: {query}")
            logger.debug(f"Params: {params}")
            return None
    
    @time_execution('db_write')
    def save_results(self, results_df, results_type='analisis'):
        """
        Save results to the appropriate table.
        
        Args:
            results_df: DataFrame with results
            results_type: Type of results ('analisis', 'promedios', or 'ranking_completo')
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected or not self.session:
            logger.warning("Cannot save results: not connected to database")
            return False
        
        try:
            # Determine target table
            if results_type == 'ranking_completo':
                table_name = 'nv_cp_analisis_datos_v2'
            elif results_type == 'analisis':
                table_name = 'an_resultados'
            else:
                table_name = 'an_resultados_promedios'
            
            if_exists = 'append'  # Default behavior
            
            # Check if custom storage behavior is configured
            storage_mode = get_config('db_resultados_modo', 'append')
            if storage_mode == 'replace':
                if_exists = 'replace'
            
            # Convert DataFrame to SQL
            results_df.to_sql(table_name, self.engine, if_exists=if_exists, index=False)
            
            logger.info(f"Saved {len(results_df)} {results_type} results to {table_name}")
            
            # Update stats metadata
            now = datetime.datetime.now()
            stats = {
                'last_update': now.isoformat(),
                'record_count': len(results_df),
                'table': table_name
            }
            
            self.set_metadata('stats', f'last_{results_type}_update', 
                            json.dumps(stats), 
                            f'Statistics for last {results_type} update')
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            return False
    
    def close(self):
        """Close database connections."""
        if self.session:
            self.session.close()


# Create a singleton instance
db_manager = None

def get_db_manager(engine=None):
    """
    Get the database manager singleton instance.
    
    Args:
        engine: SQLAlchemy engine (optional)
    
    Returns:
        DatabaseManager instance
    """
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager(engine)
    return db_manager

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    manager = get_db_manager()
    print("Metadata:", manager.metadata)