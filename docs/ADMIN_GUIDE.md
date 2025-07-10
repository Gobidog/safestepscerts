# Certificate Generator - Administrator Guide

## Table of Contents
1. [Admin Overview](#admin-overview)
2. [Accessing Admin Features](#accessing-admin-features)
3. [Managing Templates](#managing-templates)
4. [Password Management](#password-management)
5. [Usage Monitoring](#usage-monitoring)
6. [Maintenance Tasks](#maintenance-tasks)
7. [Troubleshooting Admin Issues](#troubleshooting-admin-issues)
8. [Security Best Practices](#security-best-practices)
9. [Advanced Configuration](#advanced-configuration)

## Admin Overview

As an administrator, you have full access to all user features plus additional capabilities:
- Upload and manage certificate templates
- Map templates to course names
- Change user and admin passwords
- Monitor usage statistics
- View activity logs
- Perform system maintenance

### Admin vs User Access
| Feature | User | Admin |
|---------|------|--------|
| Generate certificates | ✅ | ✅ |
| Upload spreadsheets | ✅ | ✅ |
| Preview certificates | ✅ | ✅ |
| Upload templates | ❌ | ✅ |
| Change passwords | ❌ | ✅ |
| View usage stats | ❌ | ✅ |
| Delete templates | ❌ | ✅ |

## Accessing Admin Features

1. Navigate to the application URL
2. Click "Login" in the sidebar
3. Enter admin credentials:
   - **Username**: `admin`
   - **Password**: Your admin password
4. After login, you'll see "Admin Panel" in the sidebar
5. Click to access administrative features

### Admin Panel Layout
The admin panel is organized into sections:
- **Template Management** - Upload, view, delete templates
- **Course Mapping** - Link courses to templates
- **Password Management** - Update credentials
- **Usage Statistics** - Monitor application usage
- **System Maintenance** - Cleanup and optimization

## Managing Templates

### Uploading New Templates

#### Template Requirements
PDF templates must include:
- Form fields (not just text placeholders)
- Required fields: `FirstName` and `LastName`
- Recommended: Clear space for names
- Maximum file size: 10MB

#### Upload Process
1. Navigate to Admin Panel
2. In "Template Management" section:
3. Enter a descriptive template name (e.g., "Professional Certificate 2025")
4. Click "Browse" and select your PDF file
5. Click "Upload Template"
6. Wait for confirmation message

#### Validating Templates
After upload, the system automatically:
- Checks for required form fields
- Validates PDF structure
- Reports any issues found
- Shows field detection results

### Viewing Templates
Current templates are displayed in a table showing:
- Template name
- Upload date
- File size
- Number of times used
- Actions (Preview, Delete)

### Template Testing
Before making a template available:
1. Click "Test Template" button
2. System generates sample with dummy data
3. Review the output
4. Check name positioning and formatting

### Deleting Templates
1. Find template in the list
2. Click "Delete" button
3. Confirm deletion in popup
4. Note: This doesn't affect already generated certificates

### Course Mapping

Map course names to specific templates:

1. In "Course Mapping" section
2. View current mappings table
3. To add a new mapping:
   - Enter exact course name (case-sensitive)
   - Select template from dropdown
   - Click "Add Mapping"
4. To update existing:
   - Click "Edit" next to mapping
   - Select new template
   - Save changes

#### Default Template
Set a default template for unmapped courses:
1. Select template from "Default Template" dropdown
2. Click "Set as Default"
3. This template is used when no course match is found

## Password Management

### Changing Passwords

For security, regularly update passwords:

1. Navigate to "Password Management" section
2. To change user password:
   - Enter new password in "New User Password" field
   - Re-enter in "Confirm User Password" field
   - Click "Update User Password"
3. To change admin password:
   - Enter current admin password
   - Enter new admin password
   - Confirm new password
   - Click "Update Admin Password"

### Password Requirements
- Minimum 8 characters
- Mix of letters and numbers recommended
- Avoid common words or patterns
- Change every 90 days

### After Password Changes
- Notify affected users immediately
- Current sessions remain active
- New logins require new password
- Update any documentation

## Usage Monitoring

### Statistics Dashboard

Monitor application usage through:

#### Overall Statistics
- Total certificates generated
- Number of active users
- Templates usage count
- Storage space used
- Average generation time

#### Time-based Metrics
- Daily generation count
- Peak usage hours
- Monthly trends
- Busiest days of week

#### User Activity
- Recent logins
- Generation history
- Error frequency
- Session durations

### Activity Logs

Access detailed logs showing:
- User actions (login, generate, download)
- Admin actions (template upload, password change)
- System events (cleanup, errors)
- Timestamps for all activities

#### Log Filtering
- Filter by date range
- Filter by user type
- Search by specific user
- Export logs as CSV

### Performance Monitoring

Track system performance:
- Average certificate generation time
- Queue lengths during peak times
- Memory usage patterns
- Storage growth rate

## Maintenance Tasks

### Regular Maintenance

#### Daily Tasks
- Check error logs
- Monitor storage space
- Verify template availability
- Review failed generations

#### Weekly Tasks
- Clean temporary files
- Archive old logs
- Update course mappings
- Test critical templates

#### Monthly Tasks
- Full system backup
- Password rotation reminder
- Usage report generation
- Performance optimization

### Storage Management

#### Automatic Cleanup
System automatically removes:
- Temporary files older than 2 hours
- Generated ZIPs after 24 hours
- Session data after 30 minutes inactive

#### Manual Cleanup
When needed:
1. Navigate to "System Maintenance"
2. Click "Clean Temporary Files"
3. Review space to be freed
4. Confirm cleanup action

### Backup Procedures

#### What to Backup
- Certificate templates
- Course mappings
- Configuration files
- User activity logs

#### Backup Schedule
- Templates: After each upload
- Configs: Weekly
- Logs: Monthly
- Full backup: Monthly

## Troubleshooting Admin Issues

### Common Admin Problems

#### "Template upload failed"
- Check PDF has form fields (use Adobe Acrobat)
- Verify FirstName and LastName fields exist
- Ensure file size < 10MB
- Try re-saving PDF with Adobe

#### "Cannot change password"
- Verify current admin password is correct
- Check password meets requirements
- Clear browser cache
- Try incognito/private mode

#### "Statistics not updating"
- Allow 5 minutes for updates
- Refresh the page
- Check browser console for errors
- Verify database connection

#### "Cleanup not working"
- Check storage permissions
- Verify cleanup schedule is enabled
- Manual cleanup if automatic fails
- Check system logs for errors

### Advanced Debugging

#### Checking Logs
1. Access system logs directory
2. Look for error patterns
3. Common log files:
   - `app.log` - Application events
   - `error.log` - Error details
   - `access.log` - User activity

#### Performance Issues
If system is slow:
1. Check concurrent user count
2. Review certificate queue length
3. Monitor memory usage
4. Consider scaling resources

## Security Best Practices

### Access Control
- Use strong, unique passwords
- Don't share admin credentials
- Rotate passwords quarterly
- Monitor unauthorized access attempts

### Template Security
- Scan templates for malicious code
- Validate all uploads
- Keep template backups
- Restrict template access

### Data Protection
- Don't store sensitive data in templates
- Regularly purge old generation logs
- Use HTTPS for all connections
- Implement IP whitelisting if needed

### Audit Trail
- Review admin action logs weekly
- Monitor unusual activity patterns
- Document all admin changes
- Keep audit logs for 1 year

## Advanced Configuration

### Environment Variables

Key configurations:
```bash
USER_PASSWORD=<user_password>
ADMIN_PASSWORD=<admin_password>
GCS_BUCKET=<bucket_name>
MAX_UPLOAD_SIZE=5242880  # 5MB
SESSION_TIMEOUT=1800  # 30 minutes
RATE_LIMIT=40  # requests per minute
```

### Performance Tuning

#### Scaling Options
- Increase Cloud Run instances
- Adjust memory allocation
- Enable Cloud CDN for templates
- Use Redis for session storage

#### Optimization Tips
- Compress large templates
- Limit concurrent generations
- Cache frequently used templates
- Archive old data regularly

### Integration Options

#### Webhook Notifications
Configure webhooks for:
- Generation completion
- Error alerts
- Usage thresholds
- Maintenance reminders

#### API Access
Limited API available for:
- Programmatic generation
- Template management
- Statistics retrieval
- Bulk operations

### Custom Branding

Customize the application:
1. Replace logo in header
2. Adjust color scheme
3. Modify welcome messages
4. Add organization name

## Emergency Procedures

### System Down
1. Check Cloud Run status
2. Verify billing is current
3. Review error logs
4. Contact cloud support

### Data Loss
1. Restore from latest backup
2. Regenerate affected certificates
3. Notify affected users
4. Document incident

### Security Breach
1. Change all passwords immediately
2. Review access logs
3. Disable compromised accounts
4. Implement additional security

## Support and Resources

### Getting Help
- Technical documentation: See API_DOCUMENTATION.md
- Deployment guide: See DEPLOYMENT_GUIDE.md
- Cloud Run docs: https://cloud.google.com/run/docs

### Monitoring Tools
- Google Cloud Console
- Cloud Logging
- Cloud Monitoring
- Error Reporting

### Best Practices Resources
- PDF form field creation guides
- Cloud Run optimization tips
- Security hardening checklists
- Performance benchmarking tools

---

**Remember**: As an administrator, you're responsible for maintaining system security, performance, and availability. Regular monitoring and maintenance ensure smooth operation for all users.