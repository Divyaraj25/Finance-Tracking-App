# app/routes/api.py
"""
RESTful API routes for Expense Tracker System
Version: 1.0.0
"""
from flask import Blueprint, request, jsonify
from app import limiter
from app.models import Transaction, Account, Category, Budget, Log
from datetime import datetime
from bson import ObjectId
from app import mongo

api_bp = Blueprint('api', __name__)

# ==================== API Documentation ====================

API_DOCS = {
    'info': {
        'name': 'Expense Tracker System API',
        'version': '1.0.0',
        'description': 'Complete financial management API',
        'documentation': '/api/v1/docs'
    },
    'endpoints': {
        'transactions': {
            'GET': '/api/v1/transactions - List all transactions',
            'POST': '/api/v1/transactions - Create transaction',
            'GET': '/api/v1/transactions/:id - Get transaction',
            'PUT': '/api/v1/transactions/:id - Update transaction',
            'DELETE': '/api/v1/transactions/:id - Delete transaction'
        },
        'accounts': {
            'GET': '/api/v1/accounts - List accounts',
            'POST': '/api/v1/accounts - Create account',
            'GET': '/api/v1/accounts/:id - Get account',
            'PUT': '/api/v1/accounts/:id - Update account',
            'DELETE': '/api/v1/accounts/:id - Delete account'
        },
        'categories': {
            'GET': '/api/v1/categories - List categories',
            'POST': '/api/v1/categories - Create category',
            'GET': '/api/v1/categories/:id - Get category',
            'PUT': '/api/v1/categories/:id - Update category',
            'DELETE': '/api/v1/categories/:id - Delete category'
        },
        'budgets': {
            'GET': '/api/v1/budgets - List budgets',
            'POST': '/api/v1/budgets - Create budget',
            'GET': '/api/v1/budgets/:id - Get budget',
            'PUT': '/api/v1/budgets/:id - Update budget',
            'DELETE': '/api/v1/budgets/:id - Delete budget'
        },
        'reports': {
            'GET': '/api/v1/reports/summary - Get financial summary',
            'GET': '/api/v1/reports/monthly - Get monthly report',
            'GET': '/api/v1/reports/categories - Get category report'
        },
        'export': {
            'GET': '/api/v1/export/:format - Export data in CSV/JSON/Excel'
        }
    }
}

@api_bp.route('/')
def api_root():
    """API root endpoint"""
    return jsonify({
        'message': 'Expense Tracker System API',
        'version': '1.0.0',
        'documentation': '/api/v1/docs'
    })

@api_bp.route('/docs')
def api_docs():
    """API documentation"""
    return jsonify(API_DOCS)

# ==================== Transactions API ====================

@api_bp.route('/transactions', methods=['GET'])
@limiter.limit("100 per minute")
def get_transactions():
    """Get all transactions with filters"""
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
        
        if request.args.get('start_date') and request.args.get('end_date'):
            filters['date'] = {
                '$gte': datetime.fromisoformat(request.args.get('start_date')),
                '$lte': datetime.fromisoformat(request.args.get('end_date'))
            }
        
        if request.args.get('min_amount'):
            filters['amount'] = {'$gte': float(request.args.get('min_amount'))}
        
        if request.args.get('max_amount'):
            if 'amount' not in filters:
                filters['amount'] = {}
            filters['amount']['$lte'] = float(request.args.get('max_amount'))
        
        if request.args.get('description'):
            filters['description'] = {'$regex': request.args.get('description'), '$options': 'i'}
        
        result = Transaction.get_all(filters, page, per_page)
        
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

@api_bp.route('/transactions', methods=['POST'])
@limiter.limit("50 per minute")
def create_transaction():
    """Create new transaction"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['type', 'amount', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Validate amount
        if data['amount'] <= 0:
            return jsonify({'success': False, 'error': 'Amount must be positive'}), 400
        
        # Set defaults
        if 'date' not in data:
            data['date'] = datetime.now()
        
        # Process transaction
        transaction_id = Transaction.create(data)
        
        # Update account balances
        if data['type'] == 'income' and 'to_account_id' in data:
            account = Account.get_by_id(data['to_account_id'])
            if account:
                new_balance = account['balance'] + data['amount']
                Account.update(data['to_account_id'], {'balance': new_balance})
        
        elif data['type'] == 'expense' and 'from_account_id' in data:
            account = Account.get_by_id(data['from_account_id'])
            if account:
                new_balance = account['balance'] - data['amount']
                Account.update(data['from_account_id'], {'balance': new_balance})
        
        elif data['type'] == 'transfer':
            if 'from_account_id' in data and 'to_account_id' in data:
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
            'category': 'API_TRANSACTION',
            'message': f'Transaction created: {data["description"]}',
            'details': {'transaction_id': transaction_id, 'type': data['type']}
        })
        
        return jsonify({
            'success': True,
            'message': 'Transaction created successfully',
            'transaction_id': transaction_id
        }), 201
        
    except Exception as e:
        Log.create({
            'level': 'ERROR',
            'category': 'API_TRANSACTION',
            'message': f'Failed to create transaction: {str(e)}',
            'details': {'error': str(e)}
        })
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/transactions/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Get transaction by ID"""
    try:
        transaction = Transaction.get_by_id(transaction_id)
        if transaction:
            return jsonify({
                'success': True,
                'data': Transaction.to_dict(transaction)
            })
        return jsonify({'success': False, 'error': 'Transaction not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/transactions/<transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    """Update transaction"""
    try:
        data = request.get_json()
        if Transaction.update(transaction_id, data):
            return jsonify({
                'success': True,
                'message': 'Transaction updated successfully'
            })
        return jsonify({'success': False, 'error': 'Transaction not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/transactions/<transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """Delete transaction"""
    try:
        if Transaction.delete(transaction_id):
            return jsonify({
                'success': True,
                'message': 'Transaction deleted successfully'
            })
        return jsonify({'success': False, 'error': 'Transaction not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ==================== Accounts API ====================

@api_bp.route('/accounts', methods=['GET'])
def get_accounts():
    """Get all accounts"""
    try:
        accounts = list(mongo.db.accounts.find({'is_active': True}))
        return jsonify({
            'success': True,
            'data': [Account.to_dict(acc) for acc in accounts]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/accounts', methods=['POST'])
def create_account():
    """Create new account"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['name', 'type']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Check for duplicate name
        existing = mongo.db.accounts.find_one({'name': data['name'], 'is_active': True})
        if existing:
            return jsonify({'success': False, 'error': 'Account with this name already exists'}), 400
        
        # Set defaults
        if 'balance' not in data:
            data['balance'] = 0
        if 'currency' not in data:
            data['currency'] = 'USD'
        
        account_id = Account.create(data)
        
        Log.create({
            'level': 'SUCCESS',
            'category': 'API_ACCOUNT',
            'message': f'Account created: {data["name"]}',
            'details': {'account_id': account_id}
        })
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'account_id': account_id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/accounts/<account_id>', methods=['GET'])
def get_account(account_id):
    """Get account by ID"""
    try:
        account = Account.get_by_id(account_id)
        if account:
            return jsonify({
                'success': True,
                'data': Account.to_dict(account)
            })
        return jsonify({'success': False, 'error': 'Account not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/accounts/<account_id>', methods=['PUT'])
def update_account(account_id):
    """Update account"""
    try:
        data = request.get_json()
        if Account.update(account_id, data):
            return jsonify({
                'success': True,
                'message': 'Account updated successfully'
            })
        return jsonify({'success': False, 'error': 'Account not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/accounts/<account_id>', methods=['DELETE'])
def delete_account(account_id):
    """Delete account"""
    try:
        if Account.delete(account_id):
            return jsonify({
                'success': True,
                'message': 'Account deleted successfully'
            })
        return jsonify({'success': False, 'error': 'Account not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ==================== Categories API ====================

@api_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        categories = list(mongo.db.categories.find({'is_deleted': False}))
        return jsonify({
            'success': True,
            'data': [Category.to_dict(cat) for cat in categories]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/categories', methods=['POST'])
def create_category():
    """Create new category"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'type']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Check for duplicate
        existing = mongo.db.categories.find_one({'name': data['name'], 'is_deleted': False})
        if existing:
            return jsonify({'success': False, 'error': 'Category with this name already exists'}), 400
        
        category_id = Category.create(data)
        
        return jsonify({
            'success': True,
            'message': 'Category created successfully',
            'category_id': category_id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ==================== Budgets API ====================

@api_bp.route('/budgets', methods=['GET'])
def get_budgets():
    """Get all budgets"""
    try:
        budgets = list(mongo.db.budgets.find({'is_active': True}))
        return jsonify({
            'success': True,
            'data': [Budget.to_dict(budget) for budget in budgets]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/budgets', methods=['POST'])
def create_budget():
    """Create new budget"""
    try:
        data = request.get_json()
        
        required_fields = ['category_id', 'amount', 'period']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Check if budget already exists for this category
        existing = Budget.get_by_category_and_period(data['category_id'], data['period'])
        if existing:
            return jsonify({'success': False, 'error': 'Budget already exists for this category and period'}), 400
        
        budget_id = Budget.create(data)
        
        return jsonify({
            'success': True,
            'message': 'Budget created successfully',
            'budget_id': budget_id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ==================== Reports API ====================

@api_bp.route('/reports/summary')
def get_financial_summary():
    """Get financial summary"""
    try:
        # Total balance
        accounts = list(mongo.db.accounts.find({'is_active': True}))
        total_balance = sum(a['balance'] for a in accounts)
        
        # Income vs Expense (current month)
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        
        income = sum(t['amount'] for t in mongo.db.transactions.find({
            'date': {'$gte': start_of_month},
            'type': 'income'
        }))
        
        expense = sum(t['amount'] for t in mongo.db.transactions.find({
            'date': {'$gte': start_of_month},
            'type': 'expense'
        }))
        
        # Budget summary
        budgets = list(mongo.db.budgets.find({'is_active': True}))
        total_budget = sum(b['amount'] for b in budgets)
        total_spent = sum(b['spent'] for b in budgets)
        
        return jsonify({
            'success': True,
            'data': {
                'total_balance': total_balance,
                'monthly_income': income,
                'monthly_expense': expense,
                'monthly_savings': income - expense,
                'total_budget': total_budget,
                'total_spent': total_spent,
                'remaining_budget': total_budget - total_spent,
                'savings_rate': ((income - expense) / income * 100) if income > 0 else 0
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400