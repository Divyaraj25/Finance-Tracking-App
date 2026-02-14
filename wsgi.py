# wsgi.py
"""
WSGI entry point for production
Version: 1.0.0
"""
from app import create_app

app = create_app('production')