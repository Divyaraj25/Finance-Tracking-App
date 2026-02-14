# tests/test_transactions.py
import pytest
from datetime import datetime

def test_create_transaction(client):
    """Test creating a transaction"""
    response = client.post('/api/v1/transactions', json={
        'type': 'expense',
        'amount': 50.00,
        'description': 'Test transaction',
        'date': datetime.now().isoformat()
    })
    assert response.status_code == 201
    assert response.json['success'] == True

def test_get_transactions(client):
    """Test getting transactions"""
    response = client.get('/api/v1/transactions')
    assert response.status_code == 200
    assert response.json['success'] == True

def test_invalid_transaction(client):
    """Test invalid transaction"""
    response = client.post('/api/v1/transactions', json={
        'amount': -50.00
    })
    assert response.status_code == 400
    assert response.json['success'] == False