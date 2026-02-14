# app/utils/reports.py
"""
Report generation utilities
Version: 1.0.0
"""
from datetime import datetime, timedelta
from app import mongo
from collections import defaultdict

class ReportGenerator:
    """Financial report generator"""
    
    @staticmethod
    def generate_income_statement(start_date, end_date):
        """Generate income statement"""
        # Get income transactions
        income = list(mongo.db.transactions.find({
            'date': {'$gte': start_date, '$lte': end_date},
            'type': 'income'
        }))
        
        # Get expense transactions
        expenses = list(mongo.db.transactions.find({
            'date': {'$gte': start_date, '$lte': end_date},
            'type': 'expense'
        }))
        
        # Group by category
        income_by_category = defaultdict(float)
        for t in income:
            income_by_category[t['category_id']] += t['amount']
        
        expenses_by_category = defaultdict(float)
        for t in expenses:
            expenses_by_category[t['category_id']] += t['amount']
        
        # Get category names
        categories = {}
        for cat_id in set(list(income_by_category.keys()) + list(expenses_by_category.keys())):
            category = mongo.db.categories.find_one({'_id': cat_id})
            if category:
                categories[cat_id] = category['name']
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'income': {
                'total': sum(income_by_category.values()),
                'by_category': [
                    {
                        'category': categories.get(cat_id, 'Unknown'),
                        'amount': amount
                    }
                    for cat_id, amount in income_by_category.items()
                ]
            },
            'expenses': {
                'total': sum(expenses_by_category.values()),
                'by_category': [
                    {
                        'category': categories.get(cat_id, 'Unknown'),
                        'amount': amount
                    }
                    for cat_id, amount in expenses_by_category.items()
                ]
            },
            'net_income': sum(income_by_category.values()) - sum(expenses_by_category.values())
        }
    
    @staticmethod
    def generate_balance_sheet(as_of_date):
        """Generate balance sheet"""
        # Get all active accounts
        accounts = list(mongo.db.accounts.find({'is_active': True}))
        
        # Categorize accounts
        assets = []
        liabilities = []
        
        for account in accounts:
            if account['type'] in ['bank_account', 'debit_card', 'cash', 'asset']:
                assets.append(account)
            elif account['type'] in ['credit_card', 'liability']:
                liabilities.append(account)
        
        total_assets = sum(a['balance'] for a in assets)
        total_liabilities = sum(abs(l['balance']) for l in liabilities if l['balance'] < 0)
        
        return {
            'as_of_date': as_of_date.isoformat(),
            'assets': {
                'total': total_assets,
                'accounts': [
                    {
                        'name': a['name'],
                        'balance': a['balance'],
                        'type': a['type']
                    }
                    for a in assets
                ]
            },
            'liabilities': {
                'total': total_liabilities,
                'accounts': [
                    {
                        'name': l['name'],
                        'balance': abs(l['balance']) if l['balance'] < 0 else l['balance'],
                        'type': l['type'],
                        'credit_limit': l.get('credit_limit'),
                        'due_date': l.get('due_date')
                    }
                    for l in liabilities
                ]
            },
            'net_worth': total_assets - total_liabilities
        }
    
    @staticmethod
    def generate_cash_flow(start_date, end_date):
        """Generate cash flow statement"""
        # Get all transactions
        transactions = list(mongo.db.transactions.find({
            'date': {'$gte': start_date, '$lte': end_date}
        }).sort('date', 1))
        
        # Initialize daily balances
        daily_flow = defaultdict(lambda: {'inflow': 0, 'outflow': 0, 'net': 0})
        
        for t in transactions:
            date_str = t['date'].strftime('%Y-%m-%d')
            
            if t['type'] == 'income':
                daily_flow[date_str]['inflow'] += t['amount']
                daily_flow[date_str]['net'] += t['amount']
            elif t['type'] == 'expense':
                daily_flow[date_str]['outflow'] += t['amount']
                daily_flow[date_str]['net'] -= t['amount']
            elif t['type'] == 'transfer':
                # Transfers don't affect net cash flow
                pass
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'daily': [
                {
                    'date': date,
                    'inflow': data['inflow'],
                    'outflow': data['outflow'],
                    'net': data['net']
                }
                for date, data in sorted(daily_flow.items())
            ],
            'summary': {
                'total_inflow': sum(d['inflow'] for d in daily_flow.values()),
                'total_outflow': sum(d['outflow'] for d in daily_flow.values()),
                'net_cash_flow': sum(d['net'] for d in daily_flow.values())
            }
        }
    
    @staticmethod
    def generate_category_analysis(start_date, end_date):
        """Generate category spending analysis"""
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
                    'total': {'$sum': '$amount'},
                    'count': {'$sum': 1},
                    'avg_amount': {'$avg': '$amount'},
                    'max_amount': {'$max': '$amount'},
                    'min_amount': {'$min': '$amount'}
                }
            },
            {
                '$sort': {'total': -1}
            }
        ]
        
        results = list(mongo.db.transactions.aggregate(pipeline))
        
        # Get category names and budgets
        categories = {}
        for r in results:
            category = mongo.db.categories.find_one({'_id': r['_id']})
            if category:
                budget = mongo.db.budgets.find_one({
                    'category_id': r['_id'],
                    'is_active': True
                })
                
                categories[r['_id']] = {
                    'name': category['name'],
                    'type': category['type'],
                    'budget': budget['amount'] if budget else None,
                    'spent': r['total'],
                    'remaining': (budget['amount'] - r['total']) if budget else None,
                    'progress': (r['total'] / budget['amount'] * 100) if budget else None,
                    'transaction_count': r['count'],
                    'average_amount': r['avg_amount'],
                    'max_amount': r['max_amount'],
                    'min_amount': r['min_amount']
                }
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'categories': list(categories.values()),
            'total_spent': sum(c['spent'] for c in categories.values()),
            'total_budget': sum(c['budget'] for c in categories.values() if c['budget']),
            'categories_with_budget': sum(1 for c in categories.values() if c['budget']),
            'categories_over_budget': sum(1 for c in categories.values() if c['progress'] and c['progress'] > 100)
        }