# Security Fixes Documentation

## Overview
This document details the security improvements implemented to address session persistence and authentication vulnerabilities in the Certificate Generator application.

## Critical Security Issues Fixed

### 1. Session Loss on Application Restart

**Problem**: Sessions were being lost whenever the application restarted because the JWT_SECRET was randomly generated on each startup.

**Solution**: JWT_SECRET is now loaded from environment variables, ensuring consistency across restarts.

**Implementation**:
```python
# utils/auth.py - Line 22
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
if not os.getenv("JWT_SECRET"):
    logger.warning("JWT_SECRET not set in environment - sessions will be lost on restart!")
```

**Impact**: Sessions now persist across application restarts, container deployments, and scaling events.

### 2. Default Password Vulnerability

**Problem**: The application could be deployed with default passwords, creating a security vulnerability.

**Solution**: Passwords must now be set via environment variables, and the application fails to start without them.

**Implementation**:
```python
# config.py - AuthConfig class
def __post_init__(self):
    if not self.user_password:
        raise ValueError("USER_PASSWORD environment variable must be set")
    if not self.admin_password:
        raise ValueError("ADMIN_PASSWORD environment variable must be set")
```

**Impact**: Prevents accidental deployment with default or empty passwords.

### 3. CSRF Protection Enhancement

**Problem**: CSRF tokens were not properly validated due to changing JWT secrets.

**Solution**: CSRF tokens are now generated and validated using the persistent JWT_SECRET.

**Implementation**:
```python
# utils/auth.py - generate_csrf_token()
payload = {
    "session_id": user.get("session_id"),
    "username": user.get("username"),
    "exp": datetime.utcnow() + timedelta(hours=1),
    "iat": datetime.utcnow()
}
token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
```

## Security Configuration Guide

### Required Environment Variables

1. **JWT_SECRET** (Critical for session persistence)
   - Minimum 32 characters
   - Must be consistent across all instances
   - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

2. **USER_PASSWORD** (Required)
   - Minimum 8 characters
   - Must contain uppercase, lowercase, and numbers
   - No default value allowed

3. **ADMIN_PASSWORD** (Required)
   - Same requirements as USER_PASSWORD
   - Should be different from USER_PASSWORD

### Example Configuration

```bash
# .env file
JWT_SECRET=x0atkv9WYGbOmuqvb6rgMDVFA4jXiAz2_qqn8wVdfgE
USER_PASSWORD=SecureUser123!
ADMIN_PASSWORD=SecureAdmin456!
ENABLE_CSRF_PROTECTION=true
```

## Testing Security Fixes

Run the security test suite to verify all fixes are working:

```bash
python -m pytest tests/test_security_fixes.py -v
```

### Test Coverage

1. **JWT Secret Persistence**
   - Verifies JWT_SECRET loads from environment
   - Confirms warning when not set
   - Tests session token validation

2. **Password Requirements**
   - Tests application fails without passwords
   - Validates password strength requirements
   - Confirms bcrypt hashing implementation

3. **CSRF Protection**
   - Tests token generation with persistent secret
   - Validates token verification process
   - Confirms session binding

## Production Deployment Checklist

Before deploying to production:

- [ ] Generate unique JWT_SECRET (32+ characters)
- [ ] Set strong USER_PASSWORD (not default)
- [ ] Set strong ADMIN_PASSWORD (not default)
- [ ] Enable CSRF protection
- [ ] Configure session timeout appropriately
- [ ] Set up monitoring for failed login attempts
- [ ] Test session persistence after deployment

## Monitoring and Alerts

### Key Security Events to Monitor

1. **JWT_SECRET Not Set Warning**
   ```
   logger.warning("JWT_SECRET not set in environment - sessions will be lost on restart!")
   ```

2. **Failed Login Attempts**
   ```
   logger.warning(f"Failed login attempt for role: {role}")
   ```

3. **Session Hijacking Detection**
   ```
   logger.warning("Potential session hijacking detected")
   ```

4. **CSRF Token Failures**
   ```
   logger.warning("CSRF token validation error: {e}")
   ```

### Recommended Monitoring Setup

```bash
# Create alerts in Google Cloud Logging
gcloud logging metrics create jwt_secret_warning \
  --description="JWT_SECRET not configured" \
  --log-filter='jsonPayload.message=~"JWT_SECRET not set"'

gcloud logging metrics create failed_auth \
  --description="Authentication failures" \
  --log-filter='jsonPayload.message=~"Failed login attempt"'
```

## Migration Guide

### For Existing Deployments

1. **Generate JWT_SECRET**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Update Environment Variables**:
   ```bash
   # Cloud Run
   gcloud run services update certificate-generator \
     --set-env-vars="JWT_SECRET=your-generated-secret"
   
   # Docker
   docker run -e JWT_SECRET="your-generated-secret" ...
   
   # Local .env
   echo "JWT_SECRET=your-generated-secret" >> .env
   ```

3. **Note**: All existing sessions will be invalidated after setting JWT_SECRET for the first time.

## Security Best Practices

1. **JWT_SECRET Management**
   - Store in secure secret management system
   - Rotate only during planned maintenance
   - Never commit to version control
   - Use different secrets for different environments

2. **Password Policies**
   - Enforce minimum complexity requirements
   - Implement regular password rotation
   - Use different passwords for each environment
   - Consider implementing MFA for admin accounts

3. **Session Security**
   - Configure appropriate session timeouts
   - Monitor for suspicious session activity
   - Implement IP-based session validation
   - Log all authentication events

## Troubleshooting

### Sessions Lost After Deployment

**Symptom**: Users are logged out after application restart

**Cause**: JWT_SECRET not set in environment

**Solution**:
1. Set JWT_SECRET in environment variables
2. Ensure it's the same across all instances
3. Verify with: `echo $JWT_SECRET`

### Cannot Start Application

**Symptom**: Application crashes with "USER_PASSWORD environment variable must be set"

**Cause**: Required passwords not configured

**Solution**:
1. Set USER_PASSWORD in environment
2. Set ADMIN_PASSWORD in environment
3. Ensure passwords meet complexity requirements

### CSRF Token Validation Failures

**Symptom**: Form submissions fail with CSRF errors

**Cause**: JWT_SECRET changed or sessions corrupted

**Solution**:
1. Verify JWT_SECRET is consistent
2. Have users log out and log back in
3. Check session storage integrity