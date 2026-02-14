@echo off
echo 🚀 Setting up Expense Tracker System...
echo.

echo 📦 Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

echo.
echo 📚 Installing dependencies...
pip install -r requirements.txt

echo.
echo 🔧 Creating .env file...
if not exist .env (
    copy .env.example .env
    echo ✅ Created .env file
) else (
    echo ⚠️  .env file already exists
)

echo.
echo 🗄️ Initializing database...
python manage.py init-db

echo.
echo 📊 Creating test data? (y/n)
set /p create_test=Create sample test data? 
if /i "%create_test%"=="y" (
    python scripts\create_test_data.py
)

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file if needed
echo 2. Run: python run.py
echo 3. Open http://localhost:5000
echo.

pause