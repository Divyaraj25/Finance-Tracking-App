# Transactions API

Manage expense transactions including creating, reading, updating, and deleting transactions.

## Endpoints

### Get All Transactions

```http
GET /api/v1/transactions
```

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Items per page (default: 20)
- `category` (string, optional): Filter by category
- `account` (string, optional): Filter by account
- `start_date` (string, optional): Start date (YYYY-MM-DD)
- `end_date` (string, optional): End date (YYYY-MM-DD)
- `search` (string, optional): Search in description

**Response:**
```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "id": "64a1b2c3d4e5f6789012345",
        "description": "Grocery shopping",
        "amount": 150.50,
        "category": "Food",
        "account": "Main Account",
        "date": "2024-01-15",
        "type": "expense",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 5,
      "total_items": 100,
      "items_per_page": 20
    }
  }
}
```

### Get Transaction by ID

```http
GET /api/v1/transactions/{id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "64a1b2c3d4e5f6789012345",
    "description": "Grocery shopping",
    "amount": 150.50,
    "category": "Food",
    "account": "Main Account",
    "date": "2024-01-15",
    "type": "expense",
    "notes": "Weekly groceries",
    "tags": ["essentials", "weekly"],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### Create Transaction

```http
POST /api/v1/transactions
```

**Request Body:**
```json
{
  "description": "Grocery shopping",
  "amount": 150.50,
  "category": "Food",
  "account": "Main Account",
  "date": "2024-01-15",
  "type": "expense",
  "notes": "Weekly groceries",
  "tags": ["essentials", "weekly"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "64a1b2c3d4e5f6789012345",
    "description": "Grocery shopping",
    "amount": 150.50,
    "category": "Food",
    "account": "Main Account",
    "date": "2024-01-15",
    "type": "expense",
    "notes": "Weekly groceries",
    "tags": ["essentials", "weekly"],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "Transaction created successfully"
}
```

### Update Transaction

```http
PUT /api/v1/transactions/{id}
```

**Request Body:**
```json
{
  "description": "Grocery shopping - Updated",
  "amount": 175.25,
  "notes": "Weekly groceries with extra items"
}
```

### Delete Transaction

```http
DELETE /api/v1/transactions/{id}
```

**Response:**
```json
{
  "success": true,
  "message": "Transaction deleted successfully"
}
```

### Get Transaction Statistics

```http
GET /api/v1/transactions/stats
```

**Query Parameters:**
- `period` (string): Period (week, month, quarter, year)
- `category` (string, optional): Filter by category
- `account` (string, optional): Filter by account

**Response:**
```json
{
  "success": true,
  "data": {
    "total_expenses": 2500.75,
    "total_income": 5000.00,
    "net_amount": 2499.25,
    "transaction_count": 45,
    "average_transaction": 55.57,
    "category_breakdown": {
      "Food": 800.50,
      "Transport": 300.00,
      "Entertainment": 200.25
    }
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `TRANSACTION_NOT_FOUND` | Transaction with specified ID not found |
| `INVALID_AMOUNT` | Amount must be a positive number |
| `INVALID_DATE` | Date format must be YYYY-MM-DD |
| `CATEGORY_NOT_FOUND` | Specified category does not exist |
| `ACCOUNT_NOT_FOUND` | Specified account does not exist |
| `VALIDATION_ERROR` | Request validation failed |
