#!/usr/bin/env python
# coding: utf-8

import os
import logging
import datetime
import time
import uuid
import json
import sqlalchemy
from sqlalchemy import Column, String, Integer, DateTime, Text, Float, MetaData, Table, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
from typing import Dict, Any, Optional, Union, List

logger = logging.getLogger('hdd_data_analysis')
Base = declarative_base()

class MetadataEntry(Base):
    """Model for metadata entries stored in the database."""
    __tablename__ = 'hdd_an_metadata'
    
    id_metadata = Column(String(50), primary_key=True)
    categoria = Column(String(100), nullable=False)
    clave = Column(String(100), nullable=False)
    valor = Column(Text, nullable=False)
    descripcion = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    
    def __repr__(self):
        return f"<MetadataEntry(category='{self.categoria}', key='{self.clave}', value='{self.valor[:50]}...')>"

class DatabaseManager:
    """
    Manages database operations for the HDD analysis application.
    
    This class provides functionality to:
    1. Create and manage database tables
    2. Execute queries with error handling
    3. Save analysis results
    4. Manage database metadata
    5. Handle database schema updates
    """
    
    def __init__(self, engine=None):
        """
        Initialize the database manager.
        
        Args:
            engine: SQLAlchemy engine (optional, will be created from config.py if not provided)
        """
        self.engine = engine
        self.session_maker = None
        self.is_connected = False
        self.metadata = MetaData()
        
    def initialize(self):
        """
        Initialize the database system.
        - Attempts to connect to the database
        - Creates required tables if they don't exist
        - Sets up database schema
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
                logger.info("Database connection established successfully for HDD operations")
            
            # Create session maker
            self.session_maker = sessionmaker(bind=self.engine)
            
            # Create tables if they don't exist
            self._create_tables_if_not_exists()
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            self.is_connected = False
    
    def _create_tables_if_not_exists(self):
        """Create the required tables if they don't exist."""
        try:
            # Create metadata table
            Base.metadata.create_all(self.engine, tables=[MetadataEntry.__table__])
            logger.info("HDD metadata table created or verified")
            
            # Create results tables
            self._create_results_tables()
            
        except Exception as e:
            logger.error(f"Error creating HDD database tables: {str(e)}")
            raise
    
    def _create_results_tables(self):
        """Create the results tables for HDD analysis."""
        try:
            # Table for analysis results
            hdd_an_resultados = Table(
                'hdd_an_resultados', 
                self.metadata,
                Column('id', String(50), primary_key=True),
                Column('unidad', String(100)),
                Column('equipo', String(100)),
                Column('fecha_ejecucion_del_codigo', DateTime),
                Column('metrica', String(50)),
                Column('posicion', Integer),
                Column('valor_metrico', Integer),
                Column('valor_1', Integer),
                Column('valor_2', Integer),
                Column('valor_3', Integer),
                Column('valor_4', Integer),
                Column('valor_5', Integer),
                Column('valor_6', Integer),
                Column('valor_7', Integer)
            )
            
            # Table for average results
            hdd_an_resultados_promedios = Table(
                'hdd_an_resultados_promedios', 
                self.metadata,
                Column('id', String(50), primary_key=True),
                Column('unidad', String(100)),
                Column('equipo', String(100)),
                Column('fecha', DateTime),
                Column('promedio_uso', Float),
                Column('fecha_ejecucion_del_codigo', DateTime)
            )
            
            # Table for HDD rankings v2
            nv_hdd_analisis_datos_v2 = Table(
                'nv_hdd_analisis_datos_v2', 
                self.metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('fecha_analisis', DateTime),
                Column('equipo', String(50)),
                Column('unidad', String(50)),
                Column('tipo_ranking', String(20)),
                Column('posicion', Integer),
                Column('valor_metrico', Float),
                Column('total_equipos', Integer),
                Column('detalles_uso', Text),
                Column('fecha_creacion', DateTime, default=datetime.datetime.now)
            )
            
            # Create tables
            self.metadata.create_all(self.engine)
            logger.info("HDD results tables created or verified")
            
        except Exception as e:
            logger.error(f"Error creating HDD results tables: {str(e)}")
            raise
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> Optional[List[Dict]]:
        """
        Execute a SQL query and return results.
        
        Args:
            query: SQL query to execute
            params: Query parameters (optional)
            
        Returns:
            List of dictionaries with query results or None if error
        """
        try:
            if not self.is_connected:
                logger.error("Not connected to database")
                return None
            
            with self.engine.connect() as conn:
                if params:
                    result = conn.execute(sqlalchemy.text(query), params)
                else:
                    result = conn.execute(sqlalchemy.text(query))
                
                # Convert to list of dictionaries
                columns = result.keys()
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
                
                logger.info(f"Query executed successfully: {len(rows)} rows returned")
                return rows
                
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return None
    
    def save_results(self, df: pd.DataFrame, result_type: str):
        """
        Save analysis results to the appropriate table.
        
        Args:
            df: DataFrame with results to save
            result_type: Type of results ('analisis' or 'promedios')
        """
        try:
            if not self.is_connected:
                logger.error("Not connected to database")
                return False
            
            if df.empty:
                logger.warning(f"DataFrame is empty, nothing to save for {result_type}")
                return False
            
            # Get table name based on result type
            if result_type == 'analisis':
                table_name = 'hdd_an_resultados'
            elif result_type == 'promedios':
                table_name = 'hdd_an_resultados_promedios'
            else:
                logger.error(f"Unknown result type: {result_type}")
                return False
            
            # Clear existing data in the table
            with self.engine.connect() as conn:
                conn.execute(sqlalchemy.text(f"DELETE FROM {table_name}"))
                conn.commit()
                logger.info(f"Cleared existing data from {table_name}")
            
            # Save new data
            df.to_sql(table_name, con=self.engine, if_exists='append', index=False)
            
            logger.info(f"Saved {len(df)} records to {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving results to {result_type}: {str(e)}")
            return False
    
    def set_metadata(self, category: str, key: str, value: str, description: str = None):
        """
        Set metadata in the database.
        
        Args:
            category: Metadata category
            key: Metadata key
            value: Metadata value
            description: Optional description
        """
        try:
            if not self.is_connected:
                logger.warning("Not connected to database, metadata not saved")
                return
            
            session = self.session_maker()
            
            # Check if metadata entry exists
            existing = session.query(MetadataEntry).filter_by(
                categoria=category, 
                clave=key
            ).first()
            
            if existing:
                # Update existing entry
                existing.valor = value
                if description:
                    existing.descripcion = description
                existing.timestamp = datetime.datetime.now()
                logger.debug(f"Updated metadata {category}.{key}")
            else:
                # Create new entry
                metadata_entry = MetadataEntry(
                    id_metadata=str(uuid.uuid4()),
                    categoria=category,
                    clave=key,
                    valor=value,
                    descripcion=description,
                    timestamp=datetime.datetime.now()
                )
                session.add(metadata_entry)
                logger.debug(f"Created metadata {category}.{key}")
            
            session.commit()
            session.close()
            
        except Exception as e:
            logger.error(f"Error setting metadata {category}.{key}: {str(e)}")
    
    def get_metadata(self, category: str, key: str) -> Optional[str]:
        """
        Get metadata from the database.
        
        Args:
            category: Metadata category
            key: Metadata key
            
        Returns:
            Metadata value or None if not found
        """
        try:
            if not self.is_connected:
                return None
            
            session = self.session_maker()
            
            entry = session.query(MetadataEntry).filter_by(
                categoria=category, 
                clave=key
            ).first()
            
            session.close()
            
            return entry.valor if entry else None
            
        except Exception as e:
            logger.error(f"Error getting metadata {category}.{key}: {str(e)}")
            return None
    
    def get_all_metadata(self, category: str = None) -> Dict[str, str]:
        """
        Get all metadata entries, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            Dictionary of metadata key-value pairs
        """
        try:
            if not self.is_connected:
                return {}
            
            session = self.session_maker()
            
            if category:
                entries = session.query(MetadataEntry).filter_by(categoria=category).all()
            else:
                entries = session.query(MetadataEntry).all()
            
            session.close()
            
            metadata = {}
            for entry in entries:
                metadata[f"{entry.categoria}.{entry.clave}"] = entry.valor
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error getting metadata: {str(e)}")
            return {}
    
    def check_table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table exists, False otherwise
        """
        try:
            if not self.is_connected:
                return False
            
            with self.engine.connect() as conn:
                result = conn.execute(sqlalchemy.text(
                    "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = :table_name"
                ), {'table_name': table_name})
                
                count = result.scalar()
                return count > 0
                
        except Exception as e:
            logger.error(f"Error checking if table {table_name} exists: {str(e)}")
            return False
    
    def get_table_info(self, table_name: str) -> Optional[Dict]:
        """
        Get information about a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with table information or None if error
        """
        try:
            if not self.is_connected:
                return None
            
            with self.engine.connect() as conn:
                # Get column information
                result = conn.execute(sqlalchemy.text("""
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = :table_name
                    ORDER BY ORDINAL_POSITION
                """), {'table_name': table_name})
                
                columns = []
                for row in result.fetchall():
                    columns.append({
                        'name': row[0],
                        'type': row[1],
                        'nullable': row[2] == 'YES',
                        'default': row[3]
                    })
                
                # Get row count
                result = conn.execute(sqlalchemy.text(
                    "SELECT COUNT(*) FROM " + table_name
                ))
                row_count = result.scalar()
                
                return {
                    'table_name': table_name,
                    'columns': columns,
                    'row_count': row_count
                }
                
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {str(e)}")
            return None
    
    def guardar_rankings(self, rankings: Dict[str, pd.DataFrame]) -> bool:
        """
        Guarda los rankings de unidades HDD en la tabla nv_hdd_analisis_datos_v2.
        
        Args:
            rankings: Diccionario con rankings generados
            
        Returns:
            True si se guardaron exitosamente, False en caso contrario
        """
        try:
            if not self.is_connected:
                logger.error("No hay conexión a la base de datos")
                return False
            
            if not rankings:
                logger.warning("No hay rankings para guardar")
                return False
            
            # Limpiar datos anteriores de la tabla de rankings
            with self.engine.connect() as conn:
                conn.execute(sqlalchemy.text("DELETE FROM nv_hdd_analisis_datos_v2"))
                conn.commit()
                logger.info("Datos anteriores eliminados de nv_hdd_analisis_datos_v2")
            
            # Preparar datos para guardar
            datos_para_guardar = []
            fecha_analisis = datetime.datetime.now()
            
            for tipo_ranking, df in rankings.items():
                if df.empty:
                    logger.warning(f"Ranking {tipo_ranking} está vacío, se omite")
                    continue
                
                for _, row in df.iterrows():
                    # Mapear columnas del DataFrame a la tabla
                    datos_para_guardar.append({
                        'fecha_analisis': fecha_analisis,
                        'equipo': row['equipo'],
                        'unidad': row['unidad'],
                        'tipo_ranking': row['metrica'],  # Mapear 'metrica' a 'tipo_ranking'
                        'posicion': row['posicion'],
                        'valor_metrico': float(row['valor_metrico']) if pd.notna(row['valor_metrico']) else 0.0,
                        'total_equipos': len(df),  # Total de equipos en este ranking
                        'detalles_uso': f"Últimos 7 valores: {row.get('valor_1', 'N/A')}, {row.get('valor_2', 'N/A')}, {row.get('valor_3', 'N/A')}, {row.get('valor_4', 'N/A')}, {row.get('valor_5', 'N/A')}, {row.get('valor_6', 'N/A')}, {row.get('valor_7', 'N/A')}",
                        'fecha_creacion': datetime.datetime.now()
                    })
            
            if not datos_para_guardar:
                logger.warning("No hay datos válidos para guardar")
                return False
            
            # Crear DataFrame y guardar
            df_rankings = pd.DataFrame(datos_para_guardar)
            df_rankings.to_sql('nv_hdd_analisis_datos_v2', con=self.engine, 
                              if_exists='append', index=False)
            
            logger.info(f"Rankings guardados exitosamente: {len(df_rankings)} registros")
            
            # Guardar metadata
            self.set_metadata('rankings', 'ultima_generacion', 
                             datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             'Última generación de rankings HDD')
            self.set_metadata('rankings', 'total_registros', str(len(df_rankings)),
                             'Total de registros de ranking guardados')
            
            return True
            
        except Exception as e:
            logger.error(f"Error guardando rankings: {str(e)}")
            return False
    
    def obtener_rankings(self, tipo_ranking: str = None, fecha_analisis: str = None) -> pd.DataFrame:
        """
        Obtiene rankings de la tabla nv_hdd_analisis_datos_v2.
        
        Args:
            tipo_ranking: Tipo de ranking específico (opcional)
            fecha_analisis: Fecha de análisis específica (opcional)
            
        Returns:
            DataFrame con los rankings solicitados
        """
        try:
            if not self.is_connected:
                logger.error("No hay conexión a la base de datos")
                return pd.DataFrame()
            
            # Construir consulta
            query = "SELECT * FROM nv_hdd_analisis_datos_v2 WHERE 1=1"
            params = {}
            
            if tipo_ranking:
                query += " AND tipo_ranking = :tipo_ranking"
                params['tipo_ranking'] = tipo_ranking
            
            if fecha_analisis:
                query += " AND CAST(fecha_analisis AS DATE) = :fecha_analisis"
                params['fecha_analisis'] = fecha_analisis
            
            query += " ORDER BY tipo_ranking, posicion"
            
            # Ejecutar consulta
            with self.engine.connect() as conn:
                result = conn.execute(sqlalchemy.text(query), params)
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            logger.info(f"Rankings obtenidos: {len(df)} registros")
            return df
            
        except Exception as e:
            logger.error(f"Error obteniendo rankings: {str(e)}")
            return pd.DataFrame()
    
    def close(self):
        """Close the database manager."""
        if self.session_maker:
            # Close any open sessions
            pass


# Global database manager instance
_db_manager = None

def get_db_manager(engine=None):
    """Get the global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(engine)
        _db_manager.initialize()
    return _db_manager 