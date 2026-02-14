# config.py
"""
Configuration module for Expense Tracker System
Version: 1.0.0
"""
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB = os.getenv('MONGO_DB', 'expense_tracker')
    
    # Application Settings
    APP_NAME = "Expense Tracker System"
    APP_VERSION = "1.0.0"
    COMPANY_NAME = "ExpenseTracker"
    COMPANY_YEAR = "2026"
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # Export Settings
    EXPORT_FORMATS = ['csv', 'json', 'excel']
    
    # Cache Settings
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Date Format
    DATE_FORMAT = '%Y-%m-%d'
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # Currency
    DEFAULT_CURRENCY = 'INR'
    SUPPORTED_CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'INR']

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Add production-specific settings here

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    MONGO_DB = 'expense_tracker_test'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}