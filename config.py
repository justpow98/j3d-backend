import os
from datetime import timedelta


def _normalize_db_url(url: str | None) -> str | None:
    """Ensure SQLAlchemy friendly Postgres scheme"""
    if url and url.startswith('postgres://'):
        return url.replace('postgres://', 'postgresql://', 1)
    return url


class Config:
    """Base configuration"""
    SQLALCHEMY_DATABASE_URI = _normalize_db_url(os.getenv('DATABASE_URL', 'sqlite:///j3d.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    AUTO_DB_CREATE = True  # dev/test convenience; disabled in production
    
    # Etsy API Configuration
    ETSY_CLIENT_ID = os.getenv('ETSY_CLIENT_ID')
    ETSY_CLIENT_SECRET = os.getenv('ETSY_CLIENT_SECRET')
    ETSY_REDIRECT_URI = os.getenv('ETSY_REDIRECT_URI', 'http://localhost:4200/oauth-callback')
    ETSY_API_BASE_URL = 'https://openapi.etsy.com/v3'
    
    # CORS Configuration
    CORS_ORIGINS = ['http://localhost:4200', 'http://localhost:3000']
    
    # HTTP client configuration
    HTTP_TIMEOUT = float(os.getenv('HTTP_TIMEOUT', '10'))
    
    # JWT Configuration
    JWT_EXPIRATION_HOURS = 24

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = _normalize_db_url(
        os.getenv('DATABASE_URL', 'postgresql://localhost/j3d')
    )
    AUTO_DB_CREATE = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///j3d_test.db'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
