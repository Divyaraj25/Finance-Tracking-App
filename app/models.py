"""
Database models for Expense Tracker System
Version: 1.0.0
"""
from datetime import datetime
from bson import ObjectId
from flask import current_app
from app import mongo

class BaseModel:
    """Base model with common methods"""
    
    @staticmethod
    def get_db():
        """Get database instance with error handling"""
        if mongo.db is None:
            raise Exception("MongoDB not connected. Run 'python manage.py init-db' first.")
        return mongo.db
    
    @staticmethod
    def to_dict(obj):
        """Convert MongoDB document to dict"""
        if obj and '_id' in obj:
            obj['id'] = str(obj['_id'])
            del obj['_id']
        return obj
    
    @staticmethod
    def to_list(cursor):
        """Convert cursor to list of dicts"""
        return [BaseModel.to_dict(doc) for doc in cursor]

class Transaction(BaseModel):
    """Transaction model"""
    
    @classmethod
    @property
    def collection(cls):
        return BaseModel.get_db().transactions
    
    @classmethod
    def create(cls, data):
        """Create new transaction"""
        # Ensure date is timezone-aware UTC
        if 'date' in data and isinstance(data['date'], datetime):
            if data['date'].tzinfo is None:
                import pytz
                data['date'] = pytz.UTC.localize(data['date'])
        
        data['created_at'] = datetime.now(pytz.UTC)
        data['updated_at'] = datetime.now(pytz.UTC)
        data['is_reconciled'] = data.get('is_reconciled', False)
        
        result = cls.collection.insert_one(data)
        return str(result.inserted_id)
    
    @classmethod
    def update(cls, transaction_id, data):
        """Update transaction"""
        # Ensure date is timezone-aware UTC if being updated
        if 'date' in data and isinstance(data['date'], datetime):
            if data['date'].tzinfo is None:
                import pytz
                data['date'] = pytz.UTC.localize(data['date'])
        
        data['updated_at'] = datetime.now(pytz.UTC)
        result = cls.collection.update_one(
            {'_id': ObjectId(transaction_id)},
            {'$set': data}
        )
        return result.modified_count > 0
    
    @classmethod
    def delete(cls, transaction_id):
        """Delete transaction"""
        result = cls.collection.delete_one({'_id': ObjectId(transaction_id)})
        return result.deleted_count > 0
    
    @classmethod
    def get_by_id(cls, transaction_id):
        """Get transaction by ID"""
        return cls.collection.find_one({'_id': ObjectId(transaction_id)})
    
    @classmethod
    def get_all(cls, filters=None, page=1, per_page=20):
        """Get all transactions with filters"""
        query = filters or {}
        skip = (page - 1) * per_page
        
        cursor = cls.collection.find(query).sort('date', -1).skip(skip).limit(per_page)
        total = cls.collection.count_documents(query)
        
        return {
            'items': cls.to_list(cursor),
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }

class Account(BaseModel):
    """Account model"""
    
    @classmethod
    @property
    def collection(cls):
        return BaseModel.get_db().accounts
    
    @classmethod
    def create(cls, data):
        """Create new account"""
        data['created_at'] = datetime.now()
        data['updated_at'] = datetime.now()
        data['is_active'] = data.get('is_active', True)
        
        result = cls.collection.insert_one(data)
        return str(result.inserted_id)
    
    @classmethod
    def update(cls, account_id, data):
        """Update account"""
        data['updated_at'] = datetime.now()
        result = cls.collection.update_one(
            {'_id': ObjectId(account_id)},
            {'$set': data}
        )
        return result.modified_count > 0
    
    @classmethod
    def delete(cls, account_id):
        """Delete account (soft delete)"""
        result = cls.collection.update_one(
            {'_id': ObjectId(account_id)},
            {'$set': {'is_active': False, 'updated_at': datetime.now()}}
        )
        return result.modified_count > 0
    
    @classmethod
    def get_by_id(cls, account_id):
        """Get account by ID"""
        return cls.collection.find_one({'_id': ObjectId(account_id)})
    
    @classmethod
    def get_balance(cls, account_id):
        """Get current balance of account"""
        account = cls.get_by_id(account_id)
        return account.get('balance', 0) if account else 0

class Category(BaseModel):
    """Category model"""
    
    @classmethod
    @property
    def collection(cls):
        return BaseModel.get_db().categories
    
    @classmethod
    def create(cls, data):
        """Create new category"""
        data['created_at'] = datetime.now()
        data['updated_at'] = datetime.now()
        data['is_default'] = data.get('is_default', False)
        data['is_deleted'] = False
        
        result = cls.collection.insert_one(data)
        return str(result.inserted_id)
    
    @classmethod
    def update(cls, category_id, data):
        """Update category"""
        data['updated_at'] = datetime.now()
        result = cls.collection.update_one(
            {'_id': ObjectId(category_id)},
            {'$set': data}
        )
        return result.modified_count > 0
    
    @classmethod
    def get_by_id(cls, category_id):
        """Get category by ID"""
        return cls.collection.find_one({'_id': ObjectId(category_id)})

class Budget(BaseModel):
    """Budget model"""
    
    @classmethod
    @property
    def collection(cls):
        return BaseModel.get_db().budgets
    
    @classmethod
    def create(cls, data):
        """Create new budget"""
        data['created_at'] = datetime.now()
        data['updated_at'] = datetime.now()
        data['spent'] = 0
        data['is_active'] = True
        
        result = cls.collection.insert_one(data)
        return str(result.inserted_id)
    
    @classmethod
    def update(cls, budget_id, data):
        """Update budget"""
        data['updated_at'] = datetime.now()
        result = cls.collection.update_one(
            {'_id': ObjectId(budget_id)},
            {'$set': data}
        )
        return result.modified_count > 0
    
    @classmethod
    def get_by_id(cls, budget_id):
        """Get budget by ID"""
        return cls.collection.find_one({'_id': ObjectId(budget_id)})
    
    @classmethod
    def get_by_category_and_period(cls, category_id, period):
        """Get active budget for category in period"""
        return cls.collection.find_one({
            'category_id': category_id,
            'period': period,
            'is_active': True
        })

class Log(BaseModel):
    """Log model"""
    
    @classmethod
    @property
    def collection(cls):
        return BaseModel.get_db().logs
    
    @classmethod
    def create(cls, data):
        """Create new log entry"""
        data['timestamp'] = datetime.now()
        result = cls.collection.insert_one(data)
        return str(result.inserted_id)
    
    @classmethod
    def get_all(cls, filters=None, page=1, per_page=50):
        """Get all logs with filters"""
        query = filters or {}
        skip = (page - 1) * per_page
        
        cursor = cls.collection.find(query).sort('timestamp', -1).skip(skip).limit(per_page)
        total = cls.collection.count_documents(query)
        
        return {
            'items': cls.to_list(cursor),
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }

class Settings(BaseModel):
    """Settings model"""
    
    @classmethod
    @property
    def collection(cls):
        return BaseModel.get_db().settings
    
    @classmethod
    def get(cls, key, default=None):
        """Get setting value"""
        setting = cls.collection.find_one({'key': key})
        return setting.get('value', default) if setting else default
    
    @classmethod
    def set(cls, key, value):
        """Set setting value"""
        cls.collection.update_one(
            {'key': key},
            {'$set': {'value': value, 'updated_at': datetime.now()}},
            upsert=True
        )