# User Guide - SafeSteps Certificate Generator

## Table of Contents

1. [Getting Started](#getting-started)
2. [Logging In](#logging-in)
3. [Generating Certificates](#generating-certificates)
4. [Preparing Your Data](#preparing-your-data)
5. [Understanding Templates](#understanding-templates)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

---

## Getting Started

The SafeSteps Certificate Generator allows you to create professional PDF certificates in bulk from spreadsheet data. This guide will walk you through the entire process.

### What You'll Need

1. **Login Credentials**: Username and password provided by your administrator
2. **Spreadsheet Data**: Excel (.xlsx, .xls) or CSV file with participant information
3. **Certificate Template**: Pre-configured by your administrator

### System Requirements

- Modern web browser (Chrome, Firefox, Safari, Edge)
- Stable internet connection
- Ability to download ZIP files

---

## Logging In

### Step 1: Access the Application

Navigate to the certificate generator URL provided by your administrator.

### Step 2: Enter Credentials

1. You'll see a login screen with a password field
2. Enter your user password
3. Click "Login"

### Step 3: Session Management

- Sessions last 30 minutes by default
- Activity extends your session
- You'll be notified before timeout
- Save your work regularly

---

## Generating Certificates

### The 4-Step Process

#### Step 1: Upload Your Data

1. Click "Browse files" or drag and drop your spreadsheet
2. Supported formats: .xlsx, .xls, .csv
3. Maximum file size: 5MB
4. Maximum rows: 500 per batch

#### Step 2: Data Validation

The system automatically:
- Checks for required columns
- Handles common typos (e.g., "Frist Name" → "First Name")
- Shows a preview of your data
- Highlights any issues

Required columns (flexible naming):
- First Name (or similar: fname, given name, etc.)
- Last Name (or similar: lname, surname, family name, etc.)

Optional columns:
- Course/Workshop name
- Date
- Additional fields depending on template

#### Step 3: Select Template

1. Choose from available templates
2. Templates are organized by course/type
3. Each template may have different fields

#### Step 4: Generate & Download

1. Click "Generate Certificates"
2. Watch the progress bar
3. Processing speed: ~30-60 certificates per second
4. Download the ZIP file when complete

---

## Preparing Your Data

### Spreadsheet Format

Your spreadsheet should have:
- **Header row**: Column names in the first row
- **One row per certificate**: Each participant on a separate row
- **Clean data**: No special characters in names

### Example Format

| First Name | Last Name | Course Name | Date |
|------------|-----------|-------------|------|
| John | Smith | Safety Training | 2025-01-27 |
| Jane | Doe | Safety Training | 2025-01-27 |

### Column Name Flexibility

The system recognizes variations:
- First Name: "FirstName", "First", "FName", "Given Name"
- Last Name: "LastName", "Last", "LName", "Surname", "Family Name"

### Data Validation Tips

1. **Remove extra spaces**: The system does this automatically
2. **Check for typos**: Common misspellings are auto-corrected
3. **Unicode support**: Supports international characters (é, ñ, etc.)
4. **Date formats**: Use consistent date formatting

### Handling Large Datasets

For more than 500 certificates:
1. Split your data into multiple files
2. Process each file separately
3. Keep track of completed batches

---

## Understanding Templates

### What is a Template?

A template is a PDF form with placeholders for:
- Participant names
- Course information
- Dates
- Other custom fields

### Available Templates

Your administrator configures templates for:
- Different courses
- Various certificate styles
- Multiple languages

### Template Selection

Templates are typically named by:
- Course name
- Certificate type
- Language

Example: "Safety_Training_English.pdf"

---

## Troubleshooting

### Common Issues and Solutions

#### "Column not found" Error

**Problem**: Required columns missing from spreadsheet  
**Solution**: 
- Check column headers match requirements
- Look for typos in column names
- Ensure first row contains headers

#### "File too large" Error

**Problem**: Spreadsheet exceeds 5MB limit  
**Solution**:
- Split data into smaller files
- Remove unnecessary columns
- Save as .csv for smaller size

#### "Invalid file type" Error

**Problem**: Unsupported file format  
**Solution**:
- Save as .xlsx, .xls, or .csv
- Don't use .xlsm (macro-enabled)
- Avoid password-protected files

#### Certificates Not Generating

**Problem**: Process seems stuck  
**Solution**:
- Check for special characters in names
- Verify template selection
- Ensure data has no empty rows
- Try smaller batch size

#### Can't Download ZIP File

**Problem**: Download not starting  
**Solution**:
- Check popup blockers
- Try different browser
- Check available disk space
- Right-click and "Save as"

#### Session Timeout

**Problem**: Logged out unexpectedly  
**Solution**:
- Sessions last 30 minutes
- Save work frequently
- Activity extends session
- Re-login and try again

### Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "No valid data rows found" | Empty spreadsheet | Add participant data |
| "Template not found" | Missing certificate template | Contact administrator |
| "Rate limit exceeded" | Too many requests | Wait before retrying |
| "Session expired" | Timeout after 30 minutes | Log in again |

---

## Best Practices

### Before You Start

1. **Backup your data**: Keep original spreadsheet
2. **Test with small batch**: Try 5-10 certificates first
3. **Check template**: Ensure correct template selected
4. **Clean your data**: Remove special characters

### During Generation

1. **Don't refresh**: Let process complete
2. **Watch progress**: Monitor for errors
3. **Stay logged in**: Keep session active
4. **One batch at a time**: Don't start multiple

### After Generation

1. **Download immediately**: Files are temporary
2. **Verify certificates**: Check a few samples
3. **Save ZIP file**: Store in safe location
4. **Clear browser data**: For security

### Data Privacy

1. **Secure connection**: Always use HTTPS
2. **Temporary files**: Deleted after 2 hours
3. **No permanent storage**: Data not retained
4. **Logout when done**: Protects your session

### Performance Tips

1. **Optimal batch size**: 100-200 certificates
2. **Simple names**: Avoid special formatting
3. **Off-peak hours**: Faster during low usage
4. **Stable connection**: Prevents interruptions

---

## FAQ

**Q: How many certificates can I generate at once?**  
A: Up to 500 per batch. For more, split into multiple files.

**Q: What file formats are supported?**  
A: Excel (.xlsx, .xls) and CSV (.csv) files.

**Q: Can I use special characters in names?**  
A: Yes, Unicode characters (é, ñ, ü) are supported.

**Q: How long are files available for download?**  
A: Temporary files are deleted after 2 hours.

**Q: Can I customize the certificate template?**  
A: No, only administrators can manage templates.

**Q: Is my data secure?**  
A: Yes, data is encrypted in transit and not permanently stored.

**Q: What if I lose my password?**  
A: Contact your administrator for password reset.

**Q: Can I generate certificates on mobile?**  
A: The system works on mobile browsers but desktop is recommended.

---

## Support

If you encounter issues not covered in this guide:

1. Note the exact error message
2. Save any error screenshots
3. Contact your administrator
4. Provide:
   - Time of error
   - What you were doing
   - Browser and device used
   - Sample of your data (if possible)