# app/routes/budgets.py
"""
Budget management routes
Version: 1.0.0
"""
from flask import Blueprint, render_template, request, jsonify
from app.models import Budget, Category, Transaction, Log
from datetime import datetime, timedelta
from bson import ObjectId
import calendar
from app import mongo

budgets_bp = Blueprint('budgets', __name__)

@budgets_bp.route('/')
def index():
    """Budgets listing page"""
    return render_template('budgets/index.html')

@budgets_bp.route('/data')
def get_budgets_data():
    """Get budgets data for DataTable"""
    try:
        # Get optional date filters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = {'is_active': True}
        
        # Add date filters if both are provided
        if start_date and end_date:
            try:
                # Parse dates from request (user's local time) and convert to UTC
                start = parse_date_from_request(start_date)
                end = parse_date_from_request(end_date, end_of_day=True)
                if start and end:
                    query['$and'] = [
                        {'start_date': {'$lte': end}},
                        {'end_date': {'$gte': start}}
                    ]
            except Exception as e:
                print(f"Date parsing error: {e}")
        
        budgets = list(mongo.db.budgets.find(query))
        
        result = []
        for budget in budgets:
            budget_dict = {}
            budget_dict['id'] = str(budget['_id'])
            
            # Get category details
            category = Category.get_by_id(budget['category_id'])
            budget_dict['category_name'] = category['name'] if category else 'Unknown'
            budget_dict['category_type'] = category['type'] if category else 'unknown'
            
            # Calculate progress - ensure float conversion
            amount = float(budget.get('amount', 0))
            spent = float(budget.get('spent', 0))
            budget_dict['amount'] = amount
            budget_dict['spent'] = spent
            budget_dict['progress'] = (spent / amount * 100) if amount > 0 else 0
            budget_dict['remaining'] = amount - spent
            budget_dict['period'] = budget.get('period', 'monthly')
            budget_dict['status'] = get_budget_status(budget_dict)
            
            # Format dates
            if isinstance(budget.get('start_date'), datetime):
                budget_dict['start_date'] = budget['start_date'].isoformat()
            else:
                budget_dict['start_date'] = str(budget.get('start_date', ''))
                
            if isinstance(budget.get('end_date'), datetime):
                budget_dict['end_date'] = budget['end_date'].isoformat()
            else:
                budget_dict['end_date'] = str(budget.get('end_date', ''))
            
            # Get transaction count for this budget
            transaction_count = get_budget_transaction_count(budget)
            budget_dict['transaction_count'] = transaction_count
            
            result.append(budget_dict)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        print(f"Budgets data error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400

def get_budget_transaction_count(budget):
    """Get transaction count for a budget"""
    try:
        start_date = budget.get('start_date')
        end_date = budget.get('end_date')
        
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
        
        count = mongo.db.transactions.count_documents({
            'date': {'$gte': start_date, '$lte': end_date},
            'category_id': budget['category_id']
        })
        return count
    except:
        return 0

@budgets_bp.route('/create', methods=['POST'])
def create_budget():
    """Create new budget"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['category_id', 'amount', 'period']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Check if category exists
        category = Category.get_by_id(data['category_id'])
        if not category:
            return jsonify({'success': False, 'error': 'Category not found'}), 404
        
        if category.get('is_deleted'):
            return jsonify({'success': False, 'error': 'Cannot create budget for deleted category'}), 400
        
        # Check if budget already exists for this category and period
        existing = mongo.db.budgets.find_one({
            'category_id': data['category_id'],
            'period': data['period'],
            'is_active': True
        })
        
        if existing:
            # Return the existing budget ID instead of error
            return jsonify({
                'success': True,
                'message': 'Budget already exists',
                'budget_id': str(existing['_id']),
                'existing': True
            }), 200
        
        # Calculate dates based on period
        now = datetime.now()
        
        if data['period'] == 'monthly':
            start_date = datetime(now.year, now.month, 1)
            last_day = calendar.monthrange(now.year, now.month)[1]
            end_date = datetime(now.year, now.month, last_day, 23, 59, 59)
        elif data['period'] == 'weekly':
            start_date = now - timedelta(days=now.weekday())
            start_date = datetime(start_date.year, start_date.month, start_date.day)
            end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        elif data['period'] == 'yearly':
            start_date = datetime(now.year, 1, 1)
            end_date = datetime(now.year, 12, 31, 23, 59, 59)
        else:
            return jsonify({'success': False, 'error': 'Invalid period'}), 400
        
        data['start_date'] = start_date
        data['end_date'] = end_date
        data['spent'] = 0
        
        budget_id = Budget.create(data)
        
        # Calculate spent from historical transactions
        update_budget_spent(budget_id)
        
        # Log the action
        Log.create({
            'level': 'SUCCESS',
            'category': 'BUDGET',
            'message': f'Budget created for {category["name"]}',
            'details': {
                'budget_id': budget_id,
                'category_id': data['category_id'],
                'amount': data['amount'],
                'period': data['period']
            }
        })
        
        return jsonify({
            'success': True,
            'message': 'Budget created successfully',
            'budget_id': budget_id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@budgets_bp.route('/<budget_id>', methods=['GET', 'PUT', 'DELETE'])
def budget_detail(budget_id):
    """Handle individual budget operations"""
    if request.method == 'GET':
        try:
            budget = Budget.get_by_id(budget_id)
            if budget:
                budget['id'] = str(budget['_id'])
                del budget['_id']
                
                # Get category details
                category = Category.get_by_id(budget['category_id'])
                budget['category_name'] = category['name'] if category else 'Unknown'
                budget['category_type'] = category['type'] if category else 'unknown'
                
                # Calculate progress
                budget['progress'] = (budget['spent'] / budget['amount'] * 100) if budget['amount'] > 0 else 0
                budget['remaining'] = budget['amount'] - budget['spent']
                budget['status'] = get_budget_status(budget)
                
                # Get transactions in this budget
                transactions = get_budget_transactions(budget)
                budget['transactions'] = transactions[:10]  # Last 10 transactions
                budget['transaction_count'] = len(transactions)
                
                return jsonify({
                    'success': True,
                    'data': budget
                })
            return jsonify({'success': False, 'error': 'Budget not found'}), 404
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            if Budget.update(budget_id, data):
                # Recalculate spent if amount or dates changed
                if 'amount' in data or 'start_date' in data or 'end_date' in data:
                    update_budget_spent(budget_id)
                
                return jsonify({
                    'success': True,
                    'message': 'Budget updated successfully'
                })
            return jsonify({'success': False, 'error': 'Budget not found'}), 404
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    elif request.method == 'DELETE':
        try:
            # Soft delete
            result = mongo.db.budgets.update_one(
                {'_id': ObjectId(budget_id)},
                {'$set': {'is_active': False, 'updated_at': datetime.now()}}
            )
            
            if result.modified_count > 0:
                return jsonify({
                    'success': True,
                    'message': 'Budget deleted successfully'
                })
            return jsonify({'success': False, 'error': 'Budget not found'}), 404
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

@budgets_bp.route('/recalculate/<budget_id>', methods=['POST'])
def recalculate_budget(budget_id):
    """Recalculate budget spent amount"""
    try:
        old_spent = update_budget_spent(budget_id)
        budget = Budget.get_by_id(budget_id)
        
        return jsonify({
            'success': True,
            'message': 'Budget recalculated successfully',
            'data': {
                'old_spent': old_spent,
                'new_spent': budget['spent'],
                'difference': budget['spent'] - old_spent
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@budgets_bp.route('/recalculate-all', methods=['POST'])
def recalculate_all_budgets():
    """Recalculate all active budgets"""
    try:
        # Check content type and parse accordingly
        data = None
        if request.is_json:
            data = request.get_json()
        else:
            # Try to parse as form data or query string
            data = request.form.to_dict() or request.args.to_dict()
        
        start_date = data.get('start_date') if data else None
        
        budgets = list(mongo.db.budgets.find({'is_active': True}))
        updated = []
        
        for budget in budgets:
            old_spent = budget.get('spent', 0)
            new_spent = calculate_budget_spent(budget)
            
            if old_spent != new_spent:
                mongo.db.budgets.update_one(
                    {'_id': budget['_id']},
                    {'$set': {
                        'spent': new_spent,
                        'updated_at': datetime.now()
                    }}
                )
                updated.append({
                    'budget_id': str(budget['_id']),
                    'old_spent': float(old_spent),
                    'new_spent': float(new_spent)
                })
        
        return jsonify({
            'success': True,
            'message': f'Recalculated {len(updated)} budgets',
            'data': updated
        })
    except Exception as e:
        print(f"Recalculate all error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400
        
@budgets_bp.route('/summary')
def budget_summary():
    """Get budget summary statistics"""
    try:
        budgets = list(mongo.db.budgets.find({'is_active': True}))
        
        total_budget = sum(b['amount'] for b in budgets)
        total_spent = sum(b['spent'] for b in budgets)
        
        # Count by status
        status_counts = {'good': 0, 'warning': 0, 'danger': 0, 'exceeded': 0}
        
        for budget in budgets:
            if budget['amount'] > 0:
                progress = (budget['spent'] / budget['amount'] * 100)
            else:
                progress = 0
            
            if progress < 50:
                status_counts['good'] += 1
            elif progress < 75:
                status_counts['warning'] += 1
            elif progress < 100:
                status_counts['danger'] += 1
            else:
                status_counts['exceeded'] += 1
        
        # Calculate average progress safely
        average_progress = 0
        if total_budget > 0:
            average_progress = (total_spent / total_budget * 100)
        
        return jsonify({
            'success': True,
            'data': {
                'total_budget': float(total_budget),
                'total_spent': float(total_spent),
                'remaining': float(total_budget - total_spent),
                'average_progress': float(average_progress),
                'status_counts': status_counts,
                'active_budgets': len(budgets)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
             
def get_budget_status(budget):
    """Get budget status based on spending"""
    progress = (budget['spent'] / budget['amount'] * 100) if budget['amount'] > 0 else 0
    
    if progress < 50:
        return {'type': 'success', 'label': 'On Track', 'icon': 'check-circle'}
    elif progress < 75:
        return {'type': 'warning', 'label': 'Warning', 'icon': 'exclamation-triangle'}
    elif progress < 100:
        return {'type': 'danger', 'label': 'Critical', 'icon': 'exclamation-circle'}
    else:
        return {'type': 'exceeded', 'label': 'Exceeded', 'icon': 'x-circle'}

def calculate_budget_spent(budget):
    """Calculate total spent for a budget"""
    start_date = budget['start_date']
    end_date = budget['end_date']
    
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date)
    
    pipeline = [
        {
            '$match': {
                'date': {'$gte': start_date, '$lte': end_date},
                'category_id': budget['category_id'],
                'type': {'$in': ['expense', 'asset_purchase', 'credit_card_payment']}
            }
        },
        {
            '$group': {
                '_id': None,
                'total': {'$sum': '$amount'}
            }
        }
    ]
    
    result = list(mongo.db.transactions.aggregate(pipeline))
    return result[0]['total'] if result else 0

def update_budget_spent(budget_id):
    """Update budget spent amount and return old value"""
    budget = Budget.get_by_id(budget_id)
    if not budget:
        return 0
    
    old_spent = budget['spent']
    new_spent = calculate_budget_spent(budget)
    
    mongo.db.budgets.update_one(
        {'_id': ObjectId(budget_id)},
        {'$set': {
            'spent': new_spent,
            'updated_at': datetime.now()
        }}
    )
    
    return old_spent

def get_budget_transactions(budget):
    """Get transactions within budget period and category"""
    start_date = budget['start_date']
    end_date = budget['end_date']
    
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date)
    
    transactions = list(mongo.db.transactions.find({
        'date': {'$gte': start_date, '$lte': end_date},
        'category_id': budget['category_id']
    }).sort('date', -1))
    
    for t in transactions:
        t['id'] = str(t['_id'])
        del t['_id']
    
    return transactions