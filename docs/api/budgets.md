# Budgets API

Manage budget planning and tracking for different categories and time periods.

## Endpoints

### Get All Budgets

```http
GET /api/v1/budgets
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "64a1b2c3d4e5f6789012349",
      "name": "Monthly Food Budget",
      "category": "Food",
      "amount": 500.00,
      "spent": 350.75,
      "remaining": 149.25,
      "period": "monthly",
      "start_date": "2024-01-01",
      "end_date": "2024-01-31",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Create Budget

```http
POST /api/v1/budgets
```

**Request Body:**
```json
{
  "name": "Monthly Transport Budget",
  "category": "Transportation",
  "amount": 200.00,
  "period": "monthly",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

### Update Budget

```http
PUT /api/v1/budgets/{id}
```

### Delete Budget

```http
DELETE /api/v1/budgets/{id}
```

### Get Budget Progress

```http
GET /api/v1/budgets/{id}/progress
```
