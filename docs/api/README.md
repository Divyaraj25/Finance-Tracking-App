# API Documentation

Welcome to the Expense Tracker API documentation. This API provides RESTful endpoints for managing expenses, transactions, accounts, budgets, and categories.

## Base URL

```
http://localhost:5000/api/v1
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Rate Limiting

- **Rate Limit**: 100 requests per minute per IP address
- **Rate Limit Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Response Format

All API responses follow a consistent JSON format:

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Error Handling

Error responses include detailed error information:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {}
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Available Endpoints

- [Transactions](./transactions.md) - Manage expense transactions
- [Accounts](./accounts.md) - Manage user accounts
- [Categories](./categories.md) - Manage expense categories
- [Budgets](./budgets.md) - Manage budget planning
- [Dashboard](./dashboard.md) - Dashboard analytics and metrics
- [Authentication](./auth.md) - User authentication and authorization

## SDKs and Libraries

- [Python SDK](../guides/python-sdk.md)
- [JavaScript SDK](../guides/javascript-sdk.md)
- [Postman Collection](./postman-collection.json)

## Support

For API support and questions:
- Create an issue on GitHub
- Check the [FAQ](../guides/faq.md)
- Review the [troubleshooting guide](../guides/troubleshooting.md)
