# app/utils/validators.py
"""
Input validation utilities
Version: 1.0.0
"""
import re
from datetime import datetime
from bson import ObjectId

def validate_email(email):
    """Validate email address"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_amount(amount):
    """Validate transaction amount"""
    try:
        amount = float(amount)
        return amount > 0
    except (ValueError, TypeError):
        return False

def validate_date(date_string):
    """Validate date string"""
    try:
        datetime.fromisoformat(date_string)
        return True
    except (ValueError, TypeError):
        return False

def validate_object_id(id_string):
    """Validate MongoDB ObjectId"""
    try:
        ObjectId(id_string)
        return True
    except:
        return False

def validate_account_type(account_type):
    """Validate account type"""
    valid_types = ['bank_account', 'credit_card', 'debit_card', 'cash', 'asset', 'liability']
    return account_type in valid_types

def validate_transaction_type(transaction_type):
    """Validate transaction type"""
    valid_types = ['income', 'expense', 'transfer', 'asset_purchase', 'liability_payment', 'credit_card_payment']
    return transaction_type in valid_types

def validate_budget_period(period):
    """Validate budget period"""
    valid_periods = ['weekly', 'monthly', 'yearly']
    return period in valid_periods

def validate_currency(currency):
    """Validate currency code"""
    valid_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'INR', 'CAD', 'AUD', 'CHF', 'CNY', 'NZD']
    return currency.upper() in valid_currencies

def validate_tags(tags):
    """Validate tags"""
    if not tags:
        return True
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',')]
    return isinstance(tags, list) and all(isinstance(t, str) for t in tags)

def sanitize_string(input_string):
    """Sanitize string input"""
    if not input_string:
        return ''
    # Remove dangerous characters
    sanitized = re.sub(r'[<>&\'"]', '', input_string)
    return sanitized.strip()