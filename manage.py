#!/usr/bin/env python3
"""
Management script for Expense Tracker System
Version: 1.1.0
"""
import click
from flask.cli import FlaskGroup
from app import create_app, mongo
from app.models import Category, Account, Transaction, Budget, Log
from datetime import datetime, timedelta
import json
import random
from bson import ObjectId
import sys

app = create_app()

@click.group(cls=FlaskGroup, create_app=lambda: app)
def cli():
    """Management script for Expense Tracker System"""
    pass

@cli.command('init-db')
def init_db():
    """Initialize database with default data and indexes"""
    click.echo('🚀 Initializing database...')
    
    with app.app_context():
        try:
            # Test MongoDB connection
            mongo.db.command('ping')
            click.echo('  ✅ MongoDB connected')
            
            # CRITICAL: Create database if it doesn't exist
            # This forces MongoDB to create the database
            if 'expense_tracker' not in mongo.cx.list_database_names():
                click.echo('  📁 Creating expense_tracker database...')
                # Insert a dummy document to create the database
                mongo.db.initialize.insert_one({'created_at': datetime.now()})
                mongo.db.initialize.drop()  # Remove the dummy collection
                click.echo('  ✅ Database created')
            
        except Exception as e:
            click.echo(f'  ❌ MongoDB connection failed: {e}')
            click.echo('  ⚠️  Please make sure:')
            click.echo('     1. MongoDB is running (mongod --dbpath ./data)')
            click.echo('     2. Your .env file has correct MONGO_URI')
            click.echo('     3. Port 27017 is not blocked')
            sys.exit(1)
    
    # Only proceed if MongoDB is connected
    click.echo('  📊 Creating indexes...')
    create_indexes()
    
    click.echo('  📁 Creating default categories...')
    create_default_categories()
    
    click.echo('  ⚙️ Creating system settings...')
    create_system_settings()
    
    click.echo('✅ Database initialization complete!')

def create_indexes():
    """Create all database indexes"""
    click.echo('  📊 Creating indexes...')
    
    # Transactions indexes
    mongo.db.transactions.create_index('date')
    mongo.db.transactions.create_index('category_id')
    mongo.db.transactions.create_index('from_account_id')
    mongo.db.transactions.create_index('to_account_id')
    mongo.db.transactions.create_index('type')
    mongo.db.transactions.create_index([('date', -1)])
    
    # Accounts indexes
    mongo.db.accounts.create_index('name', unique=True)
    mongo.db.accounts.create_index('type')
    mongo.db.accounts.create_index('is_active')
    
    # Categories indexes
    mongo.db.categories.create_index('name', unique=True)
    mongo.db.categories.create_index('type')
    mongo.db.categories.create_index('is_deleted')
    mongo.db.categories.create_index('is_default')
    
    # Budgets indexes
    mongo.db.budgets.create_index('category_id')
    mongo.db.budgets.create_index('period')
    mongo.db.budgets.create_index('is_active')
    mongo.db.budgets.create_index([('start_date', 1), ('end_date', 1)])
    
    # Logs indexes
    mongo.db.logs.create_index('timestamp')
    mongo.db.logs.create_index('level')
    mongo.db.logs.create_index('category')
    mongo.db.logs.create_index([('timestamp', -1)])
    
    # Settings indexes
    mongo.db.settings.create_index('key', unique=True)
    
    click.echo('  ✅ Indexes created')

def create_default_categories():
    """Create default categories"""
    click.echo('  📁 Creating default categories...')
    
    default_categories = [
        # Expense categories
        {"name": "Uncategorized Expense", "type": "expense", "is_default": True, 
         "description": "Default category for uncategorized expenses"},
        {"name": "Food & Dining", "type": "expense", "is_default": False,
         "description": "Restaurants, cafes, grocery shopping, food delivery"},
        {"name": "Transportation", "type": "expense", "is_default": False,
         "description": "Fuel, public transport, parking, ride sharing, vehicle maintenance"},
        {"name": "Utilities", "type": "expense", "is_default": False,
         "description": "Electricity, water, gas, internet, phone, streaming services"},
        {"name": "Entertainment", "type": "expense", "is_default": False,
         "description": "Movies, games, concerts, hobbies, sports"},
        {"name": "Shopping", "type": "expense", "is_default": False,
         "description": "Clothing, electronics, home goods, online shopping"},
        {"name": "Healthcare", "type": "expense", "is_default": False,
         "description": "Doctor visits, medications, insurance, fitness"},
        {"name": "Education", "type": "expense", "is_default": False,
         "description": "Tuition, books, courses, training"},
        {"name": "Housing", "type": "expense", "is_default": False,
         "description": "Rent, mortgage, property tax, maintenance, furniture"},
        {"name": "Personal Care", "type": "expense", "is_default": False,
         "description": "Haircuts, spa, cosmetics, grooming"},
        {"name": "Gifts & Donations", "type": "expense", "is_default": False,
         "description": "Birthday gifts, charity donations, wedding gifts"},
        {"name": "Travel", "type": "expense", "is_default": False,
         "description": "Flights, hotels, vacation rentals, activities"},
        {"name": "Insurance", "type": "expense", "is_default": False,
         "description": "Health, auto, home, life insurance premiums"},
        {"name": "Taxes", "type": "expense", "is_default": False,
         "description": "Income tax, property tax, sales tax"},
        
        # Income categories
        {"name": "Uncategorized Income", "type": "income", "is_default": True,
         "description": "Default category for uncategorized income"},
        {"name": "Salary", "type": "income", "is_default": False,
         "description": "Regular employment income, wages, bonuses"},
        {"name": "Freelance", "type": "income", "is_default": False,
         "description": "Contract work, consulting, gig economy"},
        {"name": "Business", "type": "income", "is_default": False,
         "description": "Business revenue, sales, services"},
        {"name": "Investment", "type": "income", "is_default": False,
         "description": "Dividends, interest, capital gains"},
        {"name": "Rental", "type": "income", "is_default": False,
         "description": "Property rental income"},
        {"name": "Refund", "type": "income", "is_default": False,
         "description": "Tax refunds, product returns, reimbursements"},
        {"name": "Gift", "type": "income", "is_default": False,
         "description": "Monetary gifts, inheritance"},
        
        # Asset categories
        {"name": "Uncategorized Asset", "type": "asset", "is_default": True,
         "description": "Default category for assets"},
        {"name": "Stocks", "type": "asset", "is_default": False,
         "description": "Equity investments, shares"},
        {"name": "Bonds", "type": "asset", "is_default": False,
         "description": "Fixed income investments"},
        {"name": "Real Estate", "type": "asset", "is_default": False,
         "description": "Property, land, buildings"},
        {"name": "Cryptocurrency", "type": "asset", "is_default": False,
         "description": "Bitcoin, Ethereum, other crypto"},
        {"name": "Vehicle", "type": "asset", "is_default": False,
         "description": "Cars, motorcycles, boats"},
        {"name": "Precious Metals", "type": "asset", "is_default": False,
         "description": "Gold, silver, platinum"},
        {"name": "Retirement", "type": "asset", "is_default": False,
         "description": "401k, IRA, pension funds"},
        
        # Liability categories
        {"name": "Uncategorized Liability", "type": "liability", "is_default": True,
         "description": "Default category for liabilities"},
        {"name": "Credit Card Bill", "type": "liability", "is_default": False,
         "description": "Credit card statement payments"},
        {"name": "Mortgage", "type": "liability", "is_default": False,
         "description": "Home loan payments"},
        {"name": "Student Loan", "type": "liability", "is_default": False,
         "description": "Education debt"},
        {"name": "Personal Loan", "type": "liability", "is_default": False,
         "description": "Loans from individuals or banks"},
        {"name": "Auto Loan", "type": "liability", "is_default": False,
         "description": "Vehicle financing"},
        {"name": "Medical Debt", "type": "liability", "is_default": False,
         "description": "Healthcare related debt"},
        {"name": "Tax Liability", "type": "liability", "is_default": False,
         "description": "Taxes owed"}
    ]
    
    count = 0
    for cat_data in default_categories:
        existing = mongo.db.categories.find_one({'name': cat_data['name']})
        if not existing:
            cat_data['created_at'] = datetime.now()
            cat_data['updated_at'] = datetime.now()
            cat_data['is_deleted'] = False
            mongo.db.categories.insert_one(cat_data)
            count += 1
            click.echo(f'    ✅ Created: {cat_data["name"]}')
    
    click.echo(f'  ✅ Created {count} default categories')

def create_system_settings():
    """Create default system settings"""
    click.echo('  ⚙️ Creating system settings...')
    
    default_settings = [
        # Application settings
        {'key': 'app_name', 'value': 'Expense Tracker System'},
        {'key': 'app_version', 'value': '1.1.0'},
        {'key': 'company_name', 'value': 'ExpenseTracker'},
        {'key': 'company_year', 'value': '2026'},
        
        # User preferences
        {'key': 'currency', 'value': 'USD'},
        {'key': 'date_format', 'value': 'YYYY-MM-DD'},
        {'key': 'time_format', 'value': '24h'},
        {'key': 'theme', 'value': 'light'},
        {'key': 'items_per_page', 'value': 20},
        {'key': 'notifications_enabled', 'value': True},
        
        # NEW: Timezone and regional settings
        {'key': 'timezone', 'value': 'local'},
        {'key': 'week_start', 'value': 'monday'},
        {'key': 'number_format', 'value': '1,234.56'},
        {'key': 'first_day', 'value': '1'},  # 0=Sunday, 1=Monday, 6=Saturday
        
        # Export settings
        {'key': 'export_format', 'value': 'csv'},
        
        # Default categories
        {'key': 'default_income_category', 'value': 'Uncategorized Income'},
        {'key': 'default_expense_category', 'value': 'Uncategorized Expense'},
        
        # System settings
        {'key': 'first_run', 'value': True},
        {'key': 'setup_complete', 'value': True},
        {'key': 'db_initialized', 'value': datetime.now().isoformat()},
        {'key': 'version', 'value': '1.1.0'}
    ]
    
    count = 0
    for setting in default_settings:
        existing = mongo.db.settings.find_one({'key': setting['key']})
        if not existing:
            setting['created_at'] = datetime.now()
            setting['updated_at'] = datetime.now()
            mongo.db.settings.insert_one(setting)
            count += 1
            click.echo(f'    ✅ Created setting: {setting["key"]}')
    
    click.echo(f'  ✅ Created {count} system settings')

@cli.command('reset-db')
@click.confirmation_option(prompt='⚠️  Are you sure you want to reset the database? This will DELETE ALL DATA!')
def reset_db():
    """Reset the database (delete all collections)"""
    click.echo('🔥 Resetting database...')
    
    collections = ['transactions', 'accounts', 'categories', 'budgets', 'logs', 'settings']
    for collection in collections:
        result = mongo.db[collection].delete_many({})
        click.echo(f'  ✅ Cleared {collection}: {result.deleted_count} documents')
    
    click.echo('✅ Database reset complete!')

@cli.command('backup')
def backup_db():
    """Backup database to JSON file"""
    click.echo('💾 Creating database backup...')
    
    backup_data = {}
    collections = ['transactions', 'accounts', 'categories', 'budgets', 'logs', 'settings']
    
    for collection in collections:
        cursor = mongo.db[collection].find({})
        backup_data[collection] = list(cursor)
        click.echo(f'  ✅ Backed up {collection}: {len(backup_data[collection])} documents')
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'backups/backup_{timestamp}.json'
    
    # Ensure backups directory exists
    import os
    os.makedirs('backups', exist_ok=True)
    
    with open(filename, 'w') as f:
        json.dump(backup_data, f, default=str, indent=2)
    
    click.echo(f'✅ Backup saved to: {filename}')

@cli.command('restore')
@click.argument('filename')
def restore_db(filename):
    """Restore database from backup file"""
    click.echo(f'🔄 Restoring database from: {filename}')
    
    try:
        with open(filename, 'r') as f:
            backup_data = json.load(f)
        
        for collection_name, documents in backup_data.items():
            if documents:
                # Convert string dates back to datetime
                for doc in documents:
                    for key, value in doc.items():
                        if key in ['date', 'created_at', 'updated_at', 'timestamp', 'start_date', 'end_date']:
                            if value:
                                try:
                                    doc[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                                except:
                                    pass
                
                mongo.db[collection_name].delete_many({})
                result = mongo.db[collection_name].insert_many(documents)
                click.echo(f'  ✅ Restored {len(result.inserted_ids)} documents to {collection_name}')
        
        click.echo('✅ Database restore complete!')
    except FileNotFoundError:
        click.echo(f'❌ Backup file not found: {filename}')
    except Exception as e:
        click.echo(f'❌ Restore failed: {e}')

@cli.command('export-categories')
def export_categories():
    """Export categories to CSV"""
    import csv
    
    categories = list(mongo.db.categories.find({'is_deleted': False}))
    
    with open('backups/categories_export.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Type', 'Description', 'Is Default', 'Created At'])
        
        for cat in categories:
            writer.writerow([
                cat['name'],
                cat['type'],
                cat.get('description', ''),
                cat.get('is_default', False),
                cat.get('created_at', '')
            ])
    
    click.echo('✅ Categories exported to backups/categories_export.csv')

@cli.command('stats')
def show_stats():
    """Show database statistics"""
    click.echo('📊 Database Statistics:')
    click.echo('  ' + '=' * 40)
    
    stats = {
        'Accounts': mongo.db.accounts.count_documents({'is_active': True}),
        'Categories': mongo.db.categories.count_documents({'is_deleted': False}),
        'Transactions': mongo.db.transactions.count_documents({}),
        'Budgets': mongo.db.budgets.count_documents({'is_active': True}),
        'Logs': mongo.db.logs.count_documents({})
    }
    
    for name, count in stats.items():
        click.echo(f'  {name:15}: {count:6,}')
    
    click.echo('  ' + '=' * 40)
    
    # Account balance total
    total_balance = mongo.db.accounts.aggregate([
        {'$match': {'is_active': True}},
        {'$group': {'_id': None, 'total': {'$sum': '$balance'}}}
    ])
    total = list(total_balance)
    if total:
        click.echo(f'  Total Balance : ${total[0]["total"]:,.2f}')

@cli.command('update-settings')
def update_settings():
    """Update existing settings with new default values"""
    click.echo('🔄 Updating settings with new defaults...')
    
    new_settings = [
        {'key': 'timezone', 'value': 'local'},
        {'key': 'week_start', 'value': 'monday'},
        {'key': 'number_format', 'value': '1,234.56'},
        {'key': 'first_day', 'value': '1'},
        {'key': 'version', 'value': '1.1.0'}
    ]
    
    count = 0
    for setting in new_settings:
        existing = mongo.db.settings.find_one({'key': setting['key']})
        if not existing:
            setting['created_at'] = datetime.now()
            setting['updated_at'] = datetime.now()
            mongo.db.settings.insert_one(setting)
            count += 1
            click.echo(f'  ✅ Added: {setting["key"]} = {setting["value"]}')
        else:
            click.echo(f'  ⏭️  Skipped: {setting["key"]} already exists')
    
    click.echo(f'✅ Added {count} new settings')

if __name__ == '__main__':
    cli()