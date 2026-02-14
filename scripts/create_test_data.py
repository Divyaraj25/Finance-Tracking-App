#!/usr/bin/env python3
"""
Create comprehensive test data for development
Version: 1.0.0
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, mongo
from app.models import Account, Category, Transaction, Budget
from datetime import datetime, timedelta
import random
from bson import ObjectId

app = create_app('development')

def create_test_data():
    """Create comprehensive sample test data"""
    with app.app_context():
        print("\n" + "="*60)
        print("💰 CREATING COMPREHENSIVE TEST DATA")
        print("="*60)
        
        # Clear existing test data but keep defaults
        print("\n📦 Clearing existing test data...")
        mongo.db.accounts.delete_many({})
        mongo.db.transactions.delete_many({})
        mongo.db.budgets.delete_many({})
        
        # 1. CREATE ACCOUNTS
        print("\n🏦 Creating test accounts...")
        account_objects = create_accounts()
        
        # 2. GET CATEGORIES
        print("\n📁 Fetching categories...")
        categories = get_categories()
        
        # 3. CREATE TRANSACTIONS
        print("\n💳 Creating test transactions...")
        transactions = create_transactions(account_objects, categories)
        
        # 4. CREATE BUDGETS
        print("\n🎯 Creating test budgets...")
        budgets = create_budgets(categories)
        
        # 5. CREATE SYSTEM LOGS
        print("\n📋 Creating test logs...")
        create_logs()
        
        # 6. UPDATE ACCOUNT BALANCES
        print("\n💰 Updating account balances...")
        update_account_balances(account_objects)
        
        # 7. PRINT SUMMARY
        print_summary(account_objects, categories, transactions, budgets)
        
        print("\n" + "="*60)
        print("✅ TEST DATA CREATION COMPLETE!")
        print("="*60)

def create_accounts():
    """Create diverse test accounts"""
    account_objects = []
    
    account_data = [
        # Bank Accounts
        {"name": "Chase Checking", "type": "bank_account", "balance": 5432.10, 
         "currency": "USD", "description": "Primary checking account"},
        {"name": "Chase Savings", "type": "bank_account", "balance": 12500.00, 
         "currency": "USD", "description": "Emergency fund"},
        {"name": "Wells Fargo Checking", "type": "bank_account", "balance": 2345.67, 
         "currency": "USD", "description": "Joint account"},
        
        # Credit Cards
        {"name": "Chase Sapphire Preferred", "type": "credit_card", "balance": -1240.50, 
         "currency": "USD", "credit_limit": 10000.00, "due_date": "2026-03-15",
         "statement_balance": 1240.50, "description": "Travel rewards card"},
        {"name": "American Express Gold", "type": "credit_card", "balance": -856.75, 
         "currency": "USD", "credit_limit": 8000.00, "due_date": "2026-03-20",
         "statement_balance": 856.75, "description": "Dining rewards"},
        {"name": "Capital One Venture", "type": "credit_card", "balance": -2100.00, 
         "currency": "USD", "credit_limit": 15000.00, "due_date": "2026-03-25",
         "statement_balance": 2100.00, "description": "Miles card"},
        
        # Cash
        {"name": "Wallet Cash", "type": "cash", "balance": 350.00, 
         "currency": "USD", "description": "Physical cash"},
        {"name": "Home Safe", "type": "cash", "balance": 500.00, 
         "currency": "USD", "description": "Emergency cash"},
        
        # Assets
        {"name": "Vanguard 401k", "type": "asset", "balance": 45230.89, 
         "currency": "USD", "interest_rate": 7.2, "description": "Retirement account"},
        {"name": "Robinhood Investment", "type": "asset", "balance": 8900.00, 
         "currency": "USD", "description": "Stock portfolio"},
        {"name": "Tesla Model 3", "type": "asset", "balance": 35000.00, 
         "currency": "USD", "description": "2022 Tesla Model 3"},
        {"name": "Rental Property", "type": "asset", "balance": 250000.00, 
         "currency": "USD", "description": "Investment property"},
        
        # Liabilities
        {"name": "Mortgage", "type": "liability", "balance": -185000.00, 
         "currency": "USD", "interest_rate": 3.5, "description": "Home loan"},
        {"name": "Student Loan", "type": "liability", "balance": -12500.00, 
         "currency": "USD", "interest_rate": 4.2, "description": "Education debt"},
        {"name": "Car Loan", "type": "liability", "balance": -12000.00, 
         "currency": "USD", "interest_rate": 2.9, "description": "Tesla financing"},
        
        # Foreign Currency
        {"name": "Euro Travel Card", "type": "debit_card", "balance": 850.00, 
         "currency": "EUR", "description": "Travel money card"},
        {"name": "JPY Cash", "type": "cash", "balance": 50000.00, 
         "currency": "JPY", "description": "Japanese Yen from trip"},
    ]
    
    for acc_data in account_data:
        try:
            account_id = Account.create(acc_data)
            # Store both the ID and the full account data
            account_info = {'id': account_id, **acc_data}
            account_objects.append(account_info)
            print(f"  ✅ Created: {acc_data['name']} ({acc_data['type']}) - ${abs(acc_data['balance']):,.2f}")
        except Exception as e:
            print(f"  ❌ Failed: {acc_data['name']} - {e}")
    
    return account_objects

def get_categories():
    """Get all non-deleted categories"""
    categories = list(mongo.db.categories.find({'is_deleted': False}))
    
    # Group by type
    categories_by_type = {
        'expense': [],
        'income': [],
        'asset': [],
        'liability': []
    }
    
    for cat in categories:
        cat['id'] = str(cat['_id'])
        cat_type = cat['type']
        if cat_type in categories_by_type:
            categories_by_type[cat_type].append(cat)
    
    # Print counts
    for cat_type, cats in categories_by_type.items():
        print(f"  📊 {cat_type.title()}: {len(cats)} categories")
    
    return categories_by_type

def create_transactions(account_objects, categories):
    """Create realistic test transactions for the last 90 days"""
    transactions = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    expense_categories = categories['expense']
    income_categories = categories['income']
    asset_categories = categories['asset']
    liability_categories = categories['liability']
    
    # Get account IDs by type
    bank_accounts = [a['id'] for a in account_objects if a['type'] in ['bank_account', 'debit_card']]
    credit_cards = [a['id'] for a in account_objects if a['type'] == 'credit_card']
    cash_accounts = [a['id'] for a in account_objects if a['type'] == 'cash']
    asset_accounts = [a['id'] for a in account_objects if a['type'] == 'asset']
    
    print(f"    📊 Bank accounts: {len(bank_accounts)}")
    print(f"    📊 Credit cards: {len(credit_cards)}")
    print(f"    📊 Cash accounts: {len(cash_accounts)}")
    print(f"    📊 Asset accounts: {len(asset_accounts)}")
    
    # 1. REGULAR EXPENSES (60 transactions)
    print("  🛒 Creating regular expenses...")
    expense_templates = [
        {"desc": "Grocery shopping at {store}", "store": ["Walmart", "Kroger", "Safeway", "Whole Foods", "Trader Joe's", "Costco"]},
        {"desc": "Dinner at {restaurant}", "restaurant": ["Olive Garden", "Chipotle", "P.F. Chang's", "Local Bistro", "Sushi House"]},
        {"desc": "Coffee at {shop}", "shop": ["Starbucks", "Dunkin", "Peet's", "Local Cafe"]},
        {"desc": "Gas at {station}", "station": ["Shell", "Chevron", "Exxon", "BP"]},
        {"desc": "Uber ride", "static": True},
        {"desc": "Amazon purchase", "static": True},
        {"desc": "Target shopping", "static": True},
        {"desc": "Netflix subscription", "static": True},
        {"desc": "Spotify premium", "static": True},
        {"desc": "Gym membership", "static": True},
    ]
    
    for i in range(60):
        date = start_date + timedelta(days=random.randint(0, 90))
        template = random.choice(expense_templates)
        
        # Generate description
        if template.get('static'):
            description = template['desc']
        else:
            # FIXED: Get the key dynamically
            for key in template.keys():
                if key not in ['desc', 'static']:
                    value = random.choice(template[key])
                    description = template['desc'].format(**{key: value})
                    break
        
        # Random amount between $5 and $200
        amount = round(random.uniform(5, 200), 2)
        
        # Random account (70% credit card, 30% bank/cash)
        if credit_cards and random.random() < 0.7:
            from_account = random.choice(credit_cards)
        elif bank_accounts:
            from_account = random.choice(bank_accounts)
        elif cash_accounts:
            from_account = random.choice(cash_accounts)
        else:
            continue
            
        # Get random expense category
        if expense_categories:
            category = random.choice(expense_categories)
            category_id = category['id']
        else:
            category_id = None
        
        transaction = {
            'date': date,
            'description': description,
            'amount': amount,
            'type': 'expense',
            'category_id': category_id,
            'from_account_id': from_account,
            'to_account_id': None,
            'tags': random.sample(['groceries', 'dining', 'transport', 'shopping', 'bills', 'entertainment'], 
                                 k=random.randint(0, 3)),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'is_reconciled': random.choice([True, False])
        }
        
        Transaction.create(transaction)
        transactions.append(transaction)
        
        if (i + 1) % 20 == 0:
            print(f"    ✅ Created {i + 1} expenses")
    
    # 2. INCOME TRANSACTIONS (15 transactions)
    print("  💵 Creating income transactions...")
    income_templates = [
        {"desc": "Salary - {month}", "month": ["January", "February", "March"]},
        {"desc": "Freelance project - {client}", "client": ["TechCorp", "DesignStudio", "Consulting LLC"]},
        {"desc": "Dividend payment", "static": True},
        {"desc": "Tax refund", "static": True},
        {"desc": "Gift from family", "static": True},
        {"desc": "Bonus payment", "static": True},
    ]
    
    for i in range(15):
        date = start_date + timedelta(days=random.randint(0, 90))
        template = random.choice(income_templates)
        
        if template.get('static'):
            description = template['desc']
        else:
            # FIXED: Get the key dynamically
            for key in template.keys():
                if key not in ['desc', 'static']:
                    value = random.choice(template[key])
                    description = template['desc'].format(**{key: value})
                    break
        
        amount = round(random.uniform(500, 5000), 2)
        
        # Get random income category
        if income_categories:
            category = random.choice(income_categories)
            category_id = category['id']
        else:
            category_id = None
        
        if bank_accounts:
            transaction = {
                'date': date,
                'description': description,
                'amount': amount,
                'type': 'income',
                'category_id': category_id,
                'from_account_id': None,
                'to_account_id': random.choice(bank_accounts),
                'tags': ['income', 'salary'] if 'Salary' in description else ['freelance'],
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'is_reconciled': random.choice([True, False])
            }
            
            Transaction.create(transaction)
            transactions.append(transaction)
        
        if (i + 1) % 5 == 0:
            print(f"    ✅ Created {i + 1} incomes")
    
    # 3. TRANSFERS (10 transactions)
    print("  🔄 Creating transfer transactions...")
    for i in range(10):
        date = start_date + timedelta(days=random.randint(0, 90))
        amount = round(random.uniform(100, 1000), 2)
        
        if len(bank_accounts) >= 2:
            from_account = random.choice(bank_accounts)
            to_account = random.choice([a for a in bank_accounts if a != from_account])
            
            transaction = {
                'date': date,
                'description': f"Transfer between accounts",
                'amount': amount,
                'type': 'transfer',
                'category_id': None,
                'from_account_id': from_account,
                'to_account_id': to_account,
                'tags': ['transfer'],
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'is_reconciled': random.choice([True, False])
            }
            
            Transaction.create(transaction)
            transactions.append(transaction)
    
    # 4. CREDIT CARD PAYMENTS (8 transactions)
    print("  💳 Creating credit card payments...")
    credit_card_bill_category = None
    for cat in liability_categories:
        if 'Credit Card Bill' in cat['name']:
            credit_card_bill_category = cat['id']
            break
    
    for i in range(8):
        date = end_date - timedelta(days=random.randint(1, 30))
        amount = round(random.uniform(200, 1000), 2)
        
        if bank_accounts and credit_cards:
            transaction = {
                'date': date,
                'description': f"Credit card payment",
                'amount': amount,
                'type': 'credit_card_payment',
                'category_id': credit_card_bill_category,
                'from_account_id': random.choice(bank_accounts),
                'to_account_id': random.choice(credit_cards),
                'tags': ['payment', 'credit card'],
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'is_reconciled': random.choice([True, False])
            }
            
            Transaction.create(transaction)
            transactions.append(transaction)
    
    # 5. ASSET PURCHASES (5 transactions)
    print("  🏢 Creating asset purchases...")
    for i in range(5):
        date = start_date + timedelta(days=random.randint(0, 90))
        amount = round(random.uniform(1000, 10000), 2)
        
        if bank_accounts and asset_accounts and asset_categories:
            # Get random asset category
            category = random.choice(asset_categories)
            category_id = category['id']
                
            transaction = {
                'date': date,
                'description': f"Investment purchase",
                'amount': amount,
                'type': 'asset_purchase',
                'category_id': category_id,
                'from_account_id': random.choice(bank_accounts),
                'to_account_id': random.choice(asset_accounts),
                'tags': ['investment'],
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'is_reconciled': random.choice([True, False])
            }
            
            Transaction.create(transaction)
            transactions.append(transaction)
    
    print(f"  ✅ Total transactions created: {len(transactions)}")
    return transactions

def create_budgets(categories):
    """Create realistic test budgets"""
    budgets = []
    expense_categories = categories['expense']
    
    budget_templates = [
        {"category_name": "Food & Dining", "amount": 600, "period": "monthly"},
        {"category_name": "Transportation", "amount": 200, "period": "monthly"},
        {"category_name": "Entertainment", "amount": 150, "period": "monthly"},
        {"category_name": "Shopping", "amount": 300, "period": "monthly"},
        {"category_name": "Utilities", "amount": 250, "period": "monthly"},
        {"category_name": "Healthcare", "amount": 100, "period": "monthly"},
        {"category_name": "Personal Care", "amount": 80, "period": "monthly"},
    ]
    
    for template in budget_templates:
        # Find category by name
        category = None
        for cat in expense_categories:
            if cat['name'] == template['category_name']:
                category = cat
                break
        
        if category:
            # Check if budget already exists
            existing = mongo.db.budgets.find_one({
                'category_id': category['id'],
                'is_active': True
            })
            
            if not existing:
                budget_data = {
                    'category_id': category['id'],
                    'amount': template['amount'],
                    'period': template['period']
                }
                
                try:
                    budget_id = Budget.create(budget_data)
                    budgets.append(budget_id)
                    print(f"  ✅ Created budget: {category['name']} - ${template['amount']}/{template['period']}")
                except Exception as e:
                    print(f"  ❌ Failed budget for {category['name']}: {e}")
    
    return budgets

def create_logs():
    """Create test system logs"""
    log_levels = ['SUCCESS', 'INFO', 'WARNING', 'ERROR', 'AUDIT']
    log_categories = ['SYSTEM', 'ACCOUNT', 'TRANSACTION', 'BUDGET', 'CATEGORY', 'API', 'AUTH']
    
    for i in range(50):
        date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        log_entry = {
            'timestamp': date,
            'level': random.choice(log_levels),
            'category': random.choice(log_categories),
            'message': f"Test log entry {i+1}",
            'details': {
                'test_id': i+1,
                'source': 'create_test_data.py'
            }
        }
        
        mongo.db.logs.insert_one(log_entry)
    
    print(f"  ✅ Created 50 test log entries")

def update_account_balances(account_objects):
    """Recalculate and update account balances based on transactions"""
    for account in account_objects:
        account_id = account['id']
        
        # Calculate inflows
        inflow = mongo.db.transactions.aggregate([
            {'$match': {'to_account_id': account_id}},
            {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
        ])
        inflow_total = list(inflow)
        inflow_amount = inflow_total[0]['total'] if inflow_total else 0
        
        # Calculate outflows
        outflow = mongo.db.transactions.aggregate([
            {'$match': {'from_account_id': account_id}},
            {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
        ])
        outflow_total = list(outflow)
        outflow_amount = outflow_total[0]['total'] if outflow_total else 0
        
        # Calculate credit card payments (special handling)
        cc_payments = mongo.db.transactions.aggregate([
            {'$match': {
                'to_account_id': account_id,
                'type': 'credit_card_payment'
            }},
            {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
        ])
        cc_payments_total = list(cc_payments)
        cc_payment_amount = cc_payments_total[0]['total'] if cc_payments_total else 0
        
        # For credit cards: payments increase balance (make less negative)
        if account['type'] == 'credit_card':
            new_balance = account['balance'] + cc_payment_amount - outflow_amount + inflow_amount
        else:
            new_balance = account['balance'] + inflow_amount - outflow_amount
        
        mongo.db.accounts.update_one(
            {'_id': ObjectId(account_id)},
            {'$set': {'balance': new_balance}}
        )

def print_summary(account_objects, categories, transactions, budgets):
    """Print comprehensive summary of created test data"""
    print("\n" + "="*60)
    print("📊 TEST DATA SUMMARY")
    print("="*60)
    
    # Accounts summary
    print("\n🏦 ACCOUNTS:")
    print(f"  Total Accounts: {len(account_objects)}")
    
    account_types = {}
    for acc in account_objects:
        acc_type = acc['type']
        account_types[acc_type] = account_types.get(acc_type, 0) + 1
    
    for acc_type, count in account_types.items():
        print(f"    {acc_type.replace('_', ' ').title()}: {count}")
    
    # Transactions summary
    print("\n💰 TRANSACTIONS:")
    total_transactions = mongo.db.transactions.count_documents({})
    print(f"  Total Transactions: {total_transactions}")
    
    tx_types = mongo.db.transactions.aggregate([
        {'$group': {'_id': '$type', 'count': {'$sum': 1}}}
    ])
    
    for tx in tx_types:
        print(f"    {tx['_id'].replace('_', ' ').title()}: {tx['count']}")
    
    # Budgets summary
    print("\n🎯 BUDGETS:")
    total_budgets = mongo.db.budgets.count_documents({'is_active': True})
    print(f"  Active Budgets: {total_budgets}")
    
    # Financial summary
    print("\n💵 FINANCIAL SUMMARY:")
    
    # Total assets
    assets = mongo.db.accounts.aggregate([
        {'$match': {'type': {'$in': ['bank_account', 'debit_card', 'cash', 'asset']}, 'is_active': True}},
        {'$group': {'_id': None, 'total': {'$sum': '$balance'}}}
    ])
    total_assets = list(assets)
    total_assets_value = total_assets[0]['total'] if total_assets else 0
    
    # Total liabilities
    liabilities = mongo.db.accounts.aggregate([
        {'$match': {'type': {'$in': ['credit_card', 'liability']}, 'is_active': True}},
        {'$group': {'_id': None, 'total': {'$sum': '$balance'}}}
    ])
    total_liabilities = list(liabilities)
    total_liabilities_value = abs(total_liabilities[0]['total']) if total_liabilities else 0
    
    net_worth = total_assets_value - total_liabilities_value
    
    print(f"  Total Assets:     ${total_assets_value:>12,.2f}")
    print(f"  Total Liabilities: ${total_liabilities_value:>12,.2f}")
    print(f"  Net Worth:        ${net_worth:>12,.2f}")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    create_test_data()