# Quick Start Guide

Get started with the Expense Tracker in just a few minutes.

## Prerequisites

- Python 3.9 or higher
- MongoDB 6.0 or higher
- Git (to clone the repository)

## 1. Clone and Install

```bash
git clone https://github.com/yourusername/expense-tracker.git
cd expense-tracker
pip install -r requirements.txt
```

## 2. Set Up Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
MONGODB_URI=mongodb://localhost:27017/expense_tracker
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

## 3. Initialize Database

```bash
python create_db.py
```

## 4. Run the Application

```bash
python run.py
```

The application will be available at `http://localhost:5000`

## 5. Create Your First Account

1. Open your browser and go to `http://localhost:5000`
2. Click "Sign Up" to create a new account
3. Fill in your details and register

## 6. Add Your First Transaction

1. Navigate to the "Transactions" page
2. Click "Add Transaction"
3. Enter:
   - Description: "Coffee"
   - Amount: 4.50
   - Category: "Food"
   - Account: "Main Account"
4. Click "Save"

## 7. Check Your Dashboard

Go to the "Dashboard" to see:
- Total balance
- Recent transactions
- Spending overview
- Budget progress

## Next Steps

- [Set up multiple accounts](./accounts.md)
- [Create budgets](./budgets.md)
- [Customize categories](./categories.md)
- [Explore advanced features](./advanced-features.md)

## Need Help?

- Check the [FAQ](./faq.md)
- Review [troubleshooting guide](./troubleshooting.md)
- Create an issue on GitHub
