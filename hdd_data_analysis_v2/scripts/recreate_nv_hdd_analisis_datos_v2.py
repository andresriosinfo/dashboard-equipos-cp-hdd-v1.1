#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para recrear la tabla nv_hdd_analisis_datos_v2 con la estructura simplificada.
"""

import sys
import os
import sqlalchemy
from sqlalchemy import create_engine, text

# Añadir el directorio src al sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)
sys.path.insert(0, project_root)

# Importar configuración de la base de datos
try:
    from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
except ImportError as e:
    print(f"Error importando configuración: {e}")
    sys.exit(1)

connection_str = f'mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes'
engine = create_engine(connection_str)

sql = '''
IF OBJECT_ID('dbo.nv_hdd_analisis_datos_v2', 'U') IS NOT NULL
    DROP TABLE dbo.nv_hdd_analisis_datos_v2;

CREATE TABLE dbo.nv_hdd_analisis_datos_v2 (
    id INT IDENTITY(1,1) PRIMARY KEY,
    fecha_analisis DATETIME,
    equipo VARCHAR(50),
    unidad VARCHAR(50),
    tipo_ranking VARCHAR(20),
    posicion INT,
    valor_metrico FLOAT,
    total_equipos INT,
    detalles_uso TEXT,
    fecha_creacion DATETIME DEFAULT GETDATE()
);
'''

with engine.connect() as conn:
    print("Ejecutando script para recrear la tabla nv_hdd_analisis_datos_v2...")
    conn.execute(text(sql))
    conn.commit()
    print("Tabla nv_hdd_analisis_datos_v2 recreada correctamente con estructura simplificada.") 