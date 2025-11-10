"""
Archivo de configuración para el Sistema de Gestión de Notas
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
# 1) Si existe .env en el directorio actual, usarlo.
# 2) En ejecutable one-file, usar el directorio de extracción (_MEIPASS) si existe.
cwd_env = os.path.join(os.getcwd(), '.env')
if os.path.exists(cwd_env):
    load_dotenv(cwd_env)
else:
    base_dir = getattr(sys, '_MEIPASS', None)
    if base_dir:
        load_dotenv(os.path.join(base_dir, '.env'))
    else:
        # Fallback a búsqueda estándar si no hay archivo específico
        load_dotenv()

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu_clave_secreta_muy_segura_aqui'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de base de datos
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or ''
    DB_NAME = os.environ.get('DB_NAME') or 'sistema_academico'
    
    # URI de conexión a la base de datos
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SQLALCHEMY_ECHO = False

class TestingConfig(Config):
    """Configuración para pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
