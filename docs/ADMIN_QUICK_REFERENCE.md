# Admin Quick Reference Guide

**Version**: 1.0  
**Last Updated**: July 28, 2025  
**Target Audience**: System Administrators

## 🚀 Quick Admin Tasks

### Current System Users
```
Admin User:
  Username: admin
  Email: admin@safesteps.local  
  Password: Admin@SafeSteps2024 (default)
  Role: admin

Test User:
  Username: testuser
  Email: testuser@safesteps.local
  Password: [Contact dev team - bcrypt hashed]
  Role: user
```

## 🔧 Common Admin Operations

### Reset User Password (Python Console)
```python
# Connect to user store
from utils.auth import reset_user_password
from utils.user_store import user_store

# Get user ID
user = user_store.get_user_by_username("testuser")
print(f"User ID: {user.user_id}")

# Reset password (must meet requirements: 8+ chars, uppercase, lowercase, number)
success = reset_user_password(user.user_id, "NewPass123!")
print(f"Password reset: {'Success' if success else 'Failed'}")
```

### Create New User (Python Console)
```python
from utils.auth import create_user

# Create new user
user = create_user(
    username="newuser",
    email="newuser@safesteps.local", 
    password="SecurePass123!",
    role="user"  # or "admin"
)

if user:
    print(f"Created user: {user.username} with ID: {user.user_id}")
else:
    print("User creation failed - check if username/email already exists")
```

### List All Users (Python Console)
```python
from utils.auth import list_users

# List all active users
users = list_users(include_inactive=False)
for user in users:
    print(f"{user.username} ({user.email}) - {user.role} - Active: {user.is_active}")

# List all users including inactive
all_users = list_users(include_inactive=True)
print(f"\nTotal users: {len(all_users)}")
```

### Toggle User Active Status (Python Console)
```python
from utils.auth import toggle_user_status
from utils.user_store import user_store

# Get user
user = user_store.get_user_by_username("testuser")

# Toggle status
updated_user = toggle_user_status(user.user_id)
print(f"User {updated_user.username} is now {'active' if updated_user.is_active else 'inactive'}")
```

## 🏥 System Health Checks

### Check Environment Health
```python
from config import get_environment_health

health = get_environment_health()
print(f"System Status: {health['status']}")

if health['issues']:
    print("\nCritical Issues:")
    for issue in health['issues']:
        print(f"  • {issue}")

if health['warnings']:
    print("\nWarnings:")
    for warning in health['warnings']:
        print(f"  • {warning}")
```

### Verify Authentication System
```python
from utils.auth import login_with_credentials

# Test admin login
success, role, error = login_with_credentials("admin", "Admin@SafeSteps2024")
print(f"Admin login test: {'SUCCESS' if success else 'FAILED'}")
if error:
    print(f"Error: {error}")

# Test any user credentials
username = "testuser"  # or email
password = "TestPassword123!"  # known password
success, role, error = login_with_credentials(username, password)
print(f"User login test: {'SUCCESS' if success else 'FAILED'}")
```

### Check Template System
```python
from utils.storage import StorageManager

storage = StorageManager()
templates = storage.list_template_files()
print(f"Available templates: {len(templates)}")
for template in templates:
    print(f"  • {template}")
```

## 🚨 Emergency Procedures

### Reset Admin Password (Emergency Access)
If you're locked out of the admin account:

1. **Access server/container directly**
2. **Run Python console in application directory**
3. **Execute password reset**:
```python
import os
import sys
sys.path.append('/home/marsh/coding/Safesteps')

from utils.user_store import user_store

# Find admin user
admin = user_store.get_user_by_username("admin")
print(f"Admin user ID: {admin.user_id}")

# Reset to default password
success = user_store.update_password(admin.user_id, "Admin@SafeSteps2024")
print(f"Password reset: {'Success' if success else 'Failed'}")
```

### Create Emergency Admin User
If no admin users exist:

```python
from utils.auth import create_user

# Create emergency admin
emergency_admin = create_user(
    username="emergency",
    email="emergency@safesteps.local",
    password="Emergency123!",
    role="admin"
)

print(f"Emergency admin created: {emergency_admin.username if emergency_admin else 'FAILED'}")
```

### System Recovery
If authentication system is completely broken:

1. **Check JWT_SECRET environment variable**:
```bash
echo $JWT_SECRET
# If empty, set it:
export JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

2. **Verify user storage file**:
```bash
ls -la /home/marsh/coding/Safesteps/data/storage/users.json
# If missing or corrupted, restore from backup or reinitialize
```

3. **Restart application** after fixes

## 📊 User Management Best Practices

### Password Requirements
All passwords must have:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter  
- At least one number

### Security Guidelines
- **Change default passwords** immediately in production
- **Use unique passwords** for each admin account
- **Regularly audit user accounts** (monthly recommended)
- **Monitor failed login attempts** for suspicious activity
- **Keep admin accounts to minimum required**

### Account Lifecycle
1. **New User**: Create with temporary password, require change on first login
2. **Active User**: Regular access, monitor for unusual activity
3. **Departing User**: Deactivate immediately, don't delete (for audit trail)
4. **Cleanup**: Archive or delete inactive accounts after retention period

## 🔍 Troubleshooting Common Issues

### "User not found" errors
```python
# Check exact username/email format
from utils.user_store import user_store
users = user_store._read_users()
for user_id, user_data in users.items():
    print(f"ID: {user_id}")
    print(f"Username: '{user_data['username']}'")
    print(f"Email: '{user_data['email']}'")
    print("---")
```

### "Too many login attempts" errors
```python
# Reset rate limiting for specific user
from utils.auth import rate_limiter
rate_limiter.reset("login_attempt_username")  # Replace with actual username
print("Rate limit reset for user")
```

### User file corruption
```bash
# Backup current file
cp /path/to/users.json /path/to/users.json.backup

# Check file format
python -c "import json; print(json.load(open('/path/to/users.json')))"

# If corrupted, restore from backup or reinitialize
```

## 📞 Support Contacts

### For Technical Issues
- **Development Team**: Authentication system problems
- **System Administrator**: Server/deployment issues
- **Security Team**: Security policy questions

### For User Management
- **HR Department**: New user creation requests
- **IT Help Desk**: Password reset requests
- **Department Managers**: User role change requests

## 📋 Maintenance Checklist

### Daily
- [ ] Check system health status
- [ ] Review failed login attempts
- [ ] Monitor active user sessions

### Weekly  
- [ ] Audit user account list
- [ ] Check for inactive/unused accounts
- [ ] Review access logs for anomalies

### Monthly
- [ ] Password policy compliance check
- [ ] User role validation
- [ ] System security update review
- [ ] Backup user database

### Quarterly
- [ ] Complete user access review
- [ ] Security policy update
- [ ] System performance analysis
- [ ] Documentation updates

---

**Emergency Contact**: System Administrator  
**Documentation Location**: `/home/marsh/coding/Safesteps/docs/`  
**User Database**: `/home/marsh/coding/Safesteps/data/storage/users.json`  
**Last Security Review**: July 28, 2025