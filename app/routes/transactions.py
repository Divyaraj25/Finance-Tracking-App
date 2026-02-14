# app/routes/transactions.py
"""
Transaction management routes
Version: 1.1.0
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.models import Transaction, Account, Category, Log
from datetime import datetime
from bson import ObjectId
from app import mongo
from app.utils.helpers import local_to_utc, parse_date_from_request, get_current_utc_time

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/')
def index():
    """Transactions listing page"""
    return render_template('transactions/index.html')

@transactions_bp.route('/data')
def get_transactions_data():
    """Get transactions data for DataTable"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Build filters
        filters = {}
        
        if request.args.get('type'):
            filters['type'] = request.args.get('type')
        
        if request.args.get('category_id'):
            filters['category_id'] = request.args.get('category_id')
        
        if request.args.get('account_id'):
            filters['$or'] = [
                {'from_account_id': request.args.get('account_id')},
                {'to_account_id': request.args.get('account_id')}
            ]
        
        # Handle date filters with timezone conversion
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        if start_date and end_date:
            # Convert user's local dates to UTC for query
            utc_start = parse_date_from_request(start_date)
            utc_end = parse_date_from_request(end_date, end_of_day=True)
            if utc_start and utc_end:
                filters['date'] = {
                    '$gte': utc_start,
                    '$lte': utc_end
                }
        
        if request.args.get('search'):
            filters['description'] = {
                '$regex': request.args.get('search'),
                '$options': 'i'
            }
        
        result = Transaction.get_all(filters, page, per_page)
        
        # Enhance with related data and format dates
        for transaction in result['items']:
            # Add category name
            if transaction.get('category_id'):
                category = Category.get_by_id(transaction['category_id'])
                transaction['category_name'] = category['name'] if category else 'Unknown'
            
            # Add account names
            if transaction.get('from_account_id'):
                account = Account.get_by_id(transaction['from_account_id'])
                transaction['from_account_name'] = account['name'] if account else 'Unknown'
            
            if transaction.get('to_account_id'):
                account = Account.get_by_id(transaction['to_account_id'])
                transaction['to_account_name'] = account['name'] if account else 'Unknown'
            
            # Convert datetime to ISO string for frontend
            if 'date' in transaction and isinstance(transaction['date'], datetime):
                transaction['date'] = transaction['date'].isoformat()
            if 'created_at' in transaction and isinstance(transaction['created_at'], datetime):
                transaction['created_at'] = transaction['created_at'].isoformat()
            if 'updated_at' in transaction and isinstance(transaction['updated_at'], datetime):
                transaction['updated_at'] = transaction['updated_at'].isoformat()
        
        return jsonify({
            'success': True,
            'data': result['items'],
            'pagination': {
                'page': result['page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'pages': result['pages']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@transactions_bp.route('/create', methods=['POST'])
def create_transaction():
    """Create new transaction"""
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('type') or not data.get('amount') or not data.get('description'):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Handle date with timezone conversion
        if 'date' in data and data['date']:
            # Parse the date from the request (in user's local time)
            user_date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
            # Convert to UTC for storage
            data['date'] = local_to_utc(user_date)
        else:
            # Default to current UTC time
            data['date'] = get_current_utc_time()
        
        if 'tags' not in data:
            data['tags'] = []
        
        # Create transaction
        transaction_id = Transaction.create(data)
        
        # Update account balances (these are numeric, not timezone affected)
        if data['type'] == 'income' and data.get('to_account_id'):
            account = Account.get_by_id(data['to_account_id'])
            if account:
                new_balance = account['balance'] + data['amount']
                Account.update(data['to_account_id'], {'balance': new_balance})
        
        elif data['type'] == 'expense' and data.get('from_account_id'):
            account = Account.get_by_id(data['from_account_id'])
            if account:
                new_balance = account['balance'] - data['amount']
                Account.update(data['from_account_id'], {'balance': new_balance})
        
        elif data['type'] == 'transfer':
            if data.get('from_account_id') and data.get('to_account_id'):
                from_account = Account.get_by_id(data['from_account_id'])
                to_account = Account.get_by_id(data['to_account_id'])
                
                if from_account and to_account:
                    Account.update(data['from_account_id'], 
                                 {'balance': from_account['balance'] - data['amount']})
                    Account.update(data['to_account_id'], 
                                 {'balance': to_account['balance'] + data['amount']})
        
        # Log the action
        Log.create({
            'level': 'SUCCESS',
            'category': 'TRANSACTION',
            'message': f'Transaction created: {data["description"]}',
            'details': {'transaction_id': transaction_id, 'type': data['type']}
        })
        
        return jsonify({
            'success': True,
            'message': 'Transaction created successfully',
            'transaction_id': transaction_id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@transactions_bp.route('/<transaction_id>', methods=['GET', 'PUT', 'DELETE'])
def transaction_detail(transaction_id):
    """Handle individual transaction operations"""
    if request.method == 'GET':
        try:
            transaction = Transaction.get_by_id(transaction_id)
            if transaction:
                # Convert datetime to ISO string
                if 'date' in transaction and isinstance(transaction['date'], datetime):
                    transaction['date'] = transaction['date'].isoformat()
                return jsonify({
                    'success': True,
                    'data': Transaction.to_dict(transaction)
                })
            return jsonify({'success': False, 'error': 'Transaction not found'}), 404
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Handle date update with timezone conversion
            if 'date' in data and data['date']:
                user_date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
                data['date'] = local_to_utc(user_date)
            
            if Transaction.update(transaction_id, data):
                return jsonify({
                    'success': True,
                    'message': 'Transaction updated successfully'
                })
            return jsonify({'success': False, 'error': 'Transaction not found'}), 404
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    elif request.method == 'DELETE':
        try:
            if Transaction.delete(transaction_id):
                return jsonify({
                    'success': True,
                    'message': 'Transaction deleted successfully'
                })
            return jsonify({'success': False, 'error': 'Transaction not found'}), 404
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

@transactions_bp.route('/bulk-delete', methods=['POST'])
def bulk_delete():
    """Delete multiple transactions"""
    try:
        data = request.get_json()
        transaction_ids = data.get('ids', [])
        
        if not transaction_ids:
            return jsonify({'success': False, 'error': 'No transaction IDs provided'}), 400
        
        # Convert string IDs to ObjectId
        object_ids = [ObjectId(id) for id in transaction_ids]
        
        result = mongo.db.transactions.delete_many({'_id': {'$in': object_ids}})
        
        return jsonify({
            'success': True,
            'message': f'{result.deleted_count} transactions deleted successfully',
            'deleted_count': result.deleted_count
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400