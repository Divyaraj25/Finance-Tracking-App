# app/routes/health.py
"""
Health check routes for monitoring
Version: 1.0.0
"""
from flask import Blueprint, jsonify
from app import mongo
from datetime import datetime
import platform
import os

health_bp = Blueprint('health', __name__)

@health_bp.route('/')
def health_check():
    """Basic health check endpoint"""
    try:
        # Check MongoDB connection
        mongo.db.command('ping')
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'expense-tracker',
        'version': '1.0.0',
        'database': db_status,
        'environment': os.getenv('FLASK_ENV', 'development')
    })

@health_bp.route('/detailed')
def detailed_health():
    """Detailed health check for monitoring systems"""
    health_data = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': {
            'name': 'Expense Tracker System',
            'version': '1.0.0',
            'environment': os.getenv('FLASK_ENV', 'development')
        },
        'system': {
            'python_version': platform.python_version(),
            'platform': platform.platform(),
            'hostname': platform.node()
        },
        'checks': {}
    }
    
    # Check MongoDB
    try:
        mongo.db.command('ping')
        health_data['checks']['mongodb'] = {
            'status': 'healthy',
            'latency': measure_mongodb_latency()
        }
    except Exception as e:
        health_data['status'] = 'degraded'
        health_data['checks']['mongodb'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Check disk space
    try:
        import shutil
        disk_usage = shutil.disk_usage('/')
        health_data['checks']['disk'] = {
            'status': 'healthy',
            'total': disk_usage.total,
            'used': disk_usage.used,
            'free': disk_usage.free,
            'percent_used': (disk_usage.used / disk_usage.total) * 100
        }
    except Exception as e:
        health_data['checks']['disk'] = {
            'status': 'unknown',
            'error': str(e)
        }
    
    # Check memory
    try:
        import psutil
        memory = psutil.virtual_memory()
        health_data['checks']['memory'] = {
            'status': 'healthy' if memory.percent < 90 else 'critical',
            'total': memory.total,
            'available': memory.available,
            'percent_used': memory.percent
        }
    except Exception as e:
        health_data['checks']['memory'] = {
            'status': 'unknown',
            'error': str(e)
        }
    
    return jsonify(health_data)

def measure_mongodb_latency():
    """Measure MongoDB query latency"""
    import time
    start = time.time()
    mongo.db.command('ping')
    latency = (time.time() - start) * 1000  # Convert to milliseconds
    return round(latency, 2)