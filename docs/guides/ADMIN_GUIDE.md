# Administrator Guide - SafeSteps Certificate Generator

## Table of Contents

1. [Administrator Overview](#administrator-overview)
2. [Initial Setup](#initial-setup)
3. [Template Management](#template-management)
4. [User Management](#user-management)
5. [System Monitoring](#system-monitoring)
6. [Security Management](#security-management)
7. [Troubleshooting Admin Issues](#troubleshooting-admin-issues)
8. [Best Practices](#best-practices)

---

## Administrator Overview

As an administrator, you have full access to:
- Upload and manage certificate templates
- Change user and admin passwords
- Monitor system usage and performance
- View activity logs
- Test certificate generation
- Manage storage settings

### Admin Responsibilities

1. **Template Management**: Keep templates up-to-date
2. **Access Control**: Manage user passwords securely
3. **System Health**: Monitor performance and storage
4. **Security**: Ensure secure configuration
5. **Support**: Help users troubleshoot issues

---

## Initial Setup

### Environment Configuration

1. **Set Critical Environment Variables**:
```bash
# Generate secure JWT secret (REQUIRED)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in your environment
export JWT_SECRET=<generated_secret>
export USER_PASSWORD=<secure_user_password>
export ADMIN_PASSWORD=<secure_admin_password>
```

2. **Configure Storage** (for production):
```bash
# Google Cloud Storage
export GCS_BUCKET_NAME=your-bucket-name
export GCS_PROJECT_ID=your-project-id

# Or use local storage for development
export USE_LOCAL_STORAGE=true
```

3. **Security Settings**:
```bash
# Enable CSRF protection (recommended)
export ENABLE_CSRF_PROTECTION=true

# Set session timeout (minutes)
export SESSION_TIMEOUT_MINUTES=30

# Configure rate limiting
export RATE_LIMIT_REQUESTS=100
export RATE_LIMIT_WINDOW_SECONDS=3600
```

### First Login

1. Navigate to the application URL
2. Enter the admin password
3. You'll see the admin dashboard

---

## Template Management

### Understanding Templates

Templates are PDF files with form fields that get filled with data:
- Must be valid PDF with form fields
- Fields are mapped to spreadsheet columns
- Support any field names (flexible mapping)

### Uploading Templates

1. **Navigate to Admin Panel**
2. **Upload New Template Section**:
   - Choose PDF file (max 10MB)
   - Enter template name (descriptive)
   - Select associated course
   - Upload

3. **Template Requirements**:
   - PDF with fillable form fields
   - Common fields: FirstName, LastName, Date, Course
   - Fields can have any names
   - Form fields will be flattened during generation

### Managing Existing Templates

#### View Templates
- Lists all uploaded templates
- Shows file size and upload date
- Displays associated course

#### Test Templates
1. Select template to test
2. System generates sample certificate
3. Uses dummy data: "John Doe"
4. Download to verify formatting

#### Download Templates
- Click download icon
- Saves current version
- Useful for backup

#### Delete Templates
1. Click delete button
2. Confirm deletion
3. Cannot be undone
4. Update users about removal

### Template Best Practices

1. **Naming Convention**:
   - Use descriptive names
   - Include version/date
   - Example: "Safety_Certificate_v2_2025.pdf"

2. **Field Standards**:
   - Use consistent field names
   - Document field mappings
   - Test before deployment

3. **Quality Control**:
   - Test with sample data
   - Check all text fits properly
   - Verify fonts embed correctly

---

## User Management

### Password Management

#### Changing User Password
1. Go to Admin Panel
2. Find "Change User Password"
3. Enter new password (min 8 chars)
4. Must include:
   - Uppercase letter
   - Lowercase letter
   - Number
5. Save changes

#### Changing Admin Password
1. Similar process as user
2. More critical - update securely
3. Notify other admins
4. Update documentation

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- No dictionary words recommended

### Access Control Best Practices

1. **Regular Updates**:
   - Change passwords quarterly
   - After staff changes
   - If compromise suspected

2. **Secure Distribution**:
   - Never email passwords
   - Use secure channels
   - Consider password manager

3. **Documentation**:
   - Track password changes
   - Note who has access
   - Plan for succession

---

## System Monitoring

### Usage Statistics

The admin dashboard shows:
- Total certificates generated
- Active sessions count
- Storage usage
- Recent activity

### Activity Logs

Monitor for:
- Login attempts (successful/failed)
- Certificate generation
- Template uploads/changes
- Password changes
- Errors and warnings

### Performance Metrics

Watch for:
- Generation speed (target: 30-60/second)
- Memory usage
- Storage capacity
- Error rates

### Storage Management

#### Local Storage
- Check disk space regularly
- Clean old temporary files
- Monitor templates directory

#### Google Cloud Storage
- Monitor bucket usage
- Check access permissions
- Review costs monthly

---

## Security Management

### Critical Security Tasks

1. **JWT Secret Management**:
   - MUST be set in environment
   - Never change in production
   - Same across all instances
   - Store securely

2. **Regular Security Audits**:
   - Review access logs
   - Check for unusual activity
   - Verify CSRF protection enabled
   - Test rate limiting

3. **Session Security**:
   - Monitor active sessions
   - Check for session hijacking
   - Review timeout settings
   - Clear old sessions

### Security Checklist

Daily:
- [ ] Check error logs
- [ ] Monitor active sessions
- [ ] Review failed logins

Weekly:
- [ ] Review activity logs
- [ ] Check storage usage
- [ ] Verify backups

Monthly:
- [ ] Security audit
- [ ] Update passwords
- [ ] Review user access
- [ ] Test disaster recovery

### Incident Response

If security incident suspected:
1. **Immediate Actions**:
   - Change all passwords
   - Review recent logs
   - Check for data breach
   - Notify stakeholders

2. **Investigation**:
   - Analyze activity logs
   - Check system integrity
   - Review access patterns
   - Document findings

3. **Recovery**:
   - Restore from backup if needed
   - Update security measures
   - Communicate with users
   - Implement preventions

---

## Troubleshooting Admin Issues

### Common Admin Problems

#### Cannot Upload Template

**Causes**:
- File too large (>10MB)
- Not a valid PDF
- No form fields in PDF
- Storage permissions

**Solutions**:
- Reduce PDF size
- Verify PDF has form fields
- Check storage configuration
- Review error logs

#### Templates Not Persisting

**Issue**: Templates disappear after restart

**Solution**:
- Configure GCS properly
- Check bucket permissions
- Verify environment variables
- Use local storage for testing

#### Password Changes Not Working

**Causes**:
- Weak password
- Session timeout
- CSRF token expired

**Solutions**:
- Meet password requirements
- Re-login and try again
- Refresh page for new token

#### High Memory Usage

**Symptoms**:
- Slow performance
- Generation failures
- System crashes

**Solutions**:
- Limit concurrent users
- Reduce batch sizes
- Restart application
- Increase server resources

### Advanced Troubleshooting

#### Enable Debug Mode
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

#### Check Logs
```bash
# View recent errors
grep ERROR app.log | tail -50

# Monitor in real-time
tail -f app.log | grep -E "(ERROR|WARNING)"
```

#### Storage Diagnostics
```bash
# Check local storage
du -sh ./local_storage/*

# Verify GCS access
gsutil ls gs://your-bucket/
```

---

## Best Practices

### Daily Operations

1. **Morning Checks**:
   - Review overnight logs
   - Check system health
   - Verify template availability
   - Monitor storage space

2. **User Support**:
   - Respond to issues promptly
   - Document common problems
   - Create FAQ for users
   - Regular training sessions

### Template Management

1. **Version Control**:
   - Keep template backups
   - Document changes
   - Test before deploying
   - Maintain changelog

2. **Organization**:
   - Clear naming scheme
   - Group by course/type
   - Remove old versions
   - Regular cleanup

### Security Practices

1. **Access Control**:
   - Principle of least privilege
   - Regular password rotation
   - Monitor usage patterns
   - Document access changes

2. **Data Protection**:
   - No sensitive data in logs
   - Regular security audits
   - Encrypted connections only
   - Secure backup storage

### Performance Optimization

1. **Resource Management**:
   - Monitor peak usage times
   - Plan capacity accordingly
   - Optimize template sizes
   - Regular maintenance windows

2. **User Experience**:
   - Keep templates updated
   - Clear error messages
   - Fast response times
   - Regular user feedback

### Documentation

Maintain:
- Template field mappings
- Password change log
- System configuration
- Troubleshooting guide
- User feedback/issues

### Backup Strategy

1. **Regular Backups**:
   - Templates: Daily
   - Configuration: Weekly
   - Logs: Monthly archive

2. **Recovery Testing**:
   - Test restore process
   - Document procedures
   - Update contact info
   - Practice scenarios

---

## Emergency Contacts

Maintain list of:
- System administrators
- Technical support
- Cloud provider support
- Security team
- Management contacts

## Appendix: Quick Reference

### Key Environment Variables
```bash
JWT_SECRET              # Session encryption key
USER_PASSWORD          # User access password
ADMIN_PASSWORD         # Admin access password
GCS_BUCKET_NAME        # Google Cloud Storage bucket
USE_LOCAL_STORAGE      # true/false
ENABLE_CSRF_PROTECTION # true/false
SESSION_TIMEOUT_MINUTES # Default: 30
RATE_LIMIT_REQUESTS    # Default: 100
```

### Important Paths
- Templates: `/templates/` or GCS bucket
- Temp files: `/temp/`
- Logs: Application logs location
- Local storage: `./local_storage/`

### Useful Commands
```bash
# Generate secure password
python -c "import secrets; print(secrets.token_urlsafe(16))"

# Check application status
curl https://your-app-url/healthz

# Clear temp files
find ./temp -mtime +1 -delete
```