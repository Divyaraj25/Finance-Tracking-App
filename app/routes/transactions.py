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
import pytz

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
        
        # CRITICAL FIX: Convert amount to float (it comes as string from form)
        try:
            # Handle if amount is string or number
            if isinstance(data['amount'], str):
                # Remove any commas or currency symbols
                amount_str = data['amount'].replace(',', '').replace('$', '').replace('€', '').replace('£', '').strip()
                data['amount'] = float(amount_str)
            else:
                data['amount'] = float(data['amount'])
        except (ValueError, TypeError) as e:
            return jsonify({'success': False, 'error': f'Invalid amount format: {data["amount"]}'}), 400
        
        # Ensure amount is positive
        if data['amount'] <= 0:
            return jsonify({'success': False, 'error': 'Amount must be positive'}), 400
        
        # Handle date with timezone conversion
        if 'date' in data and data['date']:
            try:
                # Parse the date from the request (in user's local time)
                if isinstance(data['date'], str):
                    # If it's just YYYY-MM-DD format
                    if len(data['date']) == 10 and data['date'].count('-') == 2:
                        user_date = datetime.fromisoformat(f"{data['date']}T00:00:00")
                    else:
                        user_date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
                else:
                    user_date = data['date']
                
                # Convert to UTC for storage
                data['date'] = local_to_utc(user_date)
            except Exception as e:
                print(f"Date parsing error: {e}")
                # Default to current UTC time
                data['date'] = get_current_utc_time()
        else:
            # Default to current UTC time
            data['date'] = get_current_utc_time()
        
        # Handle tags
        if 'tags' not in data:
            data['tags'] = []
        elif isinstance(data['tags'], str):
            data['tags'] = [tag.strip() for tag in data['tags'].split(',') if tag.strip()]
        elif not isinstance(data['tags'], list):
            data['tags'] = [str(data['tags'])]
        
        # Ensure IDs are strings
        if data.get('category_id') and not isinstance(data['category_id'], str):
            data['category_id'] = str(data['category_id'])
        if data.get('from_account_id') and not isinstance(data['from_account_id'], str):
            data['from_account_id'] = str(data['from_account_id'])
        if data.get('to_account_id') and not isinstance(data['to_account_id'], str):
            data['to_account_id'] = str(data['to_account_id'])
        
        # Create transaction
        transaction_id = Transaction.create(data)
        
        # Update account balances
        if data['type'] == 'income' and data.get('to_account_id'):
            account = Account.get_by_id(data['to_account_id'])
            if account:
                new_balance = float(account['balance']) + float(data['amount'])
                Account.update(data['to_account_id'], {'balance': new_balance})
        
        elif data['type'] == 'expense' and data.get('from_account_id'):
            account = Account.get_by_id(data['from_account_id'])
            if account:
                new_balance = float(account['balance']) - float(data['amount'])
                Account.update(data['from_account_id'], {'balance': new_balance})
        
        elif data['type'] == 'transfer':
            if data.get('from_account_id') and data.get('to_account_id'):
                from_account = Account.get_by_id(data['from_account_id'])
                to_account = Account.get_by_id(data['to_account_id'])
                
                if from_account and to_account:
                    Account.update(data['from_account_id'], 
                                 {'balance': float(from_account['balance']) - float(data['amount'])})
                    Account.update(data['to_account_id'], 
                                 {'balance': float(to_account['balance']) + float(data['amount'])})
        
        # Log the action
        Log.create({
            'level': 'SUCCESS',
            'category': 'TRANSACTION',
            'message': f'Transaction created: {data["description"]}',
            'details': {
                'transaction_id': transaction_id, 
                'type': data['type'],
                'amount': float(data['amount'])
            }
        })
        
        return jsonify({
            'success': True,
            'message': 'Transaction created successfully',
            'transaction_id': transaction_id
        }), 201
        
    except Exception as e:
        print(f"Transaction creation error: {str(e)}")
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
            
            # Ensure amount is float if present
            if 'amount' in data:
                try:
                    data['amount'] = float(data['amount'])
                except (ValueError, TypeError):
                    return jsonify({'success': False, 'error': 'Invalid amount format'}), 400
            
            # Handle date update with timezone conversion
            if 'date' in data and data['date']:
                try:
                    if isinstance(data['date'], str):
                        if len(data['date']) == 10 and data['date'].count('-') == 2:
                            user_date = datetime.fromisoformat(f"{data['date']}T00:00:00")
                        else:
                            user_date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
                    else:
                        user_date = data['date']
                    
                    data['date'] = local_to_utc(user_date)
                except Exception as e:
                    print(f"Date parsing error in update: {e}")
                    # Remove date from update if parsing fails
                    del data['date']
            
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
        object_ids = [ObjectId(id) for id in transaction_ids if ObjectId.is_valid(id)]
        
        if not object_ids:
            return jsonify({'success': False, 'error': 'No valid transaction IDs'}), 400
        
        result = mongo.db.transactions.delete_many({'_id': {'$in': object_ids}})
        
        return jsonify({
            'success': True,
            'message': f'{result.deleted_count} transactions deleted successfully',
            'deleted_count': result.deleted_count
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400