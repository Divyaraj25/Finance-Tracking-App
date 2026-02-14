# Save this as create_db.py
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.expense_tracker

# Create a dummy collection to force database creation
db.initialize.insert_one({'status': 'created'})
print("✅ Database 'expense_tracker' created!")

# Verify it exists
print(f"📊 Databases: {client.list_database_names()}")