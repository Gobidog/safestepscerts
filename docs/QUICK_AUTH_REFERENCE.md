# Quick Authentication Reference - SafeSteps Certificate Generator

## ✅ AUTHENTICATION FIXED - Working Credentials

### Admin Account
- **Username**: `admin` or `admin@safesteps.local`
- **Password**: `Admin@SafeSteps2024`
- **Access Level**: Full administrative privileges
  - User management
  - Template management
  - System configuration
  - All certificate functions

### Test User Account
- **Username**: `testuser` or `testuser@safesteps.local`
- **Password**: `UserPass123`
- **Access Level**: Standard user
  - Certificate generation
  - Profile management
  - View own activity

## Password Reset Utility

If you need to reset passwords, use the provided utility:

```bash
python utils/reset_passwords.py
```

This utility:
- Creates automatic backup of users.json
- Updates password hashes securely
- Verifies changes immediately
- Maintains data integrity

## Troubleshooting Login Issues

### Cannot Login?
1. **Check credentials exactly** - passwords are case-sensitive
2. **Clear browser cache** - Ctrl+F5 or Cmd+Shift+R
3. **Verify JWT_SECRET** is set in environment
4. **Check users.json** exists in data/storage/

### After Deployment
1. Ensure JWT_SECRET environment variable is set
2. Verify users.json is present
3. Test both admin and user logins
4. Check session persistence works

## Security Notes
- Passwords are hashed with bcrypt (12 rounds)
- Sessions use JWT tokens with 30-minute timeout
- Failed login attempts are rate-limited
- CSRF protection enabled by default

## Environment Variables
```bash
# Required for authentication
JWT_SECRET=your-secret-here-minimum-32-chars
ADMIN_PASSWORD=Admin@SafeSteps2024  # Must match users.json
USER_PASSWORD=UserPass123           # For reference only
```

---
Last Updated: 2025-07-28
Status: FULLY OPERATIONAL