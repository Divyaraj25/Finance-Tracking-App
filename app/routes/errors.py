# app/routes/errors.py
"""
Error handling and monitoring routes
Version: 1.0.0
"""
from flask import Blueprint, render_template, request, jsonify
from app.models import Log
from datetime import datetime, timedelta
from bson import ObjectId
from app import mongo

errors_bp = Blueprint('errors', __name__)

@errors_bp.route('/')
def index():
    """Error monitoring page"""
    return render_template('errors/index.html')

@errors_bp.route('/data')
def get_errors():
    """Get error logs"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        # Build filters
        filters = {
            'level': 'ERROR'
        }
        
        if request.args.get('category'):
            filters['category'] = request.args.get('category')
        
        if request.args.get('start_date') and request.args.get('end_date'):
            filters['timestamp'] = {
                '$gte': datetime.fromisoformat(request.args.get('start_date')),
                '$lte': datetime.fromisoformat(request.args.get('end_date'))
            }
        
        if request.args.get('search'):
            filters['$or'] = [
                {'message': {'$regex': request.args.get('search'), '$options': 'i'}},
                {'details': {'$regex': request.args.get('search'), '$options': 'i'}}
            ]
        
        skip = (page - 1) * per_page
        
        errors = list(mongo.db.logs.find(filters)
                     .sort('timestamp', -1)
                     .skip(skip)
                     .limit(per_page))
        
        total = mongo.db.logs.count_documents(filters)
        
        for error in errors:
            error['id'] = str(error['_id'])
            del error['_id']
        
        return jsonify({
            'success': True,
            'data': errors,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@errors_bp.route('/summary')
def get_error_summary():
    """Get error summary statistics"""
    try:
        now = datetime.now()
        today_start = datetime(now.year, now.month, now.day)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Total errors
        total_errors = mongo.db.logs.count_documents({'level': 'ERROR'})
        
        # Errors by category
        by_category = list(mongo.db.logs.aggregate([
            {'$match': {'level': 'ERROR'}},
            {'$group': {'_id': '$category', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]))
        
        # Errors over time
        by_day = list(mongo.db.logs.aggregate([
            {
                '$match': {
                    'level': 'ERROR',
                    'timestamp': {'$gte': month_ago}
                }
            },
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$timestamp'},
                        'month': {'$month': '$timestamp'},
                        'day': {'$dayOfMonth': '$timestamp'}
                    },
                    'count': {'$sum': 1}
                }
            },
            {'$sort': {'_id.year': 1, '_id.month': 1, '_id.day': 1}}
        ]))
        
        # Most frequent errors
        frequent = list(mongo.db.logs.aggregate([
            {'$match': {'level': 'ERROR'}},
            {'$group': {
                '_id': '$message',
                'count': {'$sum': 1},
                'last_occurrence': {'$max': '$timestamp'}
            }},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]))
        
        return jsonify({
            'success': True,
            'data': {
                'total_errors': total_errors,
                'errors_today': mongo.db.logs.count_documents({
                    'level': 'ERROR',
                    'timestamp': {'$gte': today_start}
                }),
                'errors_week': mongo.db.logs.count_documents({
                    'level': 'ERROR',
                    'timestamp': {'$gte': week_ago}
                }),
                'errors_month': mongo.db.logs.count_documents({
                    'level': 'ERROR',
                    'timestamp': {'$gte': month_ago}
                }),
                'by_category': by_category,
                'by_day': by_day,
                'frequent_errors': frequent
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@errors_bp.route('/<error_id>')
def get_error_detail(error_id):
    """Get detailed error information"""
    try:
        error = mongo.db.logs.find_one({'_id': ObjectId(error_id)})
        
        if not error:
            return jsonify({'success': False, 'error': 'Error not found'}), 404
        
        error['id'] = str(error['_id'])
        del error['_id']
        
        # Find similar errors
        similar = list(mongo.db.logs.find({
            '_id': {'$ne': ObjectId(error_id)},
            'message': error['message'],
            'level': 'ERROR'
        }).sort('timestamp', -1).limit(5))
        
        for e in similar:
            e['id'] = str(e['_id'])
            del e['_id']
        
        error['similar_errors'] = similar
        
        return jsonify({
            'success': True,
            'data': error
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@errors_bp.route('/resolve/<error_id>', methods=['POST'])
def resolve_error(error_id):
    """Mark error as resolved"""
    try:
        # Add resolution note
        data = request.get_json()
        
        Log.create({
            'level': 'INFO',
            'category': 'ERROR_RESOLUTION',
            'message': f'Error {error_id} marked as resolved',
            'details': {
                'error_id': error_id,
                'resolution': data.get('resolution', ''),
                'resolved_by': 'system'
            }
        })
        
        return jsonify({
            'success': True,
            'message': 'Error marked as resolved'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@errors_bp.route('/categories')
def get_error_categories():
    """Get error categories"""
    try:
        categories = list(mongo.db.logs.distinct('category', {'level': 'ERROR'}))
        return jsonify({
            'success': True,
            'data': categories
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400