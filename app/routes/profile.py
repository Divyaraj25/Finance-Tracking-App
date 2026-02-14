# app/routes/profile.py
"""
User profile and settings routes
Version: 1.0.0
"""
from flask import Blueprint, render_template, request, jsonify, session
from app.models import Settings, Log
from datetime import datetime
import uuid
from app import mongo

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/')
def index():
    """Profile page"""
    return render_template('profile/index.html')

@profile_bp.route('/settings')
def get_settings():
    """Get all settings"""
    try:
        settings = {}
        
        # Application settings
        settings['app_name'] = Settings.get('app_name', 'Expense Tracker System')
        settings['app_version'] = Settings.get('app_version', '1.0.0')
        settings['company_name'] = Settings.get('company_name', 'ExpenseTracker')
        settings['company_year'] = Settings.get('company_year', '2026')
        
        # User preferences
        settings['currency'] = Settings.get('currency', 'USD')
        settings['date_format'] = Settings.get('date_format', 'YYYY-MM-DD')
        settings['time_format'] = Settings.get('time_format', '24h')
        settings['theme'] = Settings.get('theme', 'light')
        settings['items_per_page'] = Settings.get('items_per_page', 20)
        settings['notifications_enabled'] = Settings.get('notifications_enabled', True)
        
        # NEW: Timezone and regional settings
        settings['timezone'] = Settings.get('timezone', 'local')
        settings['week_start'] = Settings.get('week_start', 'monday')
        settings['number_format'] = Settings.get('number_format', '1,234.56')
        settings['first_day'] = Settings.get('first_day', '1')  # 0=Sunday, 1=Monday, 6=Saturday
        
        # Export settings
        settings['export_format'] = Settings.get('export_format', 'csv')
        
        # Default categories
        settings['default_income_category'] = Settings.get('default_income_category', 'uncategorized_income')
        settings['default_expense_category'] = Settings.get('default_expense_category', 'uncategorized_expense')
        
        return jsonify({
            'success': True,
            'data': settings
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@profile_bp.route('/settings', methods=['POST'])
def update_settings():
    """Update settings"""
    try:
        data = request.get_json()
        
        for key, value in data.items():
            Settings.set(key, value)
        
        # Log the action
        Log.create({
            'level': 'CHANGE',
            'category': 'SETTINGS',
            'message': 'Settings updated',
            'details': {'updated_fields': list(data.keys())}
        })
        
        return jsonify({
            'success': True,
            'message': 'Settings updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@profile_bp.route('/statistics')
def get_user_statistics():
    """Get user statistics"""
    try:
        # Get session ID or create one
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
            session['start_time'] = datetime.now().isoformat()
        
        # Calculate statistics
        stats = {
            'session_id': session.get('session_id'),
            'session_start': session.get('start_time'),
            'session_duration': calculate_session_duration(session.get('start_time')),
            
            # Application usage
            'total_transactions': mongo.db.transactions.count_documents({}),
            'total_accounts': mongo.db.accounts.count_documents({'is_active': True}),
            'total_categories': mongo.db.categories.count_documents({'is_deleted': False}),
            'total_budgets': mongo.db.budgets.count_documents({'is_active': True}),
            
            # Current totals
            'total_balance': calculate_total_balance(),
            'total_budget_amount': calculate_total_budget(),
            'total_budget_spent': calculate_total_spent(),
            
            # Activity today
            'transactions_today': count_todays_transactions(),
            'logs_today': count_todays_logs()
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@profile_bp.route('/reset-session', methods=['POST'])
def reset_session():
    """Reset user session"""
    try:
        session.clear()
        return jsonify({
            'success': True,
            'message': 'Session reset successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

def calculate_session_duration(start_time_str):
    """Calculate session duration in minutes"""
    if not start_time_str:
        return 0
    
    try:
        start_time = datetime.fromisoformat(start_time_str)
        duration = datetime.now() - start_time
        return round(duration.total_seconds() / 60, 1)
    except:
        return 0

def calculate_total_balance():
    """Calculate total balance across all accounts"""
    result = mongo.db.accounts.aggregate([
        {'$match': {'is_active': True}},
        {'$group': {'_id': None, 'total': {'$sum': '$balance'}}}
    ])
    result = list(result)
    return result[0]['total'] if result else 0

def calculate_total_budget():
    """Calculate total budget amount"""
    result = mongo.db.budgets.aggregate([
        {'$match': {'is_active': True}},
        {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
    ])
    result = list(result)
    return result[0]['total'] if result else 0

def calculate_total_spent():
    """Calculate total spent from budgets"""
    result = mongo.db.budgets.aggregate([
        {'$match': {'is_active': True}},
        {'$group': {'_id': None, 'total': {'$sum': '$spent'}}}
    ])
    result = list(result)
    return result[0]['total'] if result else 0

def count_todays_transactions():
    """Count transactions created today"""
    today_start = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
    return mongo.db.transactions.count_documents({
        'created_at': {'$gte': today_start}
    })

def count_todays_logs():
    """Count logs created today"""
    today_start = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
    return mongo.db.logs.count_documents({
        'timestamp': {'$gte': today_start}
    })