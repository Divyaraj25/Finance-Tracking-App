# save as debug_mongo.py
from pymongo import MongoClient
from app import create_app
from app import mongo
import os
from dotenv import load_dotenv

load_dotenv()

print("="*60)
print("🔍 MONGODB DIAGNOSTIC")
print("="*60)

# 1. Check .env settings
print("\n1️⃣ .ENV CONFIGURATION:")
print(f"   MONGO_URI: {os.getenv('MONGO_URI', 'NOT SET')}")
print(f"   MONGO_DB: {os.getenv('MONGO_DB', 'NOT SET')}")

# 2. Direct PyMongo connection
print("\n2️⃣ DIRECT PYMONGO CONNECTION:")
try:
    client = MongoClient('localhost', 27017)
    client.admin.command('ping')
    print("   ✅ Connected to MongoDB")
    print(f"   📊 Databases: {client.list_database_names()}")
    
    # Check if expense_tracker exists
    if 'expense_tracker' in client.list_database_names():
        print("   ✅ Database 'expense_tracker' exists")
        print(f"   📁 Collections: {client['expense_tracker'].list_collection_names()}")
    else:
        print("   ❌ Database 'expense_tracker' does NOT exist!")
        print("   ⚠️  This is your problem! Creating it now...")
        client['expense_tracker'].create_collection('temp')
        client['expense_tracker']['temp'].drop()
        print("   ✅ Database 'expense_tracker' created!")
        
except Exception as e:
    print(f"   ❌ Failed: {e}")

# 3. Flask-PyMongo connection
print("\n3️⃣ FLASK-PYMONGO CONNECTION:")
try:
    app = create_app()
    with app.app_context():
        mongo.db.command('ping')
        print("   ✅ Flask-PyMongo connected")
        print(f"   📊 Current DB: {mongo.db.name}")
        print(f"   📁 Collections: {mongo.db.list_collection_names()}")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    print(f"   Error: {e}")

print("\n" + "="*60)