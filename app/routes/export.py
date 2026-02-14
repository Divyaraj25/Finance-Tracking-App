# app/routes/export.py
"""
Export functionality for Expense Tracker System
Version: 1.0.0
"""
from flask import Blueprint, request, jsonify, send_file, Response
from app.models import Transaction, Account, Category, Budget
from datetime import datetime
import csv
import json
import io
import pandas as pd
from bson import ObjectId
from app import mongo

export_bp = Blueprint('export', __name__)

@export_bp.route('/<format>')
def export_data(format):
    """Export data in specified format"""
    try:
        # Get data type
        data_type = request.args.get('type', 'transactions')
        
        # Get date range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = {}
        if start_date and end_date:
            try:
                query['date'] = {
                    '$gte': datetime.fromisoformat(start_date),
                    '$lte': datetime.fromisoformat(end_date)
                }
            except:
                pass
        
        # Fetch data based on type
        if data_type == 'transactions':
            data = fetch_transactions(query)
        elif data_type == 'accounts':
            data = fetch_accounts()
        elif data_type == 'budgets':
            data = fetch_budgets()
        elif data_type == 'categories':
            data = fetch_categories()
        elif data_type == 'all':
            data = fetch_all_data(query)
        else:
            return jsonify({'success': False, 'error': 'Invalid data type'}), 400
        
        # Check if data is empty
        if not data or (isinstance(data, list) and len(data) == 0) or (isinstance(data, dict) and all(len(v) == 0 for v in data.values() if isinstance(v, list))):
            return jsonify({'success': False, 'error': 'No data to export'}), 404
        
        # Export in requested format
        if format == 'csv':
            return export_csv(data, data_type)
        elif format == 'json':
            return export_json(data, data_type)
        elif format == 'excel':
            return export_excel(data, data_type)
        else:
            return jsonify({'success': False, 'error': 'Unsupported format'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
        
def fetch_transactions(query=None):
    """Fetch transactions data"""
    query = query or {}
    transactions = list(mongo.db.transactions.find(query).sort('date', -1))
    
    # Enhance with related data
    for t in transactions:
        t['_id'] = str(t['_id'])
        if 'category_id' in t:
            category = mongo.db.categories.find_one({'_id': ObjectId(t['category_id'])})
            t['category_name'] = category['name'] if category else 'Unknown'
        
        if 'from_account_id' in t:
            from_acc = mongo.db.accounts.find_one({'_id': ObjectId(t['from_account_id'])})
            t['from_account_name'] = from_acc['name'] if from_acc else 'Unknown'
        
        if 'to_account_id' in t:
            to_acc = mongo.db.accounts.find_one({'_id': ObjectId(t['to_account_id'])})
            t['to_account_name'] = to_acc['name'] if to_acc else 'Unknown'
    
    return transactions

def fetch_accounts():
    """Fetch accounts data"""
    accounts = list(mongo.db.accounts.find({'is_active': True}))
    for a in accounts:
        a['_id'] = str(a['_id'])
    return accounts

def fetch_budgets():
    """Fetch budgets data"""
    budgets = list(mongo.db.budgets.find({'is_active': True}))
    for b in budgets:
        b['_id'] = str(b['_id'])
        category = mongo.db.categories.find_one({'_id': ObjectId(b['category_id'])})
        b['category_name'] = category['name'] if category else 'Unknown'
    return budgets

def fetch_categories():
    """Fetch categories data"""
    categories = list(mongo.db.categories.find({'is_deleted': False}))
    for c in categories:
        c['_id'] = str(c['_id'])
    return categories

def fetch_all_data(query):
    """Fetch all data"""
    return {
        'transactions': fetch_transactions(query),
        'accounts': fetch_accounts(),
        'budgets': fetch_budgets(),
        'categories': fetch_categories(),
        'exported_at': datetime.now().isoformat()
    }

def export_csv(data, data_type):
    """Export data as CSV"""
    output = io.StringIO()
    
    if isinstance(data, list):
        if data:
            # Get all possible fieldnames from all items
            fieldnames = set()
            for item in data:
                fieldnames.update(item.keys())
            fieldnames = sorted(list(fieldnames))
            
            writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(data)
    else:
        # For 'all' data type, flatten structure
        flattened = []
        for key, items in data.items():
            if isinstance(items, list) and key != 'exported_at':
                for item in items:
                    item_copy = item.copy()
                    item_copy['_data_type'] = key
                    flattened.append(item_copy)
        
        if flattened:
            # Get all possible fieldnames
            fieldnames = set()
            for item in flattened:
                fieldnames.update(item.keys())
            fieldnames = sorted(list(fieldnames))
            
            writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(flattened)
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename={data_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        }
    )

def export_json(data, data_type):
    """Export data as JSON"""
    return Response(
        json.dumps(data, default=str, indent=2),
        mimetype='application/json',
        headers={
            'Content-Disposition': f'attachment; filename={data_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        }
    )

def export_excel(data, data_type):
    """Export data as Excel"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if isinstance(data, list):
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name=data_type.capitalize(), index=False)
        else:
            for key, items in data.items():
                if isinstance(items, list):
                    df = pd.DataFrame(items)
                    df.to_excel(writer, sheet_name=key.capitalize(), index=False)
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'{data_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

@export_bp.route('/formats')
def get_export_formats():
    """Get available export formats"""
    return jsonify({
        'success': True,
        'formats': ['csv', 'json', 'excel'],
        'data_types': ['transactions', 'accounts', 'budgets', 'categories', 'all']
    })