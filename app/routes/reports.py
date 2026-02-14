# app/routes/reports.py
"""
Reports routes for Expense Tracker System
Version: 1.1.0
"""
from flask import Blueprint, request, jsonify
from app import mongo
from app.utils.reports import ReportGenerator
from datetime import datetime, timedelta
from bson import ObjectId
import calendar
from app.utils.helpers import get_current_utc_time, parse_date_from_request, utc_to_local

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/summary')
def get_financial_summary():
    """Get financial summary"""
    try:
        # Total balance
        accounts = list(mongo.db.accounts.find({'is_active': True}))
        total_balance = sum(a['balance'] for a in accounts)
        
        # Income vs Expense (current month in UTC)
        now = get_current_utc_time()
        start_of_month = datetime(now.year, now.month, 1, tzinfo=now.tzinfo)
        
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

@reports_bp.route('/monthly')
def get_monthly_report():
    """Get monthly income/expense report"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        
        # Create UTC dates for the month
        start_date = datetime(year, month, 1, tzinfo=pytz.UTC)
        if month == 12:
            end_date = datetime(year + 1, 1, 1, tzinfo=pytz.UTC) - timedelta(microseconds=1)
        else:
            end_date = datetime(year, month + 1, 1, tzinfo=pytz.UTC) - timedelta(microseconds=1)
        
        # Get daily breakdown
        pipeline = [
            {
                '$match': {
                    'date': {'$gte': start_date, '$lte': end_date}
                }
            },
            {
                '$group': {
                    '_id': {
                        'day': {'$dayOfMonth': '$date'},
                        'type': '$type'
                    },
                    'total': {'$sum': '$amount'}
                }
            },
            {'$sort': {'_id.day': 1}}
        ]
        
        results = list(mongo.db.transactions.aggregate(pipeline))
        
        # Format for response
        daily_data = {}
        for r in results:
            day = r['_id']['day']
            if day not in daily_data:
                daily_data[day] = {'day': day, 'income': 0, 'expense': 0}
            
            if r['_id']['type'] == 'income':
                daily_data[day]['income'] = r['total']
            else:
                daily_data[day]['expense'] = r['total']
        
        # Fill in missing days
        last_day = calendar.monthrange(year, month)[1]
        for day in range(1, last_day + 1):
            if day not in daily_data:
                daily_data[day] = {'day': day, 'income': 0, 'expense': 0}
        
        return jsonify({
            'success': True,
            'data': {
                'year': year,
                'month': month,
                'daily': sorted(list(daily_data.values()), key=lambda x: x['day']),
                'summary': {
                    'total_income': sum(d['income'] for d in daily_data.values()),
                    'total_expense': sum(d['expense'] for d in daily_data.values()),
                    'net': sum(d['income'] - d['expense'] for d in daily_data.values())
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
        
@reports_bp.route('/categories')
def get_category_report():
    """Get category spending analysis"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            # Default to current month in UTC
            now = get_current_utc_time()
            start_date = datetime(now.year, now.month, 1, tzinfo=now.tzinfo)
            if now.month == 12:
                end_date = datetime(now.year + 1, 1, 1, tzinfo=now.tzinfo) - timedelta(microseconds=1)
            else:
                end_date = datetime(now.year, now.month + 1, 1, tzinfo=now.tzinfo) - timedelta(microseconds=1)
        else:
            # Parse dates from request (user's local time) and convert to UTC
            start_date = parse_date_from_request(start_date)
            end_date = parse_date_from_request(end_date, end_of_day=True)
        
        report = ReportGenerator.generate_category_analysis(start_date, end_date)
        
        return jsonify({
            'success': True,
            'data': report
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@reports_bp.route('/income-statement')
def get_income_statement():
    """Generate income statement"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'success': False, 'error': 'start_date and end_date required'}), 400
        
        # Parse dates from request (user's local time) and convert to UTC
        utc_start = parse_date_from_request(start_date)
        utc_end = parse_date_from_request(end_date, end_of_day=True)
        
        report = ReportGenerator.generate_income_statement(utc_start, utc_end)
        
        return jsonify({
            'success': True,
            'data': report
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@reports_bp.route('/balance-sheet')
def get_balance_sheet():
    """Generate balance sheet"""
    try:
        as_of_date = request.args.get('as_of_date')
        
        if as_of_date:
            # Parse date and convert to UTC
            dt = datetime.fromisoformat(as_of_date)
            as_of_date = local_to_utc(dt)
        else:
            as_of_date = get_current_utc_time()
        
        report = ReportGenerator.generate_balance_sheet(as_of_date)
        
        return jsonify({
            'success': True,
            'data': report
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@reports_bp.route('/cash-flow')
def get_cash_flow():
    """Generate cash flow statement"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'success': False, 'error': 'start_date and end_date required'}), 400
        
        # Parse dates from request (user's local time) and convert to UTC
        utc_start = parse_date_from_request(start_date)
        utc_end = parse_date_from_request(end_date, end_of_day=True)
        
        report = ReportGenerator.generate_cash_flow(utc_start, utc_end)
        
        return jsonify({
            'success': True,
            'data': report
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400