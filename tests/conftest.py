# tests/conftest.py
import pytest
from app import create_app
from app import mongo
import mongomock

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    # Use mongomock for testing
    with mongomock.patch(servers=(('localhost', 27017),)):
        with app.app_context():
            mongo.db = mongomock.MongoClient().db
            yield app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()