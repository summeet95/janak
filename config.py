import os
import sys
from datetime import timedelta


def app_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.getenv('LOCALAPPDATA', os.path.dirname(sys.executable)), 'InventoryApp')
    return os.path.dirname(__file__)


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')
    SQLITE_PATH = os.getenv('SQLITE_PATH', os.path.join(app_base_dir(), 'instance', 'inventory_app.sqlite'))
    JWT_SECRET = os.getenv('JWT_SECRET', 'jwt-secret-key-change-this')
    JWT_EXPIRATION = timedelta(hours=24)
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLITE_PATH = os.getenv('SQLITE_TEST_PATH', os.path.join(app_base_dir(), 'instance', 'inventory_app_test.sqlite'))

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
