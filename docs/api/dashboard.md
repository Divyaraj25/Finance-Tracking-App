# Dashboard API

Retrieve analytics, metrics, and dashboard data for financial overview.

## Endpoints

### Get Dashboard Overview

```http
GET /api/v1/dashboard/overview
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_balance": 7500.25,
    "monthly_income": 5000.00,
    "monthly_expenses": 3250.75,
    "net_monthly": 1749.25,
    "savings_rate": 0.35,
    "budget_utilization": 0.65,
    "recent_transactions": [
      {
        "id": "64a1b2c3d4e5f6789012345",
        "description": "Grocery shopping",
        "amount": 150.50,
        "category": "Food",
        "date": "2024-01-15"
      }
    ],
    "upcoming_bills": [
      {
        "name": "Rent",
        "amount": 1200.00,
        "due_date": "2024-02-01"
      }
    ]
  }
}
```

### Get Spending Trends

```http
GET /api/v1/dashboard/spending-trends
```

**Query Parameters:**
- `period` (string): Period (week, month, quarter, year)
- `category` (string, optional): Filter by category

### Get Budget Overview

```http
GET /api/v1/dashboard/budget-overview
```

### Get Account Summary

```http
GET /api/v1/dashboard/account-summary
```
