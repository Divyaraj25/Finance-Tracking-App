# app/routes/logs.py
"""
Log viewing and management routes
Version: 1.0.0
"""
from flask import Blueprint, render_template, request, jsonify
from app.models import Log
from app import mongo
from datetime import datetime, timedelta

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/')
def index():
    """Logs listing page"""
    return render_template('logs/index.html')

@logs_bp.route('/data')
def get_logs_data():
    """Get logs data for DataTable"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        # Build filters
        filters = {}
        
        if request.args.get('level'):
            filters['level'] = request.args.get('level')
        
        if request.args.get('category'):
            filters['category'] = request.args.get('category')
        
        if request.args.get('search'):
            filters['$or'] = [
                {'message': {'$regex': request.args.get('search'), '$options': 'i'}},
                {'details': {'$regex': request.args.get('search'), '$options': 'i'}}
            ]
        
        if request.args.get('start_date') and request.args.get('end_date'):
            try:
                filters['timestamp'] = {
                    '$gte': datetime.fromisoformat(request.args.get('start_date')),
                    '$lte': datetime.fromisoformat(request.args.get('end_date'))
                }
            except:
                pass
        
        # Get total count
        total = mongo.db.logs.count_documents(filters)
        
        # Get paginated results
        skip = (page - 1) * per_page
        logs = list(mongo.db.logs.find(filters)
                   .sort('timestamp', -1)
                   .skip(skip)
                   .limit(per_page))
        
        # Convert ObjectId to string and ensure timestamp is string
        for log in logs:
            log['id'] = str(log['_id'])
            del log['_id']
            # Ensure timestamp is ISO format string
            if isinstance(log['timestamp'], datetime):
                log['timestamp'] = log['timestamp'].isoformat()
        
        return jsonify({
            'success': True,
            'data': logs,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
              
@logs_bp.route('/levels')
def get_log_levels():
    """Get all log levels with counts"""
    try:
        pipeline = [
            {
                '$group': {
                    '_id': '$level',
                    'count': {'$sum': 1},
                    'last_timestamp': {'$max': '$timestamp'}
                }
            },
            {'$sort': {'count': -1}}
        ]
        
        levels = list(mongo.db.logs.aggregate(pipeline))
        
        return jsonify({
            'success': True,
            'data': levels
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@logs_bp.route('/categories')
def get_log_categories():
    """Get all log categories with counts"""
    try:
        pipeline = [
            {
                '$group': {
                    '_id': '$category',
                    'count': {'$sum': 1}
                }
            },
            {'$sort': {'count': -1}}
        ]
        
        categories = list(mongo.db.logs.aggregate(pipeline))
        
        return jsonify({
            'success': True,
            'data': categories
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@logs_bp.route('/summary')
def get_log_summary():
    """Get log summary statistics"""
    try:
        now = datetime.now()
        today_start = datetime(now.year, now.month, now.day)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        summary = {
            'total': mongo.db.logs.count_documents({}),
            'today': mongo.db.logs.count_documents({'timestamp': {'$gte': today_start}}),
            'this_week': mongo.db.logs.count_documents({'timestamp': {'$gte': week_ago}}),
            'this_month': mongo.db.logs.count_documents({'timestamp': {'$gte': month_ago}}),
            'by_level': {},
            'by_category': {}
        }
        
        # Get counts by level
        levels = mongo.db.logs.aggregate([
            {'$group': {'_id': '$level', 'count': {'$sum': 1}}}
        ])
        
        for level in levels:
            summary['by_level'][level['_id']] = level['count']
        
        # Get top 10 categories
        categories = mongo.db.logs.aggregate([
            {'$group': {'_id': '$category', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ])
        
        for category in categories:
            summary['by_category'][category['_id']] = category['count']
        
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@logs_bp.route('/clear', methods=['POST'])
def clear_logs():
    """Clear logs older than specified days"""
    try:
        data = request.get_json()
        days = data.get('days', 30)
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        result = mongo.db.logs.delete_many({
            'timestamp': {'$lt': cutoff_date}
        })
        
        return jsonify({
            'success': True,
            'message': f'Cleared {result.deleted_count} logs older than {days} days',
            'deleted_count': result.deleted_count
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400