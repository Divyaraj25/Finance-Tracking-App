# scripts/setup.sh
#!/bin/bash

echo "🚀 Setting up Expense Tracker System..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
if (( $(echo "$python_version < 3.9" | bc -l) )); then
    echo "❌ Python 3.9+ required. Found Python $python_version"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check MongoDB
echo "🍃 Checking MongoDB..."
if ! command -v mongod &> /dev/null; then
    echo "⚠️ MongoDB not found. Please install MongoDB 6.0+"
    exit 1
fi

# Create .env file
if [ ! -f .env ]; then
    echo "🔧 Creating .env file..."
    cp .env.example .env
    echo "✅ Created .env file. Please update with your configuration."
fi

# Initialize database
echo "🗄️ Initializing database..."
python manage.py init-db

# Create test data
read -p "Create sample test data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python scripts/create_test_data.py
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your configuration"
echo "2. Run the application: python run.py"
echo "3. Access the application: http://localhost:5000"