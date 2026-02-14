# app/routes/main.py
"""
Main routes for Expense Tracker System
Version: 1.1.0
"""
from flask import Blueprint, render_template, jsonify, request
from app import mongo
from datetime import datetime, timedelta
from app.models import Transaction, Account, Budget, Category, Log
from bson import ObjectId
from app.utils.helpers import get_current_utc_time, utc_to_local, parse_date_from_request
import pytz

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Dashboard page"""
    return render_template('dashboard/index.html')

@main_bp.route('/dashboard/data')
def dashboard_data():
    """Get dashboard data for charts"""
    try:
        # Get date range from request or use last 30 days in UTC
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if start_date_str and end_date_str:
            # Parse dates from request (they come in user's local time)
            start_date = parse_date_from_request(start_date_str)
            end_date = parse_date_from_request(end_date_str, end_of_day=True)
        else:
            # Default to last 30 days in UTC
            end_date = get_current_utc_time()
            start_date = end_date - timedelta(days=30)
        
        # Transaction summary - with proper type conversion
        transactions = list(mongo.db.transactions.find({
            'date': {'$gte': start_date, '$lte': end_date}
        }))
        
        total_income = 0.0
        total_expense = 0.0
        
        for t in transactions:
            amount = float(t.get('amount', 0))
            if t.get('type') == 'income':
                total_income += amount
            elif t.get('type') == 'expense':
                total_expense += amount
        
        # Account balances - ensure all are floats
        accounts = list(mongo.db.accounts.find({'is_active': True}))
        total_balance = 0.0
        for a in accounts:
            total_balance += float(a.get('balance', 0))
        
        # Budget summary - ensure all are floats
        budgets = list(mongo.db.budgets.find({'is_active': True}))
        total_budget = 0.0
        total_spent = 0.0
        for b in budgets:
            total_budget += float(b.get('amount', 0))
            total_spent += float(b.get('spent', 0))
        
        # Recent transactions
        recent_transactions = Transaction.get_all(page=1, per_page=5)
        
        # Ensure recent transactions have proper data types and convert dates
        if recent_transactions and 'items' in recent_transactions:
            for tx in recent_transactions['items']:
                if 'amount' in tx:
                    tx['amount'] = float(tx['amount'])
                # Convert date to ISO string for frontend (will be formatted by JS)
                if 'date' in tx and isinstance(tx['date'], datetime):
                    tx['date'] = tx['date'].isoformat()
        
        # Monthly trend
        monthly_data = get_monthly_trend()
        
        # Category breakdown
        category_breakdown = get_category_breakdown(start_date, end_date)
        
        # Account distribution
        account_distribution = get_account_distribution(accounts)
        
        return jsonify({
            'success': True,
            'data': {
                'summary': {
                    'total_balance': float(total_balance),
                    'total_income': float(total_income),
                    'total_expense': float(total_expense),
                    'total_budget': float(total_budget),
                    'total_spent': float(total_spent),
                    'remaining_budget': float(total_budget - total_spent)
                },
                'recent_transactions': recent_transactions['items'] if recent_transactions else [],
                'monthly_trend': monthly_data,
                'category_breakdown': category_breakdown,
                'account_distribution': account_distribution
            }
        })
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def get_monthly_trend():
    """Get monthly income/expense trend"""
    try:
        # Get last 12 months in UTC
        end_date = get_current_utc_time()
        start_date = end_date - timedelta(days=365)
        
        pipeline = [
            {
                '$match': {
                    'date': {'$gte': start_date, '$lte': end_date}
                }
            },
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$date'},
                        'month': {'$month': '$date'},
                        'type': '$type'
                    },
                    'total': {'$sum': '$amount'}
                }
            },
            {
                '$sort': {'_id.year': 1, '_id.month': 1}
            }
        ]
        
        result = list(mongo.db.transactions.aggregate(pipeline))
        return format_monthly_data(result)
    except Exception as e:
        print(f"Error in get_monthly_trend: {e}")
        return []

def get_category_breakdown(start_date, end_date):
    """Get expense breakdown by category"""
    try:
        pipeline = [
            {
                '$match': {
                    'date': {'$gte': start_date, '$lte': end_date},
                    'type': 'expense'
                }
            },
            {
                '$group': {
                    '_id': '$category_id',
                    'total': {'$sum': '$amount'}
                }
            },
            {
                '$sort': {'total': -1}
            },
            {
                '$limit': 10
            }
        ]
        
        result = list(mongo.db.transactions.aggregate(pipeline))
        breakdown = []
        
        for item in result:
            try:
                category = mongo.db.categories.find_one({'_id': ObjectId(item['_id'])})
                breakdown.append({
                    'category': category['name'] if category else 'Unknown',
                    'amount': float(item['total'])
                })
            except Exception as e:
                print(f"Error processing category item: {e}")
                continue
        
        return breakdown
    except Exception as e:
        print(f"Error in get_category_breakdown: {e}")
        return []

def get_account_distribution(accounts):
    """Get account balance distribution"""
    try:
        distribution = []
        for acc in accounts:
            balance = float(acc.get('balance', 0))
            if balance > 0:
                distribution.append({
                    'name': acc.get('name', 'Unknown'),
                    'balance': balance
                })
        return distribution
    except Exception as e:
        print(f"Error in get_account_distribution: {e}")
        return []

def format_monthly_data(aggregation_result):
    """Format monthly aggregation data for charts"""
    try:
        months = {}
        
        for item in aggregation_result:
            try:
                key = f"{item['_id']['year']}-{item['_id']['month']:02d}"
                if key not in months:
                    months[key] = {'month': key, 'income': 0.0, 'expense': 0.0}
                
                if item['_id']['type'] == 'income':
                    months[key]['income'] += float(item['total'])
                else:
                    months[key]['expense'] += float(item['total'])
            except Exception as e:
                print(f"Error processing monthly data item: {e}")
                continue
        
        return sorted(list(months.values()), key=lambda x: x['month'])
    except Exception as e:
        print(f"Error in format_monthly_data: {e}")
        return []