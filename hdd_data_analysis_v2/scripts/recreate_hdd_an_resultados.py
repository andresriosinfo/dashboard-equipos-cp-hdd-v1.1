#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para recrear la tabla hdd_an_resultados con la estructura correcta.
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

try:
    from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
except ImportError as e:
    print(f"Error importando configuración: {e}")
    sys.exit(1)

connection_str = f'mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes'
engine = create_engine(connection_str)

sql = '''
IF OBJECT_ID('dbo.hdd_an_resultados', 'U') IS NOT NULL
    DROP TABLE dbo.hdd_an_resultados;

CREATE TABLE dbo.hdd_an_resultados (
    id VARCHAR(50) PRIMARY KEY,
    unidad VARCHAR(100),
    equipo VARCHAR(100),
    fecha_ejecucion_del_codigo DATETIME,
    metrica VARCHAR(50),
    posicion INT,
    valor_metrico INT,
    valor_1 INT,
    valor_2 INT,
    valor_3 INT,
    valor_4 INT,
    valor_5 INT,
    valor_6 INT,
    valor_7 INT
);
'''

with engine.connect() as conn:
    print("Ejecutando script para recrear la tabla hdd_an_resultados...")
    conn.execute(text(sql))
    conn.commit()
    print("Tabla hdd_an_resultados recreada correctamente.") 