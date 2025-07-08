#!/usr/bin/env python
# coding: utf-8

"""
Configuration settings for the HDD Data Analysis application.
Edit this file to change database connection settings, schedule time, etc.
"""

# Database connection settings (same as original)
DB_HOST = '10.147.17.185'
DB_PORT = '1433'
DB_NAME = 'cmpc_20240925_093000'
DB_USER = 'otms'
DB_PASSWORD = 'Password1'

# Schedule settings
SCHEDULE_HOUR = '02:00'  # 24-hour format (HH:MM)

# Logging settings
LOG_LEVEL = 'DEBUG'  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL 