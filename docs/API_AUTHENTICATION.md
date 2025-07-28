# Authentication API Documentation

## Overview

The SafeSteps Certificate Generator authentication system provides secure user authentication and management through a set of Python functions. While this is a Streamlit application without traditional REST endpoints, these functions serve as the API for authentication operations.

## Core Authentication Functions

### `login_with_credentials(username_or_email: str, password: str) -> Tuple[bool, Dict[str, Any], str]`

Authenticates a user with username/email and password.

**Parameters:**
- `username_or_email` (str): The user's username OR email address
- `password` (str): The user's password

**Returns:**
- `success` (bool): Whether authentication succeeded
- `user_data` (dict): User information if successful, empty dict if failed
- `error_message` (str): Error description if failed, empty string if successful

**User Data Structure:**
```python
{
    "user_id": "unique-uuid",
    "username": "john_doe",
    "email": "john@example.com",
    "role": "user" | "admin",
    "created_at": "2024-01-20T10:30:00",
    "last_login": "2024-01-20T15:45:00",
    "is_active": true
}
```

**Example Usage:**
```python
from utils.auth import login_with_credentials

success, user_data, error = login_with_credentials("john_doe", "SecurePass123")
if success:
    print(f"Welcome {user_data['username']}!")
else:
    print(f"Login failed: {error}")
```

### `create_session(username: str, role: str, user_id: str = None, email: str = None) -> str`

Creates a new user session with JWT token.

**Parameters:**
- `username` (str): The username for the session
- `role` (str): User role ("user" or "admin")
- `user_id` (str, optional): Unique user identifier
- `email` (str, optional): User's email address

**Returns:**
- `session_id` (str): Unique session identifier

**Example:**
```python
session_id = create_session(
    username="john_doe",
    role="user",
    user_id="uuid-here",
    email="john@example.com"
)
```

### `validate_session(session_id: str) -> Dict[str, Any]`

Validates an existing session.

**Parameters:**
- `session_id` (str): The session ID to validate

**Returns:**
- Session data dict if valid, None if invalid

**Session Data Structure:**
```python
{
    "username": "john_doe",
    "role": "user" | "admin",
    "user_id": "unique-uuid",
    "email": "john@example.com",
    "created_at": 1704567890,
    "last_activity": 1704567890
}
```

## User Management Functions

### `create_user(username: str, email: str, password: str, role: str = "user") -> Tuple[bool, str]`

Creates a new user account.

**Parameters:**
- `username` (str): Unique username (alphanumeric and underscore only)
- `email` (str): Valid email address
- `password` (str): Password meeting security requirements
- `role` (str): User role, defaults to "user"

**Returns:**
- `success` (bool): Whether user creation succeeded
- `message` (str): Success message or error description

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

**Example:**
```python
from utils.auth import create_user

success, message = create_user(
    username="jane_doe",
    email="jane@example.com",
    password="SecurePass123",
    role="user"
)
```

### `list_users(include_inactive: bool = False) -> List[Dict[str, Any]]`

Lists all users in the system.

**Parameters:**
- `include_inactive` (bool): Whether to include deactivated users

**Returns:**
- List of user dictionaries (without passwords)

**Example:**
```python
users = list_users(include_inactive=True)
for user in users:
    print(f"{user['username']} - {user['role']} - Active: {user['is_active']}")
```

### `update_user_role(user_id: str, new_role: str) -> Tuple[bool, str]`

Updates a user's role.

**Parameters:**
- `user_id` (str): The user's unique identifier
- `new_role` (str): New role ("user" or "admin")

**Returns:**
- `success` (bool): Whether update succeeded
- `message` (str): Success or error message

**Protection:** Cannot change role if it would leave no admin users.

### `toggle_user_status(user_id: str) -> Tuple[bool, str]`

Activates or deactivates a user account.

**Parameters:**
- `user_id` (str): The user's unique identifier

**Returns:**
- `success` (bool): Whether toggle succeeded
- `message` (str): Success or error message

**Protection:** Cannot deactivate the last active admin.

### `reset_user_password(user_id: str, new_password: str) -> Tuple[bool, str]`

Resets a user's password (admin function).

**Parameters:**
- `user_id` (str): The user's unique identifier
- `new_password` (str): New password meeting requirements

**Returns:**
- `success` (bool): Whether reset succeeded
- `message` (str): Success or error message

### `delete_user(user_id: str) -> Tuple[bool, str]`

Permanently deletes a user account.

**Parameters:**
- `user_id` (str): The user's unique identifier

**Returns:**
- `success` (bool): Whether deletion succeeded
- `message` (str): Success or error message

**Protection:** Cannot delete the last admin user.

## User Store Functions

### `UserStore.add_user(user_data: Dict[str, Any]) -> bool`

Adds a new user to the store.

**Parameters:**
- `user_data` (dict): Complete user information

**Required Fields:**
- `user_id`: Unique identifier
- `username`: Unique username
- `email`: Unique email
- `password_hash`: Bcrypt hashed password
- `role`: User role
- `created_at`: ISO timestamp
- `last_login`: ISO timestamp or None
- `is_active`: Boolean status

### `UserStore.authenticate(username_or_email: str, password: str) -> Optional[Dict[str, Any]]`

Authenticates a user and returns their data.

**Parameters:**
- `username_or_email` (str): Username or email
- `password` (str): Plain text password to verify

**Returns:**
- User data dict if authenticated, None if failed

### `UserStore.get_user(user_id: str = None, username: str = None, email: str = None) -> Optional[Dict[str, Any]]`

Retrieves a user by ID, username, or email.

**Parameters:**
- `user_id` (str, optional): User's unique ID
- `username` (str, optional): User's username
- `email` (str, optional): User's email

**Returns:**
- User data dict if found, None if not found

## Security Considerations

### Password Hashing
- All passwords are hashed using bcrypt with salt
- Plain text passwords are never stored
- Password comparison is timing-attack resistant

### Session Security
- Sessions use JWT tokens with configurable expiration
- JWT_SECRET must be set in environment
- Sessions expire after 30 minutes of inactivity
- CSRF protection available with JWT tokens

### Rate Limiting
- Failed login attempts tracked per username
- Configurable rate limits via environment variables
- Prevents brute force attacks

### Data Protection
- File-based storage uses thread-safe locking
- No SQL injection possible (no SQL used)
- Input validation on all user inputs
- Case-insensitive username/email matching

## Error Handling

All functions return structured errors:

```python
# Authentication errors
"Invalid username/email or password"
"Account is inactive"
"Too many failed login attempts"

# User creation errors
"Username already exists"
"Email already in use"
"Invalid password format"
"Username can only contain letters, numbers, and underscores"

# User management errors
"User not found"
"Cannot delete the last admin user"
"Cannot deactivate the last admin user"
"Cannot remove admin role from the last admin"
```

## Environment Variables

Required for authentication system:
- `JWT_SECRET`: Secret key for JWT token generation (required)
- `ADMIN_PASSWORD`: Password for default admin account (required)
- `RATE_LIMIT_REQUESTS`: Max requests per window (default: 100)
- `RATE_LIMIT_WINDOW_SECONDS`: Rate limit window (default: 3600)