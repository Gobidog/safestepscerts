# SafeSteps Certificate Generator - User Setup Guide

## 🚀 Quick Start

### For Users
1. **Access the System**: Open your web browser and navigate to the SafeSteps application URL
2. **Login**: Use your assigned credentials (username/email and password)
3. **Generate Certificates**: Follow the 5-step workflow to create your certificates

### Default System Users
- **Administrator**: 
  - Username: `admin` 
  - Email: `admin@safesteps.local`
  - Default Password: `Admin@SafeSteps2024` (can be customized via ADMIN_PASSWORD environment variable)
- **Test User**: 
  - Username: `testuser` 
  - Email: `testuser@safesteps.local`
  - Password: Contact your administrator for current credentials

> ⚠️ **Security Note**: Default passwords should be changed immediately in production environments.
> 💡 **Login Tip**: You can use either username OR email address to log in.

## 📋 System Requirements

### Browser Compatibility
- **Chrome**: Version 90+ (Recommended)
- **Firefox**: Version 88+
- **Safari**: Version 14+
- **Edge**: Version 90+

### File Format Support
- **CSV**: Comma-separated values (recommended)
- **Excel**: .xlsx and .xls formats
- **Encoding**: UTF-8 recommended for special characters

## 📊 Data File Requirements

### Required Columns
Your spreadsheet must contain these columns (case-insensitive):
- `First Name` or `first name`
- `Last Name` or `last name`

### Optional Columns
- `Email` - For future features
- `Course` - Course or program name
- `Date` - Completion date
- `Grade` - Achievement level

### Data File Best Practices
1. **Use the first row for headers**: Column names should be in the first row
2. **Avoid empty rows**: Remove any blank rows between data
3. **Clean data**: Remove special characters that might cause issues
4. **Small batches**: Start with 10-50 recipients for testing
5. **Backup originals**: Keep a copy of your original data file

### Example Data Format
```csv
First Name,Last Name,Course,Date
John,Doe,Safety Training,2024-01-15
Jane,Smith,Fire Safety,2024-01-16
Mike,Johnson,First Aid,2024-01-17
```

## 🔧 Troubleshooting

### Login Issues
**Problem**: Cannot login with correct credentials
**Solutions**:
- Verify you're using the correct username OR email address
- Ensure password meets requirements (8+ characters, uppercase, lowercase, numbers)
- Try the other login format (email if using username, or vice versa)
- Clear your browser cache (Ctrl+F5 or Cmd+Shift+R)
- Try an incognito/private browsing window
- Disable browser extensions temporarily
- Check if cookies are enabled
- Contact your administrator

**Problem**: "Account is disabled" message
**Solution**: Contact your administrator to reactivate your account

**Problem**: "Too many login attempts" message
**Solutions**:
- Wait 5-10 minutes before trying again
- Rate limiting is applied per username/email
- Contact your administrator if lockout persists

**Problem**: Help section shows credentials that don't work
**Solutions**:
- The help section may show example credentials, not actual working ones
- Contact your administrator for current working test credentials
- Use the default admin credentials: admin / Admin@SafeSteps2024 (if unchanged)

### File Upload Issues
**Problem**: File upload fails or shows errors
**Solutions**:
- Ensure file is in CSV or Excel format (.csv, .xlsx, .xls)
- Check file size is under 10MB
- Verify file is not password-protected
- Try saving Excel file as CSV
- Remove any special characters from filename

**Problem**: "Validation failed" errors
**Solutions**:
- Ensure your file has 'First Name' and 'Last Name' columns
- Check for empty rows in your data
- Remove any merged cells in Excel files
- Ensure data starts from row 2 (headers in row 1)

### Template Issues
**Problem**: No templates available
**Solution**: Contact your administrator - templates need to be uploaded to the system

**Problem**: Template selection doesn't work
**Solutions**:
- Refresh the page and try again
- Contact administrator to verify template files

### Certificate Generation Issues
**Problem**: Generation fails or produces errors
**Solutions**:
- Try with a smaller batch of recipients first
- Check that names don't contain special characters
- Verify your data passed validation in Step 2
- Contact administrator if issue persists

### Download Issues
**Problem**: Cannot download certificates
**Solutions**:
- Check if browser is blocking downloads
- Try right-clicking the download button and "Save as"
- Ensure you have enough disk space
- Try a different browser

## 📞 Getting Help

### Before Contacting Support
1. Note the exact error message (take a screenshot if possible)
2. Try the troubleshooting steps above
3. Note what you were doing when the problem occurred
4. Check if the issue happens in a different browser

### What to Include in Support Requests
- Your username (not password)
- Browser type and version
- Screenshot of any error messages
- Description of what you were trying to do
- Steps you've already tried

### Contact Information
- **Email**: Contact your system administrator
- **Include**: Your name, department, and detailed description of the issue

## 🔒 Security & Privacy

### Password Requirements
All passwords must meet these security requirements:
- **Minimum 8 characters** in length
- **At least one uppercase letter** (A-Z)
- **At least one lowercase letter** (a-z)
- **At least one number** (0-9)

### Best Practices
- **Never share your login credentials** with anyone
- **Log out** when finished, especially on shared computers
- **Use strong passwords** that exceed minimum requirements
- **Report suspicious activity** to your administrator
- **Use unique passwords** for this system

### Data Handling
- Your uploaded files are processed securely
- Generated certificates are temporarily stored for download
- Files are automatically cleaned up after a period
- Contact your administrator for data retention policies

## 💡 Tips for Success

### Workflow Tips
1. **Prepare your data file first** before starting the process
2. **Test with a small batch** (5-10 recipients) initially
3. **Use consistent formatting** in your data
4. **Keep backups** of your original files
5. **Download certificates immediately** after generation

### Data Preparation Tips
1. **Use Excel's "Text to Columns"** feature to separate names if needed
2. **Check for duplicate entries** before upload
3. **Standardize name formats** (e.g., all first names capitalized)
4. **Remove titles** (Mr., Mrs., Dr.) from name fields if not needed

### Browser Tips
1. **Bookmark the application URL** for easy access
2. **Don't use browser back/forward buttons** during certificate generation
3. **Keep the tab active** during processing (don't minimize)
4. **Ensure stable internet connection** for large batches

## 📈 System Status Indicators

### Login Page Indicators
- 🟢 **System Ready**: All systems operational
- ⚠️ **Configuration Warnings**: System works but has non-critical issues
- 🔴 **System Error**: Critical configuration problem

### Session Status
- Your session expires after 30 minutes of inactivity
- You'll see warnings before automatic logout
- Save your work frequently during long sessions

## 🔄 Updates & Maintenance

### Scheduled Maintenance
- System updates may occur during off-hours
- You'll be notified of planned maintenance
- Save your work before maintenance windows

### New Features
- New templates may be added periodically
- Interface improvements are deployed regularly
- Check this guide for updates after system changes

---

**Last Updated**: July 28, 2025  
**Version**: 1.1  
**Document Type**: User Guide  
**Authentication System**: User Store with bcrypt password hashing