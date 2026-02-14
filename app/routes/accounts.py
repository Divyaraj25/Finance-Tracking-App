# app/routes/accounts.py
"""
Account management routes
Version: 1.0.0
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.models import Account, Transaction, Log
from datetime import datetime
from bson import ObjectId
from app import mongo
from app.utils.helpers import format_datetime_for_api

accounts_bp = Blueprint('accounts', __name__)

@accounts_bp.route('/')
def index():
    """Accounts listing page"""
    return render_template('accounts/index.html')

# Then update the get_accounts_data function to format dates
@accounts_bp.route('/data')
def get_accounts_data():
    """Get accounts data for DataTable"""
    try:
        accounts = list(mongo.db.accounts.find({'is_active': True}).sort('name', 1))
        
        # Enhance with additional data
        for account in accounts:
            account['id'] = str(account['_id'])
            del account['_id']
            
            # Get transaction count
            transaction_count = mongo.db.transactions.count_documents({
                '$or': [
                    {'from_account_id': account['id']},
                    {'to_account_id': account['id']}
                ]
            })
            account['transaction_count'] = transaction_count
            
            # Get last transaction date and format it
            last_transaction = mongo.db.transactions.find_one(
                {'$or': [
                    {'from_account_id': account['id']},
                    {'to_account_id': account['id']}
                ]},
                sort=[('date', -1)]
            )
            if last_transaction and 'date' in last_transaction:
                account['last_transaction'] = format_datetime_for_api(last_transaction['date'])
            else:
                account['last_transaction'] = None
        
        return jsonify({
            'success': True,
            'data': accounts
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@accounts_bp.route('/create', methods=['POST'])
def create_account():
    """Create new account"""
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('name'):
            return jsonify({'success': False, 'error': 'Account name is required'}), 400
        
        if not data.get('type'):
            return jsonify({'success': False, 'error': 'Account type is required'}), 400
        
        # Check for duplicate name
        existing = mongo.db.accounts.find_one({
            'name': data['name'],
            'is_active': True
        })
        if existing:
            return jsonify({'success': False, 'error': 'Account with this name already exists'}), 400
        
        # Set defaults
        if 'balance' not in data:
            data['balance'] = 0
        if 'currency' not in data:
            data['currency'] = 'USD'
        if 'is_active' not in data:
            data['is_active'] = True
        
        account_id = Account.create(data)
        
        # Log the action
        Log.create({
            'level': 'SUCCESS',
            'category': 'ACCOUNT',
            'message': f'Account created: {data["name"]}',
            'details': {
                'account_id': account_id,
                'type': data['type'],
                'initial_balance': data['balance']
            }
        })
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'account_id': account_id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@accounts_bp.route('/<account_id>', methods=['GET', 'PUT', 'DELETE'])
def account_detail(account_id):
    """Handle individual account operations"""
    if request.method == 'GET':
        try:
            account = Account.get_by_id(account_id)
            if account:
                # Get additional statistics
                account['id'] = str(account['_id'])
                del account['_id']
                
                # Get transaction summary
                transactions = list(mongo.db.transactions.find({
                    '$or': [
                        {'from_account_id': account_id},
                        {'to_account_id': account_id}
                    ]
                }))
                
                account['statistics'] = {
                    'total_transactions': len(transactions),
                    'total_inflow': sum(t['amount'] for t in transactions if t['to_account_id'] == account_id),
                    'total_outflow': sum(t['amount'] for t in transactions if t['from_account_id'] == account_id),
                    'average_transaction': sum(t['amount'] for t in transactions) / len(transactions) if transactions else 0
                }
                
                return jsonify({
                    'success': True,
                    'data': account
                })
            return jsonify({'success': False, 'error': 'Account not found'}), 404
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Check for duplicate name if name is being changed
            if data.get('name'):
                existing = mongo.db.accounts.find_one({
                    'name': data['name'],
                    'is_active': True,
                    '_id': {'$ne': ObjectId(account_id)}
                })
                if existing:
                    return jsonify({'success': False, 'error': 'Account with this name already exists'}), 400
            
            if Account.update(account_id, data):
                return jsonify({
                    'success': True,
                    'message': 'Account updated successfully'
                })
            return jsonify({'success': False, 'error': 'Account not found'}), 404
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    elif request.method == 'DELETE':
        try:
            # Check if account has transactions
            transaction_count = mongo.db.transactions.count_documents({
                '$or': [
                    {'from_account_id': account_id},
                    {'to_account_id': account_id}
                ]
            })
            
            if transaction_count > 0:
                # Soft delete if there are transactions
                if Account.delete(account_id):
                    return jsonify({
                        'success': True,
                        'message': 'Account deactivated successfully',
                        'soft_delete': True,
                        'transaction_count': transaction_count
                    })
            else:
                # Hard delete if no transactions
                result = mongo.db.accounts.delete_one({'_id': ObjectId(account_id)})
                if result.deleted_count > 0:
                    return jsonify({
                        'success': True,
                        'message': 'Account deleted permanently',
                        'soft_delete': False
                    })
            
            return jsonify({'success': False, 'error': 'Account not found'}), 404
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

@accounts_bp.route('/summary')
def account_summary():
    """Get account summary statistics"""
    try:
        accounts = list(mongo.db.accounts.find({'is_active': True}))
        
        # Initialize with floats
        total_balance = 0.0
        by_type = {}
        by_currency = {}
        
        for account in accounts:
            # Ensure balance is float
            balance = float(account.get('balance', 0))
            total_balance += balance
            
            # Group by type
            acc_type = account.get('type', 'unknown')
            if acc_type not in by_type:
                by_type[acc_type] = {
                    'count': 0,
                    'balance': 0.0
                }
            by_type[acc_type]['count'] += 1
            by_type[acc_type]['balance'] += balance
            
            # Group by currency
            currency = account.get('currency', 'USD')
            if currency not in by_currency:
                by_currency[currency] = {
                    'count': 0,
                    'balance': 0.0
                }
            by_currency[currency]['count'] += 1
            by_currency[currency]['balance'] += balance
        
        return jsonify({
            'success': True,
            'data': {
                'total_accounts': len(accounts),
                'total_balance': total_balance,
                'by_type': by_type,
                'by_currency': by_currency
            }
        })
    except Exception as e:
        print(f"Account summary error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400

@accounts_bp.route('/types')
def get_account_types():
    """Get all account types"""
    try:
        account_types = [
            {'value': 'bank_account', 'label': 'Bank Account', 'icon': 'bank'},
            {'value': 'credit_card', 'label': 'Credit Card', 'icon': 'credit-card'},
            {'value': 'debit_card', 'label': 'Debit Card', 'icon': 'credit-card-2-front'},
            {'value': 'cash', 'label': 'Cash', 'icon': 'cash'},
            {'value': 'asset', 'label': 'Asset', 'icon': 'building'},
            {'value': 'liability', 'label': 'Liability', 'icon': 'cash-stack'}
        ]
        return jsonify({
            'success': True,
            'data': account_types
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@accounts_bp.route('/<account_id>/edit', methods=['GET'])
def get_account_for_edit(account_id):
    """Get account details for editing"""
    try:
        if not ObjectId.is_valid(account_id):
            return jsonify({'success': False, 'error': 'Invalid account ID'}), 400
            
        account = Account.get_by_id(account_id)
        if account:
            account['id'] = str(account['_id'])
            del account['_id']
            
            # Ensure balance is float
            account['balance'] = float(account.get('balance', 0))
            
            return jsonify({
                'success': True,
                'data': account
            })
        return jsonify({'success': False, 'error': 'Account not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@accounts_bp.route('/<account_id>/update', methods=['PUT'])
def update_account_route(account_id):
    """Update account (for frontend)"""
    try:
        data = request.get_json()
        
        # Check for duplicate name if name is being changed
        if data.get('name'):
            existing = mongo.db.accounts.find_one({
                'name': data['name'],
                'is_active': True,
                '_id': {'$ne': ObjectId(account_id)}
            })
            if existing:
                return jsonify({'success': False, 'error': 'Account with this name already exists'}), 400
        
        if Account.update(account_id, data):
            return jsonify({
                'success': True,
                'message': 'Account updated successfully'
            })
        return jsonify({'success': False, 'error': 'Account not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400