# test_complete_flow.py
"""
Complete End-to-End Test Suite for Expense Tracker System
Tests ALL endpoints in proper workflow sequences
"""
import requests
import json
from datetime import datetime, timedelta
import time

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api/v1"

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD} {text}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️ {text}{Colors.END}")

def test_health():
    """Test 1: Health Check Endpoint"""
    print_header("1️⃣  HEALTH CHECK ENDPOINTS")
    
    results = []
    
    # Basic health check
    try:
        r = requests.get(f"{BASE_URL}/health/")
        if r.status_code == 200:
            data = r.json()
            print_success(f"Health check: {data.get('status', 'unknown')}")
            print_info(f"  Version: {data.get('version', 'N/A')}")
            print_info(f"  Database: {data.get('database', 'N/A')}")
            results.append(('GET /health/', True, r.status_code))
        else:
            print_error(f"Health check failed: {r.status_code}")
            results.append(('GET /health/', False, r.status_code))
    except Exception as e:
        print_error(f"Health check error: {e}")
        results.append(('GET /health/', False, str(e)))
    
    # Detailed health check
    try:
        r = requests.get(f"{BASE_URL}/health/detailed")
        if r.status_code == 200:
            print_success("Detailed health check successful")
            results.append(('GET /health/detailed', True, r.status_code))
        else:
            print_error(f"Detailed health check failed: {r.status_code}")
            results.append(('GET /health/detailed', False, r.status_code))
    except Exception as e:
        print_error(f"Detailed health check error: {e}")
        results.append(('GET /health/detailed', False, str(e)))
    
    return results

def test_categories_flow():
    """Test 2: Categories - Complete CRUD Flow"""
    print_header("2️⃣  CATEGORIES - COMPLETE CRUD FLOW")
    
    results = []
    test_category = {
        "name": f"Test Category {datetime.now().strftime('%H%M%S')}",
        "type": "expense",
        "description": "Created by test flow"
    }
    category_id = None
    
    # 1. GET all categories (initial)
    print_info("📋 Step 1: GET all categories")
    try:
        r = requests.get(f"{API_URL}/categories")
        if r.status_code == 200:
            data = r.json()
            initial_count = len(data.get('data', []))
            print_success(f"Retrieved {initial_count} categories")
            results.append(('GET /categories', True, r.status_code))
        else:
            print_error(f"Failed to get categories: {r.status_code}")
            results.append(('GET /categories', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /categories', False, str(e)))
    
    # 2. POST - Create new category
    print_info("📋 Step 2: POST - Create category")
    try:
        r = requests.post(f"{API_URL}/categories", json=test_category)
        if r.status_code == 201:
            data = r.json()
            category_id = data.get('category_id')
            print_success(f"Created category with ID: {category_id}")
            results.append(('POST /categories', True, r.status_code))
        else:
            print_error(f"Failed to create category: {r.status_code}")
            print_error(f"Response: {r.text}")
            results.append(('POST /categories', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('POST /categories', False, str(e)))
    
    # 3. GET by ID - Verify creation
    if category_id:
        print_info(f"📋 Step 3: GET /categories/{category_id}")
        try:
            r = requests.get(f"{API_URL}/categories/{category_id}")
            if r.status_code == 200:
                data = r.json()
                category = data.get('data', {})
                print_success(f"Retrieved category: {category.get('name')}")
                results.append((f'GET /categories/{category_id}', True, r.status_code))
            else:
                print_error(f"Failed to get category: {r.status_code}")
                results.append((f'GET /categories/{category_id}', False, r.status_code))
        except Exception as e:
            print_error(f"Error: {e}")
            results.append((f'GET /categories/{category_id}', False, str(e)))
    
    # 4. PUT - Update category
    if category_id:
        print_info(f"📋 Step 4: PUT - Update category")
        update_data = {
            "name": f"Updated {test_category['name']}",
            "description": "Updated by test flow"
        }
        try:
            r = requests.put(f"{API_URL}/categories/{category_id}", json=update_data)
            if r.status_code == 200:
                print_success(f"Updated category")
                results.append((f'PUT /categories/{category_id}', True, r.status_code))
            else:
                print_error(f"Failed to update category: {r.status_code}")
                results.append((f'PUT /categories/{category_id}', False, r.status_code))
        except Exception as e:
            print_error(f"Error: {e}")
            results.append((f'PUT /categories/{category_id}', False, str(e)))
    
    # 5. GET by type - Filter categories
    print_info("📋 Step 5: GET /categories/by-type/expense")
    try:
        r = requests.get(f"{API_URL}/categories/by-type/expense")
        if r.status_code == 200:
            data = r.json()
            print_success(f"Retrieved {len(data.get('data', []))} expense categories")
            results.append(('GET /categories/by-type/expense', True, r.status_code))
        else:
            print_error(f"Failed to get categories by type: {r.status_code}")
            results.append(('GET /categories/by-type/expense', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /categories/by-type/expense', False, str(e)))
    
    # 6. DELETE - Delete category
    if category_id:
        print_info(f"📋 Step 6: DELETE - Remove category")
        try:
            r = requests.delete(f"{API_URL}/categories/{category_id}")
            if r.status_code == 200:
                print_success(f"Deleted category")
                results.append((f'DELETE /categories/{category_id}', True, r.status_code))
            else:
                print_error(f"Failed to delete category: {r.status_code}")
                results.append((f'DELETE /categories/{category_id}', False, r.status_code))
        except Exception as e:
            print_error(f"Error: {e}")
            results.append((f'DELETE /categories/{category_id}', False, str(e)))
    
    # 7. GET all categories (final)
    print_info("📋 Step 7: GET all categories (verify deletion)")
    try:
        r = requests.get(f"{API_URL}/categories")
        if r.status_code == 200:
            data = r.json()
            final_count = len(data.get('data', []))
            print_success(f"Now have {final_count} categories")
            if 'initial_count' in locals():
                print_info(f"  Change: {final_count - initial_count} categories")
            results.append(('GET /categories (final)', True, r.status_code))
        else:
            print_error(f"Failed to get categories: {r.status_code}")
            results.append(('GET /categories (final)', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /categories (final)', False, str(e)))
    
    return results, category_id

def test_accounts_flow():
    """Test 3: Accounts - Complete CRUD Flow"""
    print_header("3️⃣  ACCOUNTS - COMPLETE CRUD FLOW")
    
    results = []
    test_account = {
        "name": f"Test Account {datetime.now().strftime('%H%M%S')}",
        "type": "bank_account",
        "balance": 1000.00,
        "currency": "USD"
    }
    account_id = None
    
    # 1. GET all accounts
    print_info("📋 Step 1: GET all accounts")
    try:
        r = requests.get(f"{API_URL}/accounts")
        if r.status_code == 200:
            data = r.json()
            print_success(f"Retrieved {len(data.get('data', []))} accounts")
            results.append(('GET /accounts', True, r.status_code))
        else:
            print_error(f"Failed to get accounts: {r.status_code}")
            results.append(('GET /accounts', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /accounts', False, str(e)))
    
    # 2. POST - Create account
    print_info("📋 Step 2: POST - Create account")
    try:
        r = requests.post(f"{API_URL}/accounts", json=test_account)
        if r.status_code == 201:
            data = r.json()
            account_id = data.get('account_id')
            print_success(f"Created account with ID: {account_id}")
            results.append(('POST /accounts', True, r.status_code))
        else:
            print_error(f"Failed to create account: {r.status_code}")
            print_error(f"Response: {r.text}")
            results.append(('POST /accounts', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('POST /accounts', False, str(e)))
    
    # 3. GET by ID
    if account_id:
        print_info(f"📋 Step 3: GET /accounts/{account_id}")
        try:
            r = requests.get(f"{API_URL}/accounts/{account_id}")
            if r.status_code == 200:
                data = r.json()
                account = data.get('data', {})
                print_success(f"Retrieved account: {account.get('name')}")
                print_info(f"  Balance: ${account.get('balance'):,.2f}")
                results.append((f'GET /accounts/{account_id}', True, r.status_code))
            else:
                print_error(f"Failed to get account: {r.status_code}")
                results.append((f'GET /accounts/{account_id}', False, r.status_code))
        except Exception as e:
            print_error(f"Error: {e}")
            results.append((f'GET /accounts/{account_id}', False, str(e)))
    
    # 4. PUT - Update account
    if account_id:
        print_info(f"📋 Step 4: PUT - Update account")
        update_data = {
            "name": f"Updated {test_account['name']}",
            "balance": 1500.00
        }
        try:
            r = requests.put(f"{API_URL}/accounts/{account_id}", json=update_data)
            if r.status_code == 200:
                print_success(f"Updated account")
                results.append((f'PUT /accounts/{account_id}', True, r.status_code))
            else:
                print_error(f"Failed to update account: {r.status_code}")
                results.append((f'PUT /accounts/{account_id}', False, r.status_code))
        except Exception as e:
            print_error(f"Error: {e}")
            results.append((f'PUT /accounts/{account_id}', False, str(e)))
    
    # 5. GET accounts summary
    print_info("📋 Step 5: GET /accounts/summary")
    try:
        r = requests.get(f"{API_URL}/accounts/summary")
        if r.status_code == 200:
            data = r.json()
            summary = data.get('data', {})
            print_success(f"Accounts summary retrieved")
            print_info(f"  Total accounts: {summary.get('total_accounts', 0)}")
            print_info(f"  Total balance: ${summary.get('total_balance', 0):,.2f}")
            results.append(('GET /accounts/summary', True, r.status_code))
        else:
            print_error(f"Failed to get accounts summary: {r.status_code}")
            results.append(('GET /accounts/summary', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /accounts/summary', False, str(e)))
    
    # 6. GET account types
    print_info("📋 Step 6: GET /accounts/types")
    try:
        r = requests.get(f"{API_URL}/accounts/types")
        if r.status_code == 200:
            data = r.json()
            print_success(f"Retrieved {len(data.get('data', []))} account types")
            results.append(('GET /accounts/types', True, r.status_code))
        else:
            print_error(f"Failed to get account types: {r.status_code}")
            results.append(('GET /accounts/types', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /accounts/types', False, str(e)))
    
    # 7. DELETE - Delete account
    if account_id:
        print_info(f"📋 Step 7: DELETE - Remove account")
        try:
            r = requests.delete(f"{API_URL}/accounts/{account_id}")
            if r.status_code == 200:
                print_success(f"Deleted account")
                results.append((f'DELETE /accounts/{account_id}', True, r.status_code))
            else:
                print_error(f"Failed to delete account: {r.status_code}")
                results.append((f'DELETE /accounts/{account_id}', False, r.status_code))
        except Exception as e:
            print_error(f"Error: {e}")
            results.append((f'DELETE /accounts/{account_id}', False, str(e)))
    
    return results, account_id

def test_transactions_flow():
    """Test 4: Transactions - Complete CRUD Flow"""
    print_header("4️⃣  TRANSACTIONS - COMPLETE CRUD FLOW")
    
    results = []
    
    # First create an account to use for transactions
    test_account = {
        "name": f"Transaction Test Account {datetime.now().strftime('%H%M%S')}",
        "type": "bank_account",
        "balance": 5000.00,
        "currency": "USD"
    }
    
    account_id = None
    transaction_id = None
    
    # Create account for testing
    try:
        r = requests.post(f"{API_URL}/accounts", json=test_account)
        if r.status_code == 201:
            account_id = r.json().get('account_id')
            print_success(f"Created test account: {account_id}")
    except Exception as e:
        print_error(f"Failed to create test account: {e}")
    
    # Get a category ID
    category_id = None
    try:
        r = requests.get(f"{API_URL}/categories")
        if r.status_code == 200:
            categories = r.json().get('data', [])
            for cat in categories:
                if cat.get('type') == 'expense':
                    category_id = cat.get('id')
                    break
    except Exception as e:
        print_error(f"Failed to get category: {e}")
    
    # 1. GET all transactions
    print_info("📋 Step 1: GET all transactions")
    try:
        r = requests.get(f"{API_URL}/transactions")
        if r.status_code == 200:
            data = r.json()
            print_success(f"Retrieved {len(data.get('data', []))} transactions")
            results.append(('GET /transactions', True, r.status_code))
        else:
            print_error(f"Failed to get transactions: {r.status_code}")
            results.append(('GET /transactions', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /transactions', False, str(e)))
    
    # 2. POST - Create expense transaction
    if account_id and category_id:
        print_info("📋 Step 2: POST - Create expense transaction")
        test_transaction = {
            "type": "expense",
            "amount": 75.50,
            "description": "Test grocery purchase",
            "date": datetime.now().isoformat(),
            "category_id": category_id,
            "from_account_id": account_id,
            "tags": ["test", "groceries"]
        }
        try:
            r = requests.post(f"{API_URL}/transactions", json=test_transaction)
            if r.status_code == 201:
                data = r.json()
                transaction_id = data.get('transaction_id')
                print_success(f"Created transaction with ID: {transaction_id}")
                results.append(('POST /transactions', True, r.status_code))
            else:
                print_error(f"Failed to create transaction: {r.status_code}")
                print_error(f"Response: {r.text}")
                results.append(('POST /transactions', False, r.status_code))
        except Exception as e:
            print_error(f"Error: {e}")
            results.append(('POST /transactions', False, str(e)))
    
    # 3. GET by ID
    if transaction_id:
        print_info(f"📋 Step 3: GET /transactions/{transaction_id}")
        try:
            r = requests.get(f"{API_URL}/transactions/{transaction_id}")
            if r.status_code == 200:
                data = r.json()
                transaction = data.get('data', {})
                print_success(f"Retrieved transaction: {transaction.get('description')}")
                print_info(f"  Amount: ${transaction.get('amount'):,.2f}")
                results.append((f'GET /transactions/{transaction_id}', True, r.status_code))
            else:
                print_error(f"Failed to get transaction: {r.status_code}")
                results.append((f'GET /transactions/{transaction_id}', False, r.status_code))
        except Exception as e:
            print_error(f"Error: {e}")
            results.append((f'GET /transactions/{transaction_id}', False, str(e)))
    
    # 4. PUT - Update transaction
    if transaction_id:
        print_info(f"📋 Step 4: PUT - Update transaction")
        update_data = {
            "description": "Updated test transaction",
            "amount": 95.75
        }
        try:
            r = requests.put(f"{API_URL}/transactions/{transaction_id}", json=update_data)
            if r.status_code == 200:
                print_success(f"Updated transaction")
                results.append((f'PUT /transactions/{transaction_id}', True, r.status_code))
            else:
                print_error(f"Failed to update transaction: {r.status_code}")
                results.append((f'PUT /transactions/{transaction_id}', False, r.status_code))
        except Exception as e:
            print_error(f"Error: {e}")
            results.append((f'PUT /transactions/{transaction_id}', False, str(e)))
    
    # 5. GET with filters
    print_info("📋 Step 5: GET /transactions with filters")
    try:
        params = {
            "type": "expense",
            "limit": 5
        }
        r = requests.get(f"{API_URL}/transactions", params=params)
        if r.status_code == 200:
            print_success(f"Retrieved filtered transactions")
            results.append(('GET /transactions (filtered)', True, r.status_code))
        else:
            print_error(f"Failed to get filtered transactions: {r.status_code}")
            results.append(('GET /transactions (filtered)', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /transactions (filtered)', False, str(e)))
    
    # 6. DELETE - Delete transaction
    if transaction_id:
        print_info(f"📋 Step 6: DELETE - Remove transaction")
        try:
            r = requests.delete(f"{API_URL}/transactions/{transaction_id}")
            if r.status_code == 200:
                print_success(f"Deleted transaction")
                results.append((f'DELETE /transactions/{transaction_id}', True, r.status_code))
            else:
                print_error(f"Failed to delete transaction: {r.status_code}")
                results.append((f'DELETE /transactions/{transaction_id}', False, r.status_code))
        except Exception as e:
            print_error(f"Error: {e}")
            results.append((f'DELETE /transactions/{transaction_id}', False, str(e)))
    
    # Cleanup - delete test account
    if account_id:
        requests.delete(f"{API_URL}/accounts/{account_id}")
    
    return results, transaction_id

def test_budgets_flow():
    """Test 5: Budgets - Complete CRUD Flow"""
    print_header("5️⃣  BUDGETS - COMPLETE CRUD FLOW")
    
    results = []
    
    # Get a category ID for budget
    category_id = None
    try:
        r = requests.get(f"{API_URL}/categories")
        if r.status_code == 200:
            categories = r.json().get('data', [])
            for cat in categories:
                if cat.get('type') == 'expense' and not cat.get('is_default'):
                    category_id = cat.get('id')
                    break
    except Exception as e:
        print_error(f"Failed to get category: {e}")
    
    budget_id = None
    
    # 1. GET all budgets
    print_info("📋 Step 1: GET all budgets")
    try:
        r = requests.get(f"{API_URL}/budgets")
        if r.status_code == 200:
            data = r.json()
            print_success(f"Retrieved {len(data.get('data', []))} budgets")
            results.append(('GET /budgets', True, r.status_code))
        else:
            print_error(f"Failed to get budgets: {r.status_code}")
            results.append(('GET /budgets', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /budgets', False, str(e)))
    
    # 2. POST - Create budget
    if category_id:
        print_info("📋 Step 2: POST - Create budget")
        test_budget = {
            "category_id": category_id,
            "amount": 500.00,
            "period": "monthly"
        }
        try:
            r = requests.post(f"{API_URL}/budgets", json=test_budget)
            if r.status_code == 201:
                data = r.json()
                budget_id = data.get('budget_id')
                print_success(f"Created budget with ID: {budget_id}")
                results.append(('POST /budgets', True, r.status_code))
            else:
                print_error(f"Failed to create budget: {r.status_code}")
                print_error(f"Response: {r.text}")
                results.append(('POST /budgets', False, r.status_code))
        except Exception as e:
            print_error(f"Error: {e}")
            results.append(('POST /budgets', False, str(e)))
    
    # 3. GET by ID
    if budget_id:
        print_info(f"📋 Step 3: GET /budgets/{budget_id}")
        try:
            r = requests.get(f"{API_URL}/budgets/{budget_id}")
            if r.status_code == 200:
                data = r.json()
                budget = data.get('data', {})
                print_success(f"Retrieved budget for category: {budget.get('category_name')}")
                print_info(f"  Amount: ${budget.get('amount'):,.2f}")
                print_info(f"  Spent: ${budget.get('spent', 0):,.2f}")
                results.append((f'GET /budgets/{budget_id}', True, r.status_code))
            else:
                print_error(f"Failed to get budget: {r.status_code}")
                results.append((f'GET /budgets/{budget_id}', False, r.status_code))
        except Exception as e:
            print_error(f"Error: {e}")
            results.append((f'GET /budgets/{budget_id}', False, str(e)))
    
    # 4. PUT - Update budget
    if budget_id:
        print_info(f"📋 Step 4: PUT - Update budget")
        update_data = {
            "amount": 600.00,
            "period": "monthly"
        }
        try:
            r = requests.put(f"{API_URL}/budgets/{budget_id}", json=update_data)
            if r.status_code == 200:
                print_success(f"Updated budget")
                results.append((f'PUT /budgets/{budget_id}', True, r.status_code))
            else:
                print_error(f"Failed to update budget: {r.status_code}")
                results.append((f'PUT /budgets/{budget_id}', False, r.status_code))
        except Exception as e:
            print_error(f"Error: {e}")
            results.append((f'PUT /budgets/{budget_id}', False, str(e)))
    
    # 5. POST - Recalculate budget
    if budget_id:
        print_info(f"📋 Step 5: POST - Recalculate budget")
        try:
            r = requests.post(f"{API_URL}/budgets/recalculate/{budget_id}")
            if r.status_code == 200:
                data = r.json()
                print_success(f"Recalculated budget")
                print_info(f"  Old spent: ${data.get('data', {}).get('old_spent', 0):,.2f}")
                print_info(f"  New spent: ${data.get('data', {}).get('new_spent', 0):,.2f}")
                results.append((f'POST /budgets/recalculate/{budget_id}', True, r.status_code))
            else:
                print_error(f"Failed to recalculate budget: {r.status_code}")
                results.append((f'POST /budgets/recalculate/{budget_id}', False, r.status_code))
        except Exception as e:
            print_error(f"Error: {e}")
            results.append((f'POST /budgets/recalculate/{budget_id}', False, str(e)))
    
    # 6. GET budget summary
    print_info("📋 Step 6: GET /budgets/summary")
    try:
        r = requests.get(f"{API_URL}/budgets/summary")
        if r.status_code == 200:
            data = r.json()
            summary = data.get('data', {})
            print_success(f"Budget summary retrieved")
            print_info(f"  Total budget: ${summary.get('total_budget', 0):,.2f}")
            print_info(f"  Total spent: ${summary.get('total_spent', 0):,.2f}")
            print_info(f"  Active budgets: {summary.get('active_budgets', 0)}")
            results.append(('GET /budgets/summary', True, r.status_code))
        else:
            print_error(f"Failed to get budget summary: {r.status_code}")
            results.append(('GET /budgets/summary', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /budgets/summary', False, str(e)))
    
    # 7. DELETE - Delete budget
    if budget_id:
        print_info(f"📋 Step 7: DELETE - Remove budget")
        try:
            r = requests.delete(f"{API_URL}/budgets/{budget_id}")
            if r.status_code == 200:
                print_success(f"Deleted budget")
                results.append((f'DELETE /budgets/{budget_id}', True, r.status_code))
            else:
                print_error(f"Failed to delete budget: {r.status_code}")
                results.append((f'DELETE /budgets/{budget_id}', False, r.status_code))
        except Exception as e:
            print_error(f"Error: {e}")
            results.append((f'DELETE /budgets/{budget_id}', False, str(e)))
    
    return results, budget_id

def test_reports_endpoints():
    """Test 6: Reports Endpoints"""
    print_header("6️⃣  REPORTS ENDPOINTS")
    
    results = []
    
    # 1. GET financial summary
    print_info("📋 Step 1: GET /reports/summary")
    try:
        r = requests.get(f"{API_URL}/reports/summary")
        if r.status_code == 200:
            data = r.json()
            summary = data.get('data', {})
            print_success(f"Financial summary retrieved")
            print_info(f"  Total balance: ${summary.get('total_balance', 0):,.2f}")
            print_info(f"  Monthly income: ${summary.get('monthly_income', 0):,.2f}")
            print_info(f"  Monthly expense: ${summary.get('monthly_expense', 0):,.2f}")
            print_info(f"  Savings rate: {summary.get('savings_rate', 0):.1f}%")
            results.append(('GET /reports/summary', True, r.status_code))
        else:
            print_error(f"Failed to get financial summary: {r.status_code}")
            results.append(('GET /reports/summary', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /reports/summary', False, str(e)))
    
    # 2. GET monthly report
    print_info("📋 Step 2: GET /reports/monthly")
    now = datetime.now()
    params = {
        "year": now.year,
        "month": now.month
    }
    try:
        r = requests.get(f"{API_URL}/reports/monthly", params=params)
        if r.status_code == 200:
            print_success(f"Monthly report retrieved")
            results.append(('GET /reports/monthly', True, r.status_code))
        else:
            print_error(f"Failed to get monthly report: {r.status_code}")
            results.append(('GET /reports/monthly', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /reports/monthly', False, str(e)))
    
    # 3. GET category report
    print_info("📋 Step 3: GET /reports/categories")
    end = datetime.now()
    start = end - timedelta(days=30)
    params = {
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": end.strftime("%Y-%m-%d")
    }
    try:
        r = requests.get(f"{API_URL}/reports/categories", params=params)
        if r.status_code == 200:
            print_success(f"Category report retrieved")
            results.append(('GET /reports/categories', True, r.status_code))
        else:
            print_error(f"Failed to get category report: {r.status_code}")
            results.append(('GET /reports/categories', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /reports/categories', False, str(e)))
    
    return results

def test_export_endpoints():
    """Test 7: Export Endpoints"""
    print_header("7️⃣  EXPORT ENDPOINTS")
    
    results = []
    
    # 1. GET export formats
    print_info("📋 Step 1: GET /export/formats")
    try:
        r = requests.get(f"{API_URL}/export/formats")
        if r.status_code == 200:
            data = r.json()
            print_success(f"Export formats retrieved")
            print_info(f"  Formats: {', '.join(data.get('formats', []))}")
            results.append(('GET /export/formats', True, r.status_code))
        else:
            print_error(f"Failed to get export formats: {r.status_code}")
            results.append(('GET /export/formats', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /export/formats', False, str(e)))
    
    # 2. Test CSV export
    print_info("📋 Step 2: GET /export/csv")
    try:
        r = requests.get(f"{API_URL}/export/csv?type=all")
        if r.status_code == 200:
            print_success(f"CSV export successful")
            results.append(('GET /export/csv', True, r.status_code))
        else:
            print_error(f"Failed to export CSV: {r.status_code}")
            results.append(('GET /export/csv', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /export/csv', False, str(e)))
    
    # 3. Test JSON export
    print_info("📋 Step 3: GET /export/json")
    try:
        r = requests.get(f"{API_URL}/export/json?type=transactions")
        if r.status_code == 200:
            print_success(f"JSON export successful")
            results.append(('GET /export/json', True, r.status_code))
        else:
            print_error(f"Failed to export JSON: {r.status_code}")
            results.append(('GET /export/json', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /export/json', False, str(e)))
    
    return results

def test_logs_endpoints():
    """Test 8: Logs Endpoints"""
    print_header("8️⃣  LOGS ENDPOINTS")
    
    results = []
    
    # 1. GET logs
    print_info("📋 Step 1: GET /logs/data")
    try:
        r = requests.get(f"{BASE_URL}/logs/data")
        if r.status_code == 200:
            data = r.json()
            print_success(f"Retrieved {len(data.get('data', []))} logs")
            results.append(('GET /logs/data', True, r.status_code))
        else:
            print_error(f"Failed to get logs: {r.status_code}")
            results.append(('GET /logs/data', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /logs/data', False, str(e)))
    
    # 2. GET log summary
    print_info("📋 Step 2: GET /logs/summary")
    try:
        r = requests.get(f"{BASE_URL}/logs/summary")
        if r.status_code == 200:
            data = r.json()
            summary = data.get('data', {})
            print_success(f"Log summary retrieved")
            print_info(f"  Total logs: {summary.get('total', 0)}")
            print_info(f"  Today: {summary.get('today', 0)}")
            results.append(('GET /logs/summary', True, r.status_code))
        else:
            print_error(f"Failed to get log summary: {r.status_code}")
            results.append(('GET /logs/summary', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /logs/summary', False, str(e)))
    
    # 3. GET log levels
    print_info("📋 Step 3: GET /logs/levels")
    try:
        r = requests.get(f"{BASE_URL}/logs/levels")
        if r.status_code == 200:
            print_success(f"Log levels retrieved")
            results.append(('GET /logs/levels', True, r.status_code))
        else:
            print_error(f"Failed to get log levels: {r.status_code}")
            results.append(('GET /logs/levels', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /logs/levels', False, str(e)))
    
    return results

def test_profile_endpoints():
    """Test 9: Profile & Settings Endpoints"""
    print_header("9️⃣  PROFILE & SETTINGS ENDPOINTS")
    
    results = []
    
    # 1. GET settings
    print_info("📋 Step 1: GET /profile/settings")
    try:
        r = requests.get(f"{BASE_URL}/profile/settings")
        if r.status_code == 200:
            data = r.json()
            settings = data.get('data', {})
            print_success(f"Settings retrieved")
            print_info(f"  Currency: {settings.get('currency', 'N/A')}")
            print_info(f"  Theme: {settings.get('theme', 'N/A')}")
            results.append(('GET /profile/settings', True, r.status_code))
        else:
            print_error(f"Failed to get settings: {r.status_code}")
            results.append(('GET /profile/settings', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /profile/settings', False, str(e)))
    
    # 2. POST update settings
    print_info("📋 Step 2: POST /profile/settings")
    test_settings = {
        "currency": "USD",
        "theme": "light",
        "items_per_page": 25
    }
    try:
        r = requests.post(f"{BASE_URL}/profile/settings", json=test_settings)
        if r.status_code == 200:
            print_success(f"Settings updated")
            results.append(('POST /profile/settings', True, r.status_code))
        else:
            print_error(f"Failed to update settings: {r.status_code}")
            results.append(('POST /profile/settings', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('POST /profile/settings', False, str(e)))
    
    # 3. GET statistics
    print_info("📋 Step 3: GET /profile/statistics")
    try:
        r = requests.get(f"{BASE_URL}/profile/statistics")
        if r.status_code == 200:
            data = r.json()
            stats = data.get('data', {})
            print_success(f"Statistics retrieved")
            print_info(f"  Total transactions: {stats.get('total_transactions', 0)}")
            print_info(f"  Total accounts: {stats.get('total_accounts', 0)}")
            results.append(('GET /profile/statistics', True, r.status_code))
        else:
            print_error(f"Failed to get statistics: {r.status_code}")
            results.append(('GET /profile/statistics', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /profile/statistics', False, str(e)))
    
    return results

def test_help_endpoints():
    """Test 10: Help System Endpoints"""
    print_header("🔟  HELP SYSTEM ENDPOINTS")
    
    results = []
    
    # 1. GET help search
    print_info("📋 Step 1: GET /help/search")
    try:
        r = requests.get(f"{BASE_URL}/help/search?q=transaction")
        if r.status_code == 200:
            data = r.json()
            print_success(f"Help search successful")
            print_info(f"  Found {len(data.get('results', []))} results")
            results.append(('GET /help/search', True, r.status_code))
        else:
            print_error(f"Failed to search help: {r.status_code}")
            results.append(('GET /help/search', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /help/search', False, str(e)))
    
    # 2. GET keyboard shortcuts
    print_info("📋 Step 2: GET /help/shortcuts")
    try:
        r = requests.get(f"{BASE_URL}/help/shortcuts")
        if r.status_code == 200:
            data = r.json()
            print_success(f"Keyboard shortcuts retrieved")
            print_info(f"  {len(data.get('data', []))} shortcuts available")
            results.append(('GET /help/shortcuts', True, r.status_code))
        else:
            print_error(f"Failed to get shortcuts: {r.status_code}")
            results.append(('GET /help/shortcuts', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /help/shortcuts', False, str(e)))
    
    # 3. GET system info
    print_info("📋 Step 3: GET /help/system-info")
    try:
        r = requests.get(f"{BASE_URL}/help/system-info")
        if r.status_code == 200:
            data = r.json()
            sys_info = data.get('data', {})
            print_success(f"System info retrieved")
            print_info(f"  Python: {sys_info.get('python', {}).get('version', 'N/A')}")
            print_info(f"  Flask: {sys_info.get('flask', {}).get('version', 'N/A')}")
            results.append(('GET /help/system-info', True, r.status_code))
        else:
            print_error(f"Failed to get system info: {r.status_code}")
            results.append(('GET /help/system-info', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /help/system-info', False, str(e)))
    
    return results

def test_updates_endpoints():
    """Test 11: Updates Endpoints"""
    print_header("1️⃣1️⃣  UPDATES ENDPOINTS")
    
    results = []
    
    # 1. GET check updates
    print_info("📋 Step 1: GET /updates/check")
    try:
        r = requests.get(f"{BASE_URL}/updates/check")
        if r.status_code == 200:
            data = r.json()
            update_info = data.get('data', {})
            print_success(f"Update check successful")
            print_info(f"  Current version: {update_info.get('current_version', 'N/A')}")
            print_info(f"  Latest version: {update_info.get('latest_version', 'N/A')}")
            print_info(f"  Updates available: {update_info.get('updates_available', False)}")
            results.append(('GET /updates/check', True, r.status_code))
        else:
            print_error(f"Failed to check updates: {r.status_code}")
            results.append(('GET /updates/check', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /updates/check', False, str(e)))
    
    # 2. GET dependencies
    print_info("📋 Step 2: GET /updates/dependencies")
    try:
        r = requests.get(f"{BASE_URL}/updates/dependencies")
        if r.status_code == 200:
            data = r.json()
            print_success(f"Dependencies retrieved")
            print_info(f"  {len(data.get('data', []))} packages checked")
            results.append(('GET /updates/dependencies', True, r.status_code))
        else:
            print_error(f"Failed to get dependencies: {r.status_code}")
            results.append(('GET /updates/dependencies', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /updates/dependencies', False, str(e)))
    
    return results

def test_errors_endpoints():
    """Test 12: Errors Endpoints"""
    print_header("1️⃣2️⃣  ERRORS ENDPOINTS")
    
    results = []
    
    # 1. GET errors
    print_info("📋 Step 1: GET /errors/data")
    try:
        r = requests.get(f"{BASE_URL}/errors/data")
        if r.status_code == 200:
            data = r.json()
            print_success(f"Errors retrieved")
            print_info(f"  Found {len(data.get('data', []))} errors")
            results.append(('GET /errors/data', True, r.status_code))
        else:
            print_error(f"Failed to get errors: {r.status_code}")
            results.append(('GET /errors/data', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /errors/data', False, str(e)))
    
    # 2. GET error summary
    print_info("📋 Step 2: GET /errors/summary")
    try:
        r = requests.get(f"{BASE_URL}/errors/summary")
        if r.status_code == 200:
            data = r.json()
            summary = data.get('data', {})
            print_success(f"Error summary retrieved")
            print_info(f"  Total errors: {summary.get('total_errors', 0)}")
            print_info(f"  Today: {summary.get('errors_today', 0)}")
            results.append(('GET /errors/summary', True, r.status_code))
        else:
            print_error(f"Failed to get error summary: {r.status_code}")
            results.append(('GET /errors/summary', False, r.status_code))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(('GET /errors/summary', False, str(e)))
    
    return results

def print_summary(all_results):
    """Print comprehensive test summary"""
    print_header("📊  COMPLETE TEST SUMMARY")
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    print(f"{'ENDPOINT':<50} {'STATUS':<15} {'CODE':<10}")
    print("-" * 75)
    
    for category, results in all_results.items():
        print(f"\n{Colors.BOLD}{category}{Colors.END}")
        for endpoint, success, status in results:
            total_tests += 1
            if success:
                passed_tests += 1
                status_display = f"{Colors.GREEN}PASSED{Colors.END}"
            else:
                failed_tests += 1
                status_display = f"{Colors.RED}FAILED{Colors.END}"
            print(f"  {endpoint:<48} {status_display:<15} {status}")
    
    print("\n" + "=" * 75)
    print(f"{Colors.BOLD}FINAL RESULTS:{Colors.END}")
    print(f"  {Colors.GREEN}✅ Passed: {passed_tests}/{total_tests}{Colors.END}")
    print(f"  {Colors.RED}❌ Failed: {failed_tests}/{total_tests}{Colors.END}")
    print(f"  {Colors.BLUE}📊 Success Rate: {(passed_tests/total_tests*100):.1f}%{Colors.END}")
    print("=" * 75)
    
    if failed_tests > 0:
        print(f"\n{Colors.YELLOW}⚠️  Some tests failed. Check the output above for error details.{Colors.END}")

def main():
    """Main test execution"""
    print_header("🚀  EXPENSE TRACKER - COMPLETE END-TO-END TEST SUITE")
    print(f"{Colors.BOLD}Base URL: {BASE_URL}{Colors.END}")
    print(f"{Colors.BOLD}API URL: {API_URL}{Colors.END}")
    print(f"{Colors.BOLD}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    
    all_results = {}
    
    # Run all test suites
    all_results['Health'] = test_health()
    all_results['Categories'] = test_categories_flow()[0]
    all_results['Accounts'] = test_accounts_flow()[0]
    all_results['Transactions'] = test_transactions_flow()[0]
    all_results['Budgets'] = test_budgets_flow()[0]
    all_results['Reports'] = test_reports_endpoints()
    all_results['Export'] = test_export_endpoints()
    all_results['Logs'] = test_logs_endpoints()
    all_results['Profile'] = test_profile_endpoints()
    all_results['Help'] = test_help_endpoints()
    all_results['Updates'] = test_updates_endpoints()
    all_results['Errors'] = test_errors_endpoints()
    
    # Print summary
    print_summary(all_results)

if __name__ == "__main__":
    main()