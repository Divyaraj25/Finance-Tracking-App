"""
Entry point for Expense Tracker System
Version: 1.0.0
"""
from app import create_app
import os
import sys

def main():
    """Main entry point with error handling"""
    try:
        # Create app
        app = create_app(os.getenv('FLASK_ENV', 'development'))
        
        # Check MongoDB connection
        with app.app_context():
            from app import mongo
            try:
                mongo.db.command('ping')
                print("✅ MongoDB connected successfully")
            except Exception as e:
                print("\n" + "="*60)
                print("⚠️  MongoDB is not running!")
                print("="*60)
                print("\nPlease start MongoDB:")
                print("  • Local:   mongod --dbpath ./data")
                print("  • Docker:  docker run -d -p 27017:27017 --name expense-mongo mongo:6.0")
                print("\nThen run database setup:")
                print("  python manage.py init-db")
                print("  python scripts/create_test_data.py")
                print("\n" + "="*60)
                
                response = input("\nContinue anyway? (y/n): ").lower()
                if response != 'y':
                    sys.exit(1)
        
        # Run app
        print(f"\n🚀 Starting Expense Tracker System v{app.config['APP_VERSION']}")
        print(f"📁 Data directory: {app.config.get('DATA_DIR', './data')}")
        print(f"🌐 URL: http://localhost:5000")
        print("\nPress Ctrl+C to stop\n")
        
        app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thank you for using Expense Tracker.")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        print("\nPlease check:")
        print("  1. MongoDB is running")
        print("  2. .env file exists with correct settings")
        print("  3. All dependencies installed: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == '__main__':
    main()