"""
Flask application factory for Expense Tracker System
Version: 1.0.0
"""
from flask import Flask, render_template, request
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# Initialize extensions - WITHOUT app
mongo = PyMongo()
cache = Cache()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

def create_app(config_name=None):
    """Application factory"""
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    from config import config
    app.config.from_object(config[config_name])
    
    # CRITICAL FIX: Set MongoDB URI explicitly
    # app.config["MONGO_URI"] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/') + os.getenv('MONGO_DB', 'expense_tracker')
    base_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')

    # Remove trailing slash if present, and also remove any existing database path or query params
    base_uri = base_uri.split('/?')[0].rstrip('/')
    db_name = os.getenv('MONGO_DB', 'expense_tracker')
    app.config["MONGO_URI"] = f"{base_uri}/{db_name}?appName=Cluster0"
    
    # Initialize extensions with app
    mongo.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    cache.init_app(app)
    limiter.init_app(app)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    from app.routes.transactions import transactions_bp
    from app.routes.accounts import accounts_bp
    from app.routes.budgets import budgets_bp
    from app.routes.categories import categories_bp
    from app.routes.logs import logs_bp
    from app.routes.export import export_bp
    from app.routes.profile import profile_bp
    from app.routes.help import help_bp
    from app.routes.updates import updates_bp
    from app.routes.errors import errors_bp
    from app.routes.health import health_bp
    from app.routes.reports import reports_bp
    
    # Register blueprints - HTML pages (no /api prefix)
    # Register blueprints - ALL API endpoints under /api/v1/
    app.register_blueprint(main_bp)  # HTML pages - no prefix
    app.register_blueprint(help_bp, url_prefix='/help')  # Help pages - no /api/v1

    # API endpoints - ALL under /api/v1/
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    app.register_blueprint(transactions_bp, url_prefix='/api/v1/transactions')
    app.register_blueprint(accounts_bp, url_prefix='/api/v1/accounts')
    app.register_blueprint(budgets_bp, url_prefix='/api/v1/budgets')
    app.register_blueprint(categories_bp, url_prefix='/api/v1/categories')
    app.register_blueprint(logs_bp, url_prefix='/api/v1/logs')           # ✅ FIXED
    app.register_blueprint(export_bp, url_prefix='/api/v1/export')
    app.register_blueprint(profile_bp, url_prefix='/api/v1/profile')     # ✅ FIXED
    app.register_blueprint(updates_bp, url_prefix='/api/v1/updates')     # ✅ FIXED
    app.register_blueprint(errors_bp, url_prefix='/api/v1/errors')       # ✅ FIXED
    app.register_blueprint(health_bp, url_prefix='/api/v1/health')       # ✅ FIXED
    app.register_blueprint(reports_bp, url_prefix='/api/v1/reports')

    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(429)
    def ratelimit_error(error):
        return render_template('errors/429.html'), 429
    
    # Context processor for template variables
    @app.context_processor
    def inject_global_vars():
        # Get theme from cookie if available
        theme = request.cookies.get('theme', 'light')
        return {
            'app_name': app.config['APP_NAME'],
            'app_version': app.config['APP_VERSION'],
            'company_name': app.config['COMPANY_NAME'],
            'current_year': datetime.now().year,
            'company_year': app.config['COMPANY_YEAR'],
            'current_theme': theme  # Add this line
        }
    
    # Test MongoDB connection and create indexes
    with app.app_context():
        try:
            # CRITICAL FIX: Use mongo.cx instead of mongo.db for ping
            mongo.cx.admin.command('ping')
            print("✅ MongoDB connected successfully")
            print(f"📊 Database: {mongo.db.name}")
            print(f"📁 Collections: {mongo.db.list_collection_names()}")
            
            # Create indexes
            init_db_indexes()
            
        except Exception as e:
            print(f"⚠️ MongoDB connection error: {e}")
            print(f"⚠️ URI used: {app.config.get('MONGO_URI', 'Not set')}")
    
    return app

def init_db_indexes():
    """Initialize database indexes"""
    try:
        # Skip if no database connection
        if mongo.db is None:
            print("⚠️ No database connection, skipping indexes")
            return
            
        # Transactions indexes
        mongo.db.transactions.create_index('date')
        mongo.db.transactions.create_index('category_id')
        mongo.db.transactions.create_index([('from_account_id', 1), ('date', -1)])
        mongo.db.transactions.create_index([('to_account_id', 1), ('date', -1)])
        mongo.db.transactions.create_index('type')
        
        # Accounts indexes
        mongo.db.accounts.create_index('name', unique=True)
        mongo.db.accounts.create_index('type')
        mongo.db.accounts.create_index('is_active')
        
        # Categories indexes
        mongo.db.categories.create_index('name', unique=True)
        mongo.db.categories.create_index('type')
        mongo.db.categories.create_index('is_deleted')
        mongo.db.categories.create_index('is_default')
        
        # Budgets indexes
        mongo.db.budgets.create_index('category_id')
        mongo.db.budgets.create_index('period')
        mongo.db.budgets.create_index('is_active')
        mongo.db.budgets.create_index([('start_date', 1), ('end_date', 1)])
        
        # Logs indexes
        mongo.db.logs.create_index('timestamp')
        mongo.db.logs.create_index('level')
        mongo.db.logs.create_index('category')
        mongo.db.logs.create_index([('timestamp', -1)])
        
        # Settings indexes
        mongo.db.settings.create_index('key', unique=True)
        
        print("✅ Database indexes created successfully")
    except Exception as e:
        print(f"⚠️ Could not create indexes: {e}")