# Security Update - JWT Authentication Added

## What Changed

Added JWT authentication protection to all user-specific endpoints. Previously, endpoints were unprotected and anyone could access any user's data.

## Protected Endpoints

### Users Routes

- `GET /users/` - Requires authentication
- `GET /users/{user_id}` - Requires authentication
- `GET /users/name/{name}` - Requires authentication
- `PUT /users/{user_id}` - Requires authentication + ownership check
- `DELETE /users/{user_id}` - Requires authentication + ownership check

### Moods Routes

- `POST /users/{user_id}/moods/` - Requires authentication + ownership check
- `GET /users/{user_id}/moods/` - Requires authentication + ownership check
- `GET /users/{user_id}/moods/{id}/` - Requires authentication + ownership check
- `PUT /users/{user_id}/moods/{id}/` - Requires authentication + ownership check
- `DELETE /users/{user_id}/moods/{id}` - Requires authentication + ownership check

### Journals Routes

- `POST /users/{user_id}/moods/{mood_id}/journals/` - Requires authentication + ownership check
- `GET /users/{user_id}/moods/{mood_id}/journals/` - Requires authentication + ownership check
- `GET /users/{user_id}/moods/{mood_id}/journals/{id}` - Requires authentication + ownership check
- `PUT /users/{user_id}/moods/{mood_id}/journals/{id}` - Requires authentication + ownership check
- `DELETE /users/{user_id}/moods/{mood_id}/journals/{id}` - Requires authentication + ownership check

### Resources Routes (Public)

- `GET /resources/` - Public (no auth required)
- `GET /resources/recommend` - Public (no auth required)
- `GET /resources/{id}` - Public (no auth required)
- `POST /resources/` - Public (consider adding admin protection)
- `DELETE /resources/{id}` - Public (consider adding admin protection)

## How It Works

1. User logs in via `POST /auth/login` and receives a JWT token
2. User includes token in `Authorization: Bearer <token>` header for protected endpoints
3. Backend validates token and extracts user identity
4. Ownership checks ensure users can only access their own data

## Testing

All 22 tests pass with authentication enabled. Tests use the `user_token` fixture which automatically handles login and token management.

## Future Improvements

1. Add admin role for resource management (POST/DELETE /resources/)
2. Implement token refresh endpoint
3. Add rate limiting
4. Consider adding user roles/permissions system
