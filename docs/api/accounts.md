# Accounts API

Manage user accounts for tracking different financial accounts like bank accounts, credit cards, and cash.

## Endpoints

### Get All Accounts

```http
GET /api/v1/accounts
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "64a1b2c3d4e5f6789012346",
      "name": "Main Bank Account",
      "type": "bank",
      "balance": 5000.00,
      "currency": "USD",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "64a1b2c3d4e5f6789012347",
      "name": "Credit Card",
      "type": "credit_card",
      "balance": -250.75,
      "currency": "USD",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Get Account by ID

```http
GET /api/v1/accounts/{id}
```

### Create Account

```http
POST /api/v1/accounts
```

**Request Body:**
```json
{
  "name": "Savings Account",
  "type": "bank",
  "initial_balance": 10000.00,
  "currency": "USD",
  "description": "Emergency savings fund"
}
```

### Update Account

```http
PUT /api/v1/accounts/{id}
```

### Delete Account

```http
DELETE /api/v1/accounts/{id}
```

### Get Account Balance

```http
GET /api/v1/accounts/{id}/balance
```

## Account Types

- `bank` - Bank accounts
- `credit_card` - Credit card accounts
- `cash` - Cash on hand
- `investment` - Investment accounts
- `other` - Other account types
