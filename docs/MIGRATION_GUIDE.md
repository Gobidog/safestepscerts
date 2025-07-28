# Migration Guide: Password-Only to Username/Email Authentication

## ✅ UPDATE (July 2025): Authentication System Fully Fixed

**IMPORTANT**: The authentication system has been completely fixed and is now working correctly with the following credentials:
- **Admin**: `admin` / `Admin@SafeSteps2024`
- **Test User**: `testuser` / `UserPass123`

If you're experiencing login issues, see the [Quick Authentication Reference](QUICK_AUTH_REFERENCE.md) for the current working credentials.

## Overview

This guide helps you migrate from the old password-only authentication system to the new username/email + password system in SafeSteps Certificate Generator.

## Migration Timeline

1. **Pre-migration** (Current state): Password-only authentication
2. **Migration Phase**: Both systems work (backward compatible)
3. **Post-migration**: Username/email authentication only

## Pre-Migration Checklist

- [ ] Backup current deployment configuration
- [ ] Note current ADMIN_PASSWORD and USER_PASSWORD values
- [ ] Ensure JWT_SECRET is set (required for new system)
- [ ] Schedule migration during low-usage period
- [ ] Notify users of upcoming changes

## Migration Steps

### Step 1: Update Environment Variables

The new system requires JWT_SECRET and uses ADMIN_PASSWORD differently:

```bash
# Old configuration
USER_PASSWORD=userpass123
ADMIN_PASSWORD=adminpass456

# New configuration (add JWT_SECRET)
JWT_SECRET=your-secure-jwt-secret-here  # REQUIRED!
ADMIN_PASSWORD=adminpass456  # Now creates default admin user
# USER_PASSWORD is deprecated but still works during migration
```

Generate a secure JWT_SECRET:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 2: Deploy Updated Application

Deploy the new version with updated environment variables. The application will:
1. Detect no users exist
2. Create default admin account:
   - Username: `admin`
   - Email: `admin@safesteps.local`
   - Password: Value from `ADMIN_PASSWORD`

### Step 3: First Admin Login

1. Navigate to the login page
2. Log in using:
   - Username: `admin` (or email: `admin@safesteps.local`)
   - Password: Your `ADMIN_PASSWORD` value
3. You'll see the new dashboard with user management

### Step 4: Create User Accounts

For each person who had access via USER_PASSWORD:

1. Go to Admin Panel → User Management
2. Click "Add User" tab
3. Create account with:
   - Unique username
   - Email address
   - Secure password (you set it)
   - Role: "user"
4. Securely communicate credentials to user

### Step 5: Create Additional Admin Accounts

For each person who had ADMIN_PASSWORD:

1. Follow same process as Step 4
2. Set Role: "admin"
3. Verify they can access admin functions

### Step 6: Test Authentication

Before removing old system:
1. Test login with username + password
2. Test login with email + password
3. Verify certificate generation works
4. Verify admin functions work

### Step 7: Remove Old Authentication (Optional)

Once all users are migrated:

1. Remove `USER_PASSWORD` from environment
2. Update any documentation
3. The old password-only system will stop working

## Backward Compatibility

During migration, both authentication methods work:

- **Old method**: Enter just the password in username field
- **New method**: Enter username/email and password

This allows gradual migration without service disruption.

## User Communication Template

Send to all users:

```
Subject: Important: SafeSteps Login Update

Dear SafeSteps User,

We're upgrading our security with individual user accounts. 

What's changing:
- You'll now have a personal username and password
- Enhanced security with individual access tracking
- Same certificate generation features you rely on

Your new credentials:
- Username: [username]
- Password: [temporary_password]
- Login URL: [your_url]

Please log in and familiarize yourself with the new system.

Questions? Contact [admin_email]
```

## Rollback Plan

If issues occur, you can rollback:

1. Keep `USER_PASSWORD` and `ADMIN_PASSWORD` in environment
2. Users can still use old password-only method
3. Fix issues while both systems work
4. Retry migration when ready

## Common Migration Issues

### Issue: "JWT_SECRET not configured"
**Solution**: Set JWT_SECRET environment variable and restart

### Issue: Lost admin access
**Solution**: 
1. Set new ADMIN_PASSWORD in environment
2. Restart application
3. Default admin account recreated

### Issue: Users can't login
**Causes**:
- Wrong username/email
- Password not communicated correctly
- Account not created yet
- Account deactivated

**Solution**: Check user list in admin panel

### Issue: Sessions lost on restart
**Cause**: JWT_SECRET changed or not persistent
**Solution**: Use same JWT_SECRET across restarts

## Data Migration

### User Data Location
- New system stores users in: `data/storage/users.json`
- Format:
```json
{
  "users": {
    "user-id": {
      "user_id": "unique-id",
      "username": "john_doe",
      "email": "john@example.com",
      "password_hash": "$2b$12$...",
      "role": "user",
      "created_at": "2024-01-20T10:00:00",
      "last_login": "2024-01-20T15:30:00",
      "is_active": true
    }
  }
}
```

### Bulk User Import (Advanced)

For many users, create import script:

```python
from utils.auth import create_user
import csv

# Read users from CSV
with open('users_to_import.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        success, message = create_user(
            username=row['username'],
            email=row['email'],
            password=row['temp_password'],
            role=row['role']
        )
        print(f"{row['username']}: {message}")
```

## Post-Migration

### Security Hardening
1. Enforce password complexity
2. Implement password expiration (manual)
3. Regular access reviews
4. Monitor failed login attempts

### User Training
- Provide login instructions
- Explain username vs email options
- Show password requirements
- Demonstrate logout process

### Monitoring
- Check login success rates
- Monitor for lockouts
- Review user activity
- Address issues quickly

## Cloud-Specific Considerations

### Streamlit Cloud
1. Add JWT_SECRET to Secrets
2. Update ADMIN_PASSWORD
3. Remove USER_PASSWORD when ready

### Google Cloud Run
```bash
gcloud run services update certificate-generator \
  --set-env-vars JWT_SECRET=your-secret,ADMIN_PASSWORD=new-admin-pass \
  --remove-env-vars USER_PASSWORD
```

### Docker Deployments
Update your docker-compose.yml or run command:
```yaml
environment:
  - JWT_SECRET=${JWT_SECRET}
  - ADMIN_PASSWORD=${ADMIN_PASSWORD}
  # Remove USER_PASSWORD when ready
```

## Success Criteria

Migration is complete when:
- [ ] All users have individual accounts
- [ ] Old password-only access disabled
- [ ] Users successfully logging in
- [ ] Admin can manage users
- [ ] No authentication errors in logs
- [ ] Documentation updated

## Getting Help

If you encounter issues:
1. Check application logs
2. Verify environment variables
3. Test with default admin account
4. Review this guide
5. Contact support with error details