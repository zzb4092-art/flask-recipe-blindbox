"""Application configuration."""
import os
from urllib.parse import quote_plus


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    _DB_USER = os.environ.get('DB_USER', 'root')
    _DB_PASS = os.environ.get('DB_PASS', 'Zb147258@@')
    _DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
    _DB_PORT = os.environ.get('DB_PORT', '3306')
    _DB_NAME = os.environ.get('DB_NAME', 'recipe_blindbox_db')

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'mysql+pymysql://{_DB_USER}:{quote_plus(_DB_PASS)}@{_DB_HOST}:{_DB_PORT}/{_DB_NAME}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 3600,
        'echo': False,
    }


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        'echo': True,
    }


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
