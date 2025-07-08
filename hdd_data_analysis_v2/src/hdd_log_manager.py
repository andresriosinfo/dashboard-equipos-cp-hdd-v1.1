#!/usr/bin/env python
# coding: utf-8

import os
import logging
import datetime
import time
import uuid
import json
import sqlalchemy
from sqlalchemy import Column, String, Integer, DateTime, Text, MetaData, Table, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Dict, Any, Optional, Union
import functools

logger = logging.getLogger('hdd_data_analysis')
Base = declarative_base()

class LogEntry(Base):
    """Model for log entries stored in the database."""
    __tablename__ = 'hdd_an_logs'
    
    id_log = Column(String(50), primary_key=True)
    nivel = Column(String(20), nullable=False)
    mensaje = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    ejecucion_id = Column(String(50))
    modulo = Column(String(100))
    detalles = Column(Text)
    
    def __repr__(self):
        return f"<LogEntry(id='{self.id_log}', level='{self.nivel}', message='{self.mensaje[:50]}...')>"

class PerformanceLog(Base):
    """Model for performance logs stored in the database."""
    __tablename__ = 'hdd_an_performance_logs'
    
    id_performance = Column(String(50), primary_key=True)
    funcion = Column(String(100), nullable=False)
    tiempo_ejecucion = Column(Integer, nullable=False)  # in milliseconds
    timestamp = Column(DateTime, default=datetime.datetime.now)
    ejecucion_id = Column(String(50))
    parametros = Column(Text)
    resultado = Column(String(20))  # success, error, warning
    
    def __repr__(self):
        return f"<PerformanceLog(function='{self.funcion}', time='{self.tiempo_ejecucion}ms')>"

class DatabaseHandler(logging.Handler):
    """Custom logging handler that writes to database."""
    
    def __init__(self, session_maker, execution_id=None):
        super().__init__()
        self.session_maker = session_maker
        self.execution_id = execution_id or str(uuid.uuid4())
    
    def emit(self, record):
        try:
            session = self.session_maker()
            
            # Create log entry
            log_entry = LogEntry(
                id_log=str(uuid.uuid4()),
                nivel=record.levelname,
                mensaje=record.getMessage(),
                timestamp=datetime.datetime.fromtimestamp(record.created),
                ejecucion_id=self.execution_id,
                modulo=record.module,
                detalles=getattr(record, 'details', None)
            )
            
            session.add(log_entry)
            session.commit()
            session.close()
            
        except Exception as e:
            # Fallback to console if database logging fails
            print(f"Database logging failed: {str(e)}")
            print(f"Original log: {record.levelname} - {record.getMessage()}")

class LogManager:
    """
    Manages application logging with database and file support.
    
    This class provides functionality to:
    1. Setup logging to multiple targets (database, file, console)
    2. Track execution performance
    3. Manage log rotation and archiving
    4. Generate execution reports
    """
    
    def __init__(self, engine=None):
        """
        Initialize the log manager.
        
        Args:
            engine: SQLAlchemy engine (optional, will be created from config.py if not provided)
        """
        self.engine = engine
        self.session_maker = None
        self.is_connected = False
        self.current_execution_id = None
        self.loggers = {}
        
    def initialize(self):
        """
        Initialize the logging system.
        - Attempts to connect to the database
        - Creates logging tables if they don't exist
        - Sets up logging handlers
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
                logger.info("Database connection established successfully for HDD logging")
            
            # Create session maker
            self.session_maker = sessionmaker(bind=self.engine)
            
            # Create tables if they don't exist
            self._create_log_tables_if_not_exists()
            
        except Exception as e:
            logger.error(f"Failed to initialize database logging: {str(e)}")
            logger.info("Falling back to file-only logging")
            self.is_connected = False
    
    def _create_log_tables_if_not_exists(self):
        """Create the logging tables if they don't exist."""
        try:
            # Create the tables
            Base.metadata.create_all(self.engine, tables=[LogEntry.__table__, PerformanceLog.__table__])
            logger.info("HDD logging tables created or verified")
                
        except Exception as e:
            logger.error(f"Error creating HDD logging tables: {str(e)}")
            raise
    
    def setup_logging(self, console=True, file=True, db=False, level='INFO'):
        """
        Setup logging configuration.
        
        Args:
            console: Enable console logging
            file: Enable file logging
            db: Enable database logging (default: False to avoid DB logging)
            level: Logging level
            
        Returns:
            Configured logger
        """
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger('hdd_data_analysis')
        root_logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        if console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, level.upper()))
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # File handler
        if file:
            log_file = os.path.join(logs_dir, f'hdd_data_analysis_{datetime.datetime.now().strftime("%Y%m%d")}.log')
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(getattr(logging, level.upper()))
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        # Database handler (disabled by default)
        if db and self.is_connected:
            db_handler = DatabaseHandler(self.session_maker, self.current_execution_id)
            db_handler.setLevel(getattr(logging, level.upper()))
            root_logger.addHandler(db_handler)
        
        self.loggers['root'] = root_logger
        return root_logger
    
    def get_execution_id(self):
        """Generate a new execution ID."""
        self.current_execution_id = str(uuid.uuid4())
        return self.current_execution_id
    
    def log_performance(self, function_name, execution_time_ms, execution_id=None, parameters=None, result='success'):
        """
        Log performance metrics.
        
        Args:
            function_name: Name of the function
            execution_time_ms: Execution time in milliseconds
            execution_id: Execution ID (optional)
            parameters: Function parameters (optional)
            result: Result status (success, error, warning)
        """
        try:
            if not self.is_connected:
                return
            
            session = self.session_maker()
            
            # Create performance log entry
            perf_log = PerformanceLog(
                id_performance=str(uuid.uuid4()),
                funcion=function_name,
                tiempo_ejecucion=execution_time_ms,
                timestamp=datetime.datetime.now(),
                ejecucion_id=execution_id or self.current_execution_id,
                parametros=json.dumps(parameters) if parameters else None,
                resultado=result
            )
            
            session.add(perf_log)
            session.commit()
            session.close()
            
        except Exception as e:
            logger.error(f"Error logging performance: {str(e)}")
    
    def clean_old_logs(self, days_to_keep=30):
        """
        Clean old log entries from database.
        
        Args:
            days_to_keep: Number of days to keep logs
        """
        try:
            if not self.is_connected:
                return
            
            session = self.session_maker()
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
            
            # Delete old log entries
            deleted_logs = session.query(LogEntry).filter(LogEntry.timestamp < cutoff_date).delete()
            
            # Delete old performance logs
            deleted_perf = session.query(PerformanceLog).filter(PerformanceLog.timestamp < cutoff_date).delete()
            
            session.commit()
            session.close()
            
            logger.info(f"Cleaned {deleted_logs} log entries and {deleted_perf} performance logs older than {days_to_keep} days")
            
        except Exception as e:
            logger.error(f"Error cleaning old logs: {str(e)}")
    
    def get_execution_summary(self, execution_id):
        """
        Get summary of a specific execution.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Dictionary with execution summary
        """
        try:
            if not self.is_connected:
                return {}
            
            session = self.session_maker()
            
            # Get log entries
            logs = session.query(LogEntry).filter_by(ejecucion_id=execution_id).all()
            
            # Get performance logs
            perf_logs = session.query(PerformanceLog).filter_by(ejecucion_id=execution_id).all()
            
            session.close()
            
            # Calculate summary
            summary = {
                'execution_id': execution_id,
                'total_logs': len(logs),
                'total_performance_logs': len(perf_logs),
                'log_levels': {},
                'total_execution_time': sum(log.tiempo_ejecucion for log in perf_logs),
                'functions_called': [log.funcion for log in perf_logs],
                'result_summary': {}
            }
            
            # Count log levels
            for log in logs:
                level = log.nivel
                summary['log_levels'][level] = summary['log_levels'].get(level, 0) + 1
            
            # Count results
            for log in perf_logs:
                result = log.resultado
                summary['result_summary'][result] = summary['result_summary'].get(result, 0) + 1
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting execution summary: {str(e)}")
            return {}
    
    def close(self):
        """Close the log manager."""
        if self.session_maker:
            # Close any open sessions
            pass


# Global log manager instance
_log_manager = None

def get_log_manager(engine=None):
    """Get the global log manager instance."""
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager(engine)
        _log_manager.initialize()
    return _log_manager

def setup_logging(console=True, file=True, db=True, level='INFO'):
    """
    Setup logging configuration.
    
    Args:
        console: Enable console logging
        file: Enable file logging
        db: Enable database logging
        level: Logging level
        
    Returns:
        Configured logger
    """
    log_manager = get_log_manager()
    return log_manager.setup_logging(console, file, db, level)

def time_execution(function_name=None):
    """
    Decorator to time function execution and log performance.
    
    Args:
        function_name: Custom function name (optional)
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log_manager = get_log_manager()
            start_time = time.time()
            
            # Get function name
            func_name = function_name or func.__name__
            
            # Prepare parameters for logging
            params = {
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys()) if kwargs else []
            }
            
            try:
                result = func(*args, **kwargs)
                execution_time_ms = int((time.time() - start_time) * 1000)
                
                # Log performance
                log_manager.log_performance(
                    func_name, 
                    execution_time_ms, 
                    log_manager.current_execution_id,
                    params,
                    'success'
                )
                
                return result
                
            except Exception as e:
                execution_time_ms = int((time.time() - start_time) * 1000)
                
                # Log performance with error
                log_manager.log_performance(
                    func_name, 
                    execution_time_ms, 
                    log_manager.current_execution_id,
                    params,
                    'error'
                )
                
                raise
        
        return wrapper
    return decorator 