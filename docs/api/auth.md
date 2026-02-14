# Authentication API

Handle user authentication, registration, and authorization.

## Endpoints

### User Registration

```http
POST /api/v1/auth/register
```

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "64a1b2c3d4e5f678901234a",
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "message": "User registered successfully"
}
```

### User Login

```http
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "secure_password123"
}
```

### Refresh Token

```http
POST /api/v1/auth/refresh
```

### Logout

```http
POST /api/v1/auth/logout
```

### Get Current User

```http
GET /api/v1/auth/me
```

### Update Profile

```http
PUT /api/v1/auth/profile
```

### Change Password

```http
PUT /api/v1/auth/password
```

## JWT Token Structure

```json
{
  "sub": "64a1b2c3d4e5f678901234a",
  "username": "john_doe",
  "email": "john@example.com",
  "exp": 1705123200,
  "iat": 1705036800
}
```
