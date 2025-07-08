#!/usr/bin/env python
# coding: utf-8

import os
import sys
import uuid
import json
import time
import logging
import datetime
import traceback
from typing import Optional, Dict, Any, List, Union

from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, func, desc, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError

# Import config manager
from cp_config_manager import get_config, get_config_manager

# SQLAlchemy Base
Base = declarative_base()

class LogEntry(Base):
    """Model for log entries stored in the database."""
    __tablename__ = 'an_logs'
    
    id_log = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.datetime.now, index=True)
    nivel = Column(String(10), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    componente = Column(String(100), nullable=False, index=True)
    id_ejecucion = Column(String(36), nullable=False, index=True)
    mensaje = Column(Text, nullable=False)
    detalles = Column(Text)
    
    def __repr__(self):
        return f"<LogEntry(id={self.id_log}, level='{self.nivel}', component='{self.componente}')>"

class PerformanceLog(Base):
    """Model for performance log entries."""
    __tablename__ = 'an_performance_logs'
    
    id_performance = Column(Integer, primary_key=True, autoincrement=True)
    id_ejecucion = Column(String(36), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.now, index=True)
    tipo_operacion = Column(String(50), nullable=False, index=True)  # e.g., 'db_query', 'analysis', 'batch_processing'
    nombre_operacion = Column(String(100), nullable=False)  # e.g., 'encontrar_maximo_por_equipo', 'sql_insert', etc.
    duracion_ms = Column(Integer, nullable=False)  # Duration in milliseconds
    recursos = Column(Text)  # JSON with resource usage (memory, CPU, etc.)
    metadatos = Column(Text)  # JSON with additional metadata
    
    def __repr__(self):
        return f"<PerformanceLog(id={self.id_performance}, operation='{self.nombre_operacion}', duration={self.duracion_ms}ms)>"

class DatabaseHandler(logging.Handler):
    """
    Logging handler that writes log records to a database.
    Implements a fallback to file logging if the database is unavailable.
    """
    
    def __init__(self, engine=None, level=logging.NOTSET):
        """
        Initialize the database handler.
        
        Args:
            engine: SQLAlchemy engine (optional, will be created from config if not provided)
            level: Minimum log level to process
        """
        super().__init__(level)
        self.engine = engine
        self.session = None
        self.is_connected = False
        self.id_ejecucion = str(uuid.uuid4())
        self.fallback_file = None
        self.fallback_handler = None
        self.pending_logs = []
        self.retry_count = 0
        self.max_retries = 3
        
        # Initialize fallback handler
        self._setup_fallback_handler()
        
        # Try to connect to the database
        self._connect_to_db()
    
    def _setup_fallback_handler(self):
        """Set up a file handler for fallback logging."""
        try:
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            self.fallback_file = os.path.join(log_dir, f'db_fallback_{datetime.datetime.now().strftime("%Y%m%d")}.log')
            self.fallback_handler = logging.FileHandler(self.fallback_file)
            self.fallback_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(name)s - [%(id_ejecucion)s] - %(message)s'
            ))
        except Exception as e:
            # Use sys.stderr as absolute fallback
            sys.stderr.write(f"Failed to create fallback log file: {str(e)}\n")
            self.fallback_handler = logging.StreamHandler(sys.stderr)
    
    def _connect_to_db(self):
        """Connect to the database and create tables if needed."""
        try:
            if not self.engine:
                # Import settings from config.py
                from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
                
                connection_str = f'mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes'
                self.engine = create_engine(connection_str, connect_args={'timeout': 30})
            
            # Test the connection
            with self.engine.connect() as conn:
                self.is_connected = True
                sys.stderr.write("Database connection established successfully for logging\n")
            
            # Create session for database operations
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
            # Create tables if they don't exist
            self._create_log_tables_if_not_exist()
            
            # Process any pending logs
            self._process_pending_logs()
            
        except Exception as e:
            self.is_connected = False
            self.engine = None
            sys.stderr.write(f"Failed to connect to database for logging: {str(e)}\n")
            sys.stderr.write("Falling back to file-based logging\n")
    
    def _create_log_tables_if_not_exist(self):
        """Create log tables if they don't exist."""
        try:
            # Create tables
            Base.metadata.create_all(self.engine, tables=[
                LogEntry.__table__,
                PerformanceLog.__table__
            ])
            
            sys.stderr.write("Log tables created or verified successfully\n")
            
        except Exception as e:
            sys.stderr.write(f"Error creating log tables: {str(e)}\n")
            self.is_connected = False
            self.engine = None
    
    def _process_pending_logs(self):
        """Process any pending logs in the queue."""
        if not self.pending_logs:
            return
        
        if not self.is_connected or not self.session:
            return
        
        try:
            sys.stderr.write(f"Processing {len(self.pending_logs)} pending log entries\n")
            
            for record in self.pending_logs:
                try:
                    self._write_to_db(record)
                except Exception as e:
                    sys.stderr.write(f"Error processing pending log: {str(e)}\n")
            
            # Clear pending logs if successful
            self.pending_logs = []
            
        except Exception as e:
            sys.stderr.write(f"Error processing pending logs: {str(e)}\n")
    
    def _write_to_db(self, record):
        """Write a log record to the database."""
        if not self.is_connected or not self.session:
            raise ValueError("Database not connected")
        
        try:
            # Extract record information
            log_entry = LogEntry(
                timestamp=datetime.datetime.fromtimestamp(record.created),
                nivel=record.levelname,
                componente=record.name,
                id_ejecucion=getattr(record, 'id_ejecucion', self.id_ejecucion),
                mensaje=record.getMessage(),
                detalles=self._get_details(record)
            )
            
            self.session.add(log_entry)
            self.session.commit()
            
        except Exception as e:
            self.session.rollback()
            raise
    
    def _write_to_fallback(self, record):
        """Write a log record to the fallback file."""
        if self.fallback_handler:
            # Add id_ejecucion to the record
            record.__dict__['id_ejecucion'] = getattr(record, 'id_ejecucion', self.id_ejecucion)
            self.fallback_handler.emit(record)
    
    def _get_details(self, record):
        """Extract detailed information from a log record."""
        details = {}
        
        # Add traceback if available
        if record.exc_info:
            details['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': ''.join(traceback.format_exception(*record.exc_info))
            }
        
        # Add extra attributes
        for key, value in record.__dict__.items():
            if key.startswith('_') or key in ('args', 'asctime', 'created', 'exc_info', 'exc_text', 
                                             'filename', 'funcName', 'id_ejecucion', 'levelname', 'levelno', 
                                             'lineno', 'module', 'msecs', 'message', 'msg', 'name', 
                                             'pathname', 'process', 'processName', 'relativeCreated', 
                                             'stack_info', 'thread', 'threadName'):
                continue
            
            try:
                # Try to serialize the value as JSON
                json.dumps({key: value})
                details[key] = value
            except (TypeError, OverflowError):
                # If it can't be serialized, convert to string
                details[key] = str(value)
        
        # If no details, return None
        if not details:
            return None
        
        # Otherwise, return JSON string
        return json.dumps(details)
    
    def emit(self, record):
        """Emit a log record to the database or fallback file."""
        # Always write to fallback first (belt and suspenders approach)
        self._write_to_fallback(record)
        
        # Try to write to database
        if self.is_connected and self.session:
            try:
                self._write_to_db(record)
                # Reset retry count on success
                self.retry_count = 0
                return
            except Exception as e:
                self.retry_count += 1
                sys.stderr.write(f"Error writing to log database (attempt {self.retry_count}): {str(e)}\n")
                
                # If max retries reached, reconnect and try again
                if self.retry_count >= self.max_retries:
                    sys.stderr.write("Max retries reached, attempting to reconnect to database\n")
                    self.is_connected = False
                    self.session.close()
                    self.session = None
                    self._connect_to_db()
                    self.retry_count = 0
        
        # If we reach here, either we're not connected or the write failed
        # Add record to pending logs for later processing
        self.pending_logs.append(record)
    
    def close(self):
        """Close the handler and clean up resources."""
        if self.session:
            self.session.close()
        
        if self.fallback_handler:
            self.fallback_handler.close()
        
        super().close()


class LogManager:
    """
    Manager for application logging operations.
    
    This class provides functionality to:
    1. Set up database and file logging
    2. Clean up old log records
    3. Archive logs
    4. Record performance metrics
    """
    
    def __init__(self, engine=None):
        """
        Initialize the log manager.
        
        Args:
            engine: SQLAlchemy engine (optional, will be created from config if not provided)
        """
        self.engine = engine
        self.session = None
        self.is_connected = False
        self.id_ejecucion = str(uuid.uuid4())
        self.db_handler = None
        self.handlers = []
        
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
                print("Database connection established successfully for log manager")
            
            # Create session for database operations
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
        except Exception as e:
            self.is_connected = False
            self.engine = None
            print(f"Failed to connect to database for log manager: {str(e)}")
    
    def setup_logging(self, level=None, console=True, file=True, db=True, 
                      log_dir=None, log_file=None, log_formatter=None):
        """
        Set up logging with various handlers.
        
        Args:
            level: Logging level (default: from config or INFO)
            console: Whether to log to console (default: True)
            file: Whether to log to file (default: True)
            db: Whether to log to database (default: True)
            log_dir: Directory for log files (default: ./logs)
            log_file: Log file name (default: cp_data_analysis_YYYYMMDD.log)
            log_formatter: Custom formatter (default: standard format)
        
        Returns:
            Root logger configured with handlers
        """
        # Get logging level from config or use default
        if level is None:
            level_name = get_config('nivel_log', 'INFO')
            level = getattr(logging, level_name.upper(), logging.INFO)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        # Remove existing handlers
        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)
        
        # Set up formatter
        if log_formatter is None:
            log_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
            )
        
        # Add console handler
        if console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_formatter)
            root_logger.addHandler(console_handler)
            self.handlers.append(console_handler)
        
        # Add file handler
        if file:
            # Set up log directory
            if log_dir is None:
                log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            # Set up log file
            if log_file is None:
                log_file = f'cp_data_analysis_{datetime.datetime.now().strftime("%Y%m%d")}.log'
            log_path = os.path.join(log_dir, log_file)
            
            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(log_formatter)
            root_logger.addHandler(file_handler)
            self.handlers.append(file_handler)
        
        # Add database handler
        if db:
            self.db_handler = DatabaseHandler(self.engine, level)
            self.db_handler.id_ejecucion = self.id_ejecucion
            root_logger.addHandler(self.db_handler)
            self.handlers.append(self.db_handler)
        
        # Log startup message
        logger = logging.getLogger('cp_data_analysis')
        logger.info(f"Logging initialized with execution ID: {self.id_ejecucion}")
        logger.debug(f"Log level: {logging.getLevelName(level)}")
        
        return root_logger
    
    def get_execution_id(self):
        """Get the current execution ID."""
        return self.id_ejecucion
    
    def set_execution_id(self, id_ejecucion):
        """
        Set the execution ID for this log manager.
        
        Args:
            id_ejecucion: New execution ID
        """
        self.id_ejecucion = id_ejecucion
        if self.db_handler:
            self.db_handler.id_ejecucion = id_ejecucion
    
    def log_performance(self, tipo_operacion, nombre_operacion, duracion_ms, recursos=None, metadatos=None):
        """
        Log performance metrics.
        
        Args:
            tipo_operacion: Type of operation (e.g., 'db_query', 'analysis', 'batch_processing')
            nombre_operacion: Name of the operation
            duracion_ms: Duration in milliseconds
            recursos: Resource usage (optional, as dictionary)
            metadatos: Additional metadata (optional, as dictionary)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected or not self.session:
            logger = logging.getLogger('cp_data_analysis')
            logger.warning(f"Cannot log performance metrics to database: not connected")
            
            # Log to regular logger instead
            logger.info(f"Performance: {tipo_operacion} - {nombre_operacion} - {duracion_ms}ms")
            return False
        
        try:
            # Convert resources and metadata to JSON strings
            recursos_json = json.dumps(recursos) if recursos else None
            metadatos_json = json.dumps(metadatos) if metadatos else None
            
            # Create performance log entry
            perf_log = PerformanceLog(
                id_ejecucion=self.id_ejecucion,
                tipo_operacion=tipo_operacion,
                nombre_operacion=nombre_operacion,
                duracion_ms=duracion_ms,
                recursos=recursos_json,
                metadatos=metadatos_json
            )
            
            self.session.add(perf_log)
            self.session.commit()
            
            logger = logging.getLogger('cp_data_analysis')
            logger.debug(f"Performance logged: {tipo_operacion} - {nombre_operacion} - {duracion_ms}ms")
            
            return True
            
        except Exception as e:
            self.session.rollback()
            logger = logging.getLogger('cp_data_analysis')
            logger.error(f"Error logging performance metrics: {str(e)}")
            return False
    
    def clean_old_logs(self, days=None):
        """
        Delete old log records.
        
        Args:
            days: Number of days to keep (default: from config or 30)
        
        Returns:
            Number of records deleted
        """
        if not self.is_connected or not self.session:
            logger = logging.getLogger('cp_data_analysis')
            logger.warning("Cannot clean old logs: not connected to database")
            return 0
        
        try:
            # Get retention days from config or use default
            if days is None:
                days = get_config('dias_retencion_logs', 30)
            
            # Calculate cutoff date
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
            
            # Delete old log entries
            log_count = self.session.query(LogEntry).filter(
                LogEntry.timestamp < cutoff_date
            ).count()
            
            self.session.query(LogEntry).filter(
                LogEntry.timestamp < cutoff_date
            ).delete()
            
            # Delete old performance logs
            perf_count = self.session.query(PerformanceLog).filter(
                PerformanceLog.timestamp < cutoff_date
            ).count()
            
            self.session.query(PerformanceLog).filter(
                PerformanceLog.timestamp < cutoff_date
            ).delete()
            
            self.session.commit()
            
            logger = logging.getLogger('cp_data_analysis')
            logger.info(f"Cleaned {log_count} log entries and {perf_count} performance logs older than {days} days")
            
            return log_count + perf_count
            
        except Exception as e:
            self.session.rollback()
            logger = logging.getLogger('cp_data_analysis')
            logger.error(f"Error cleaning old logs: {str(e)}")
            return 0
    
    def archive_logs(self, days=None, archive_dir=None):
        """
        Archive old log records to files.
        
        Args:
            days: Number of days to archive (default: from config or 90)
            archive_dir: Directory for archive files (default: ./logs/archive)
        
        Returns:
            Number of records archived
        """
        if not self.is_connected or not self.session:
            logger = logging.getLogger('cp_data_analysis')
            logger.warning("Cannot archive logs: not connected to database")
            return 0
        
        try:
            # Get archive days from config or use default
            if days is None:
                days = get_config('dias_archivo_logs', 90)
            
            # Set up archive directory
            if archive_dir is None:
                log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
                archive_dir = os.path.join(log_dir, 'archive')
            os.makedirs(archive_dir, exist_ok=True)
            
            # Calculate cutoff date
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
            
            # Fetch old log entries
            old_logs = self.session.query(LogEntry).filter(
                LogEntry.timestamp < cutoff_date
            ).all()
            
            if not old_logs:
                logger = logging.getLogger('cp_data_analysis')
                logger.info(f"No logs found to archive older than {days} days")
                return 0
            
            # Group by month for archive files
            logs_by_month = {}
            for log in old_logs:
                month_key = log.timestamp.strftime('%Y-%m')
                if month_key not in logs_by_month:
                    logs_by_month[month_key] = []
                logs_by_month[month_key].append(log)
            
            # Archive logs by month
            total_archived = 0
            for month_key, logs in logs_by_month.items():
                # Create archive file
                archive_file = os.path.join(archive_dir, f'logs_{month_key}.json')
                
                # Convert logs to serializable format
                log_data = []
                for log in logs:
                    log_dict = {
                        'id_log': log.id_log,
                        'timestamp': log.timestamp.isoformat(),
                        'nivel': log.nivel,
                        'componente': log.componente,
                        'id_ejecucion': log.id_ejecucion,
                        'mensaje': log.mensaje,
                        'detalles': log.detalles
                    }
                    log_data.append(log_dict)
                
                # Write to file
                with open(archive_file, 'w') as f:
                    json.dump(log_data, f, indent=2)
                
                total_archived += len(logs)
            
            # Delete archived logs
            self.session.query(LogEntry).filter(
                LogEntry.timestamp < cutoff_date
            ).delete()
            
            self.session.commit()
            
            logger = logging.getLogger('cp_data_analysis')
            logger.info(f"Archived {total_archived} log entries older than {days} days to {archive_dir}")
            
            return total_archived
            
        except Exception as e:
            self.session.rollback()
            logger = logging.getLogger('cp_data_analysis')
            logger.error(f"Error archiving logs: {str(e)}")
            return 0
    
    def get_logs(self, level=None, component=None, id_ejecucion=None, start_date=None, 
                end_date=None, limit=100, offset=0):
        """
        Get log entries from the database.
        
        Args:
            level: Filter by log level (optional)
            component: Filter by component name (optional)
            id_ejecucion: Filter by execution ID (optional)
            start_date: Filter by start date (optional)
            end_date: Filter by end date (optional)
            limit: Maximum number of records to return (default: 100)
            offset: Offset for pagination (default: 0)
        
        Returns:
            List of log entries as dictionaries
        """
        if not self.is_connected or not self.session:
            logger = logging.getLogger('cp_data_analysis')
            logger.warning("Cannot get logs: not connected to database")
            return []
        
        try:
            # Build query
            query = self.session.query(LogEntry)
            
            # Apply filters
            if level:
                query = query.filter(LogEntry.nivel == level)
            
            if component:
                query = query.filter(LogEntry.componente == component)
            
            if id_ejecucion:
                query = query.filter(LogEntry.id_ejecucion == id_ejecucion)
            
            if start_date:
                query = query.filter(LogEntry.timestamp >= start_date)
            
            if end_date:
                query = query.filter(LogEntry.timestamp <= end_date)
            
            # Apply limit and offset
            query = query.order_by(desc(LogEntry.timestamp)).limit(limit).offset(offset)
            
            # Execute query
            logs = query.all()
            
            # Convert logs to dictionaries
            result = []
            for log in logs:
                log_dict = {
                    'id_log': log.id_log,
                    'timestamp': log.timestamp.isoformat(),
                    'nivel': log.nivel,
                    'componente': log.componente,
                    'id_ejecucion': log.id_ejecucion,
                    'mensaje': log.mensaje,
                    'detalles': json.loads(log.detalles) if log.detalles else None
                }
                result.append(log_dict)
            
            return result
            
        except Exception as e:
            logger = logging.getLogger('cp_data_analysis')
            logger.error(f"Error getting logs: {str(e)}")
            return []
    
    def get_performance_logs(self, tipo_operacion=None, nombre_operacion=None, id_ejecucion=None, 
                           start_date=None, end_date=None, limit=100, offset=0):
        """
        Get performance log entries from the database.
        
        Args:
            tipo_operacion: Filter by operation type (optional)
            nombre_operacion: Filter by operation name (optional)
            id_ejecucion: Filter by execution ID (optional)
            start_date: Filter by start date (optional)
            end_date: Filter by end date (optional)
            limit: Maximum number of records to return (default: 100)
            offset: Offset for pagination (default: 0)
        
        Returns:
            List of performance log entries as dictionaries
        """
        if not self.is_connected or not self.session:
            logger = logging.getLogger('cp_data_analysis')
            logger.warning("Cannot get performance logs: not connected to database")
            return []
        
        try:
            # Build query
            query = self.session.query(PerformanceLog)
            
            # Apply filters
            if tipo_operacion:
                query = query.filter(PerformanceLog.tipo_operacion == tipo_operacion)
            
            if nombre_operacion:
                query = query.filter(PerformanceLog.nombre_operacion == nombre_operacion)
            
            if id_ejecucion:
                query = query.filter(PerformanceLog.id_ejecucion == id_ejecucion)
            
            if start_date:
                query = query.filter(PerformanceLog.timestamp >= start_date)
            
            if end_date:
                query = query.filter(PerformanceLog.timestamp <= end_date)
            
            # Apply limit and offset
            query = query.order_by(desc(PerformanceLog.timestamp)).limit(limit).offset(offset)
            
            # Execute query
            logs = query.all()
            
            # Convert logs to dictionaries
            result = []
            for log in logs:
                log_dict = {
                    'id_performance': log.id_performance,
                    'id_ejecucion': log.id_ejecucion,
                    'timestamp': log.timestamp.isoformat(),
                    'tipo_operacion': log.tipo_operacion,
                    'nombre_operacion': log.nombre_operacion,
                    'duracion_ms': log.duracion_ms,
                    'recursos': json.loads(log.recursos) if log.recursos else None,
                    'metadatos': json.loads(log.metadatos) if log.metadatos else None
                }
                result.append(log_dict)
            
            return result
            
        except Exception as e:
            logger = logging.getLogger('cp_data_analysis')
            logger.error(f"Error getting performance logs: {str(e)}")
            return []
    
    def close(self):
        """Close connections and handlers."""
        if self.session:
            self.session.close()
        
        for handler in self.handlers:
            handler.close()


# Performance timing decorator
def time_execution(tipo_operacion):
    """
    Decorator to time the execution of a function and log performance metrics.
    
    Args:
        tipo_operacion: Type of operation (e.g., 'db_query', 'analysis', 'batch_processing')
    
    Returns:
        Decorated function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get log manager
            log_manager = kwargs.pop('log_manager', None)
            if log_manager is None:
                log_manager = get_log_manager()
            
            # Start timing
            start_time = time.time()
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Calculate duration
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Log performance
                metadata = {
                    'function': func.__name__,
                    'args': str(args),
                    'kwargs': str(kwargs)
                }
                
                log_manager.log_performance(
                    tipo_operacion=tipo_operacion,
                    nombre_operacion=func.__name__,
                    duracion_ms=duration_ms,
                    metadatos=metadata
                )
                
                return result
                
            except Exception as e:
                # Calculate duration even if there's an error
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Log performance with error information
                metadata = {
                    'function': func.__name__,
                    'args': str(args),
                    'kwargs': str(kwargs),
                    'error': str(e),
                    'error_type': type(e).__name__
                }
                
                log_manager.log_performance(
                    tipo_operacion=tipo_operacion,
                    nombre_operacion=func.__name__,
                    duracion_ms=duration_ms,
                    metadatos=metadata
                )
                
                # Re-raise the exception
                raise
                
        return wrapper
    return decorator


# Create a singleton instance
log_manager = None

def get_log_manager(engine=None):
    """
    Get the log manager singleton instance.
    
    Args:
        engine: SQLAlchemy engine (optional)
    
    Returns:
        LogManager instance
    """
    global log_manager
    if log_manager is None:
        log_manager = LogManager(engine)
    return log_manager

def setup_logging(level=None, console=True, file=True, db=True):
    """
    Set up logging with the log manager.
    
    Args:
        level: Logging level (default: from config or INFO)
        console: Whether to log to console (default: True)
        file: Whether to log to file (default: True)
        db: Whether to log to database (default: True)
    
    Returns:
        Root logger configured with handlers
    """
    manager = get_log_manager()
    return manager.setup_logging(level, console, file, db)

def get_execution_id():
    """Get the current execution ID."""
    manager = get_log_manager()
    return manager.get_execution_id()

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Set up logging with database handler
    manager = get_log_manager()
    logger = manager.setup_logging()
    
    # Test logging
    logger.info("This is a test log message")
    logger.error("This is an error message", exc_info=True)
    
    # Test performance logging
    manager.log_performance(
        tipo_operacion='test',
        nombre_operacion='example_operation',
        duracion_ms=1000,
        recursos={'memory': '100MB', 'cpu': '10%'},
        metadatos={'test': True}
    )
    
    # Clean up
    manager.clean_old_logs()
    manager.close()