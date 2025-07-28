# Admin User Management Guide

## Overview

As an administrator of SafeSteps Certificate Generator, you have access to comprehensive user management features. This guide covers all aspects of managing user accounts.

## Accessing User Management

1. Log in with your admin credentials
2. Navigate to the Admin Panel from the sidebar
3. Select the "User Management" tab

## Default Admin Account

On first deployment, a default admin account is automatically created:
- **Username**: `admin`
- **Email**: `admin@safesteps.local`
- **Password**: Set via `ADMIN_PASSWORD` environment variable

⚠️ **Important**: Change the default admin password immediately after first login.

## User Management Features

### Viewing Users

The "User List" tab displays all users with:
- Username
- Email address
- Role (user/admin)
- Account status (active/inactive)
- Last login timestamp
- Action buttons for management

### Creating New Users

1. Click the "Add User" tab
2. Fill in the required information:
   - **Username**: Unique identifier (no spaces, case-insensitive)
   - **Email**: Valid email address (must be unique)
   - **Password**: Must meet security requirements
   - **Role**: Select "user" or "admin"
3. Click "Create User"

**Password Requirements**:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

### Editing Users

From the User List, you can:

#### Change User Role
1. Click "Change to Admin" or "Change to User" button
2. Confirm the role change
3. The change takes effect immediately

#### Reset Password
1. Click "Reset Password" for the user
2. Enter a new password meeting requirements
3. Click "Update Password"
4. Inform the user of their new password

#### Activate/Deactivate Users
1. Click "Deactivate" to disable a user account
2. Click "Activate" to re-enable a disabled account
3. Deactivated users cannot log in but their data is preserved

### Deleting Users

1. Click the "Delete" button (❌) next to the user
2. Confirm the deletion
3. The user and all associated data will be permanently removed

⚠️ **Protection**: You cannot delete the last admin user. Ensure at least one other admin exists before deleting an admin account.

## Best Practices

### Account Security
1. **Regular Audits**: Review user list monthly
2. **Deactivate Unused Accounts**: Disable accounts for users who no longer need access
3. **Strong Passwords**: Enforce strong passwords for all accounts
4. **Minimal Admin Accounts**: Only grant admin access when necessary

### User Onboarding
1. Create account with temporary password
2. Provide username and password securely
3. Instruct user to note their credentials
4. Guide them through first login

### Account Maintenance
1. **Monitor Last Login**: Identify inactive accounts
2. **Regular Password Updates**: Encourage users to update passwords
3. **Role Reviews**: Ensure users have appropriate access levels
4. **Clean Up**: Remove accounts no longer needed

## Troubleshooting

### Cannot Create User
- **"Username already exists"**: Choose a different username
- **"Email already in use"**: User may already have an account
- **"Invalid password"**: Ensure password meets all requirements

### Cannot Delete User
- **"Cannot delete last admin"**: Create another admin account first
- **"User not found"**: User may have already been deleted

### User Cannot Login
1. Check if account is active
2. Verify username/email is correct
3. Reset password if necessary
4. Check for rate limiting (too many failed attempts)

## Security Considerations

### Admin Responsibilities
- Protect admin credentials
- Regular security audits
- Monitor for suspicious activity
- Maintain principle of least privilege

### Data Protection
- User passwords are bcrypt hashed
- Sessions secured with JWT tokens
- All actions are logged
- File access is role-based

## User Storage

User data is stored in `data/storage/users.json` with:
- Encrypted passwords (bcrypt)
- Unique identifiers
- Activity timestamps
- Thread-safe file locking

## Rate Limiting

- Failed login attempts are tracked per username
- Automatic temporary lockout after multiple failures
- Protects against brute force attacks

## Audit Trail

All admin actions are logged:
- User creation/deletion
- Role changes
- Password resets
- Login attempts

## Emergency Procedures

### Lost Admin Access
1. Access server directly
2. Set new `ADMIN_PASSWORD` environment variable
3. Restart application
4. Default admin account will be recreated

### Bulk User Management
For large-scale operations:
1. Access `data/storage/users.json` directly
2. Make backups before modifications
3. Ensure JSON structure is maintained
4. Restart application after changes

## Integration with Certificate Generation

- Users can only access certificate generation features
- Admins have full access to all features
- Role-based template access can be configured
- Usage statistics tracked per user