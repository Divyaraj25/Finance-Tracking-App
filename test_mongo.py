# Save this as test_mongo.py and run it
from pymongo import MongoClient

try:
    # Test default connection
    client = MongoClient('localhost', 27017)
    client.admin.command('ping')
    print("✅ MongoDB connected to Atlas")
    print(f"📊 Databases: {client.list_database_names()}")
except Exception as e:
    print(f"❌ Failed: {e}")
    
    # Try alternative connection strings
    try:
        client = MongoClient('127.0.0.1', 27017)
        client.admin.command('ping')
        print("✅ MongoDB connected on 127.0.0.1:27017")
    except:
        try:
            client = MongoClient('mongodb://localhost:27017/')
            client.admin.command('ping')
            print("✅ MongoDB connected with URI")
        except Exception as e2:
            print(f"❌ All connections failed: {e2}")