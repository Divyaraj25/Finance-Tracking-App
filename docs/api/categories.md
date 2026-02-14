# Categories API

Manage expense categories for organizing and tracking different types of expenses.

## Endpoints

### Get All Categories

```http
GET /api/v1/categories
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "64a1b2c3d4e5f6789012348",
      "name": "Food",
      "description": "Food and groceries",
      "color": "#FF6B6B",
      "icon": "utensils",
      "budget_limit": 500.00,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Create Category

```http
POST /api/v1/categories
```

**Request Body:**
```json
{
  "name": "Transportation",
  "description": "Public transport and fuel",
  "color": "#4ECDC4",
  "icon": "car",
  "budget_limit": 200.00
}
```

### Update Category

```http
PUT /api/v1/categories/{id}
```

### Delete Category

```http
DELETE /api/v1/categories/{id}
```
