#!/usr/bin/env python
# coding: utf-8

"""
Configuration settings for the CP Data Analysis application.
Edit this file to change database connection settings, schedule time, etc.
"""

# Database connection settings
DB_HOST = '10.147.17.185'
DB_PORT = '1433'
DB_NAME = 'cmpc_20240925_093000'
DB_USER = 'otms'
DB_PASSWORD = 'Password1'
#DB_HOST = '10.121.192.93'
#DB_PORT = '1433'
#DB_NAME = 'CMPC_SF'
#DB_USER = 'cmpc_dev'
#DB_PASSWORD = 'CmPcD3v.2023'

# Schedule settings
SCHEDULE_HOUR = '02:00'  # 24-hour format (HH:MM)

# Logging settings
LOG_LEVEL = 'DEBUG'  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL