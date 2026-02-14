# app/routes/categories.py
"""
Category management routes
Version: 1.0.0
"""
from flask import Blueprint, render_template, request, jsonify
from app.models import Category, Transaction, Budget, Log
from datetime import datetime
from bson import ObjectId
from app import mongo

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/')
def index():
    """Categories listing page"""
    return render_template('categories/index.html')

@categories_bp.route('/data')
def get_categories_data():
    """Get categories data for DataTable"""
    try:
        categories = list(mongo.db.categories.find({'is_deleted': False}).sort('name', 1))
        
        for category in categories:
            category['id'] = str(category['_id'])
            del category['_id']
            
            # Get usage statistics
            transaction_count = mongo.db.transactions.count_documents({
                'category_id': category['id']
            })
            category['transaction_count'] = transaction_count
            
            budget_count = mongo.db.budgets.count_documents({
                'category_id': category['id'],
                'is_active': True
            })
            category['budget_count'] = budget_count
            
            # Get total spent/earned
            if category['type'] in ['expense', 'liability']:
                total = list(mongo.db.transactions.aggregate([
                    {'$match': {'category_id': category['id']}},
                    {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
                ]))
                category['total_amount'] = total[0]['total'] if total else 0
            else:
                category['total_amount'] = 0
        
        return jsonify({
            'success': True,
            'data': categories
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@categories_bp.route('/create', methods=['POST'])
def create_category():
    """Create new category"""
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('name'):
            return jsonify({'success': False, 'error': 'Category name is required'}), 400
        
        if not data.get('type'):
            return jsonify({'success': False, 'error': 'Category type is required'}), 400
        
        # Check for duplicate name
        existing = mongo.db.categories.find_one({
            'name': data['name'],
            'is_deleted': False
        })
        if existing:
            return jsonify({'success': False, 'error': 'Category with this name already exists'}), 400
        
        # Set defaults
        if 'description' not in data:
            data['description'] = f'Category for {data["name"]}'
        if 'is_default' not in data:
            data['is_default'] = False
        
        category_id = Category.create(data)
        
        # Log the action
        Log.create({
            'level': 'SUCCESS',
            'category': 'CATEGORY',
            'message': f'Category created: {data["name"]}',
            'details': {
                'category_id': category_id,
                'type': data['type']
            }
        })
        
        return jsonify({
            'success': True,
            'message': 'Category created successfully',
            'category_id': category_id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@categories_bp.route('/<category_id>', methods=['GET', 'PUT', 'DELETE'])
def category_detail(category_id):
    """Handle individual category operations"""
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(category_id):
            return jsonify({'success': False, 'error': 'Invalid category ID format'}), 400
        
        if request.method == 'GET':
            category = Category.get_by_id(category_id)
            if category:
                category['id'] = str(category['_id'])
                del category['_id']
                
                # Get detailed statistics
                stats = get_category_statistics(category_id)
                category['statistics'] = stats
                
                return jsonify({
                    'success': True,
                    'data': category
                })
            return jsonify({'success': False, 'error': 'Category not found'}), 404
        
        elif request.method == 'PUT':
            data = request.get_json()
            category = Category.get_by_id(category_id)
            
            if not category:
                return jsonify({'success': False, 'error': 'Category not found'}), 404
            
            if category.get('is_default'):
                return jsonify({'success': False, 'error': 'Cannot edit default categories'}), 400
            
            # Check for duplicate name if name is being changed
            if data.get('name') and data['name'] != category['name']:
                existing = mongo.db.categories.find_one({
                    'name': data['name'],
                    'is_deleted': False,
                    '_id': {'$ne': ObjectId(category_id)}
                })
                if existing:
                    return jsonify({'success': False, 'error': 'Category with this name already exists'}), 400
            
            if Category.update(category_id, data):
                return jsonify({
                    'success': True,
                    'message': 'Category updated successfully'
                })
            return jsonify({'success': False, 'error': 'Category not found'}), 404
        
        elif request.method == 'DELETE':
            category = Category.get_by_id(category_id)
            
            if not category:
                return jsonify({'success': False, 'error': 'Category not found'}), 404
            
            if category.get('is_default'):
                return jsonify({'success': False, 'error': 'Cannot delete default categories'}), 400
            
            # Check if category is in use
            transaction_count = mongo.db.transactions.count_documents({
                'category_id': category_id
            })
            
            budget_count = mongo.db.budgets.count_documents({
                'category_id': category_id,
                'is_active': True
            })
            
            if transaction_count > 0 or budget_count > 0:
                # Find default category of same type
                default_category = mongo.db.categories.find_one({
                    'type': category['type'],
                    'is_default': True,
                    'is_deleted': False
                })
                
                if default_category:
                    default_id = str(default_category['_id'])
                    
                    # Update all transactions
                    mongo.db.transactions.update_many(
                        {'category_id': category_id},
                        {'$set': {
                            'category_id': default_id,
                            'updated_at': datetime.now()
                        }}
                    )
                    
                    # Update all budgets
                    mongo.db.budgets.update_many(
                        {'category_id': category_id},
                        {'$set': {
                            'category_id': default_id,
                            'updated_at': datetime.now()
                        }}
                    )
            
            # Soft delete
            result = mongo.db.categories.update_one(
                {'_id': ObjectId(category_id)},
                {'$set': {
                    'is_deleted': True,
                    'updated_at': datetime.now()
                }}
            )
            
            if result.modified_count > 0:
                return jsonify({
                    'success': True,
                    'message': 'Category deleted successfully'
                })
            return jsonify({'success': False, 'error': 'Category not found'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@categories_bp.route('/types')
def get_category_types():
    """Get all category types"""
    types = [
        {'value': 'income', 'label': 'Income', 'icon': 'arrow-down'},
        {'value': 'expense', 'label': 'Expense', 'icon': 'arrow-up'},
        {'value': 'asset', 'label': 'Asset', 'icon': 'building'},
        {'value': 'liability', 'label': 'Liability', 'icon': 'credit-card'}
    ]
    return jsonify({
        'success': True,
        'data': types
    })

@categories_bp.route('/by-type/<category_type>')
def get_categories_by_type(category_type):
    """Get categories by type"""
    try:
        # Validate category type
        valid_types = ['income', 'expense', 'asset', 'liability']
        if category_type not in valid_types:
            return jsonify({'success': False, 'error': 'Invalid category type'}), 400
        
        categories = list(mongo.db.categories.find({
            'type': category_type,
            'is_deleted': False
        }).sort('name', 1))
        
        result = []
        for cat in categories:
            # Get transaction count
            transaction_count = mongo.db.transactions.count_documents({
                'category_id': str(cat['_id'])
            })
            
            # Get budget count
            budget_count = mongo.db.budgets.count_documents({
                'category_id': str(cat['_id']),
                'is_active': True
            })
            
            # Get total amount
            total_amount = 0
            if category_type in ['expense', 'liability']:
                pipeline = [
                    {'$match': {'category_id': str(cat['_id'])}},
                    {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
                ]
                total_result = list(mongo.db.transactions.aggregate(pipeline))
                if total_result:
                    total_amount = float(total_result[0]['total'])
            
            result.append({
                'id': str(cat['_id']),
                'name': cat['name'],
                'type': cat['type'],
                'description': cat.get('description', ''),
                'is_default': cat.get('is_default', False),
                'transaction_count': transaction_count,
                'budget_count': budget_count,
                'total_amount': total_amount
            })
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

def get_category_statistics(category_id):
    """Get detailed statistics for a category"""
    try:
        # Get monthly totals
        monthly = list(mongo.db.transactions.aggregate([
            {'$match': {'category_id': category_id}},
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$date'},
                        'month': {'$month': '$date'}
                    },
                    'total': {'$sum': '$amount'},
                    'count': {'$sum': 1}
                }
            },
            {'$sort': {'_id.year': -1, '_id.month': -1}},
            {'$limit': 12}
        ]))
        
        # Format the monthly dates for display
        for month_data in monthly:
            year = month_data['_id']['year']
            month = month_data['_id']['month']
            month_data['period'] = f"{year}-{month:02d}"
        
        # Get average transaction
        avg = list(mongo.db.transactions.aggregate([
            {'$match': {'category_id': category_id}},
            {
                '$group': {
                    '_id': None,
                    'average': {'$avg': '$amount'},
                    'max': {'$max': '$amount'},
                    'min': {'$min': '$amount'}
                }
            }
        ]))
        
        return {
            'monthly_totals': monthly,
            'average_amount': avg[0]['average'] if avg else 0,
            'max_amount': avg[0]['max'] if avg else 0,
            'min_amount': avg[0]['min'] if avg else 0,
            'total_transactions': mongo.db.transactions.count_documents({'category_id': category_id}),
            'active_budgets': mongo.db.budgets.count_documents({
                'category_id': category_id,
                'is_active': True
            })
        }
    except Exception as e:
        return {}