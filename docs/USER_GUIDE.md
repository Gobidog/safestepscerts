# Certificate Generator - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Logging In](#logging-in)
3. [Uploading Your Spreadsheet](#uploading-your-spreadsheet)
4. [Selecting a Template](#selecting-a-template)
5. [Previewing Certificates](#previewing-certificates)
6. [Generating Certificates](#generating-certificates)
7. [Downloading Results](#downloading-results)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

## Getting Started

The Certificate Generator is a web-based application that allows you to create professional PDF certificates in bulk from spreadsheet data. You can generate certificates for course completions, workshops, achievements, and more.

### What You'll Need
- A CSV or Excel file with recipient names
- User login credentials (provided by your administrator)
- A web browser (Chrome, Firefox, Safari, or Edge)

## Logging In

1. Navigate to the Certificate Generator URL
2. Click on "Login" in the sidebar
3. Enter your credentials:
   - **Username**: `testuser` or `testuser@safesteps.local`
   - **Password**: `UserPass123` (local) or `Safesteps!` (cloud)
4. Click "Login" button
5. You'll see a success message and can now access the Generate page

![Login Success]
- Green checkmark appears when login is successful
- Session expires after 30 minutes of inactivity

## Uploading Your Spreadsheet

### Supported File Formats
- **CSV** (.csv) - Comma-separated values
- **Excel** (.xlsx) - Microsoft Excel 2007+

### Required Columns
Your spreadsheet MUST contain these columns:
- `first_name` - Recipient's first name
- `last_name` - Recipient's last name

### Optional Columns
You can include additional columns like:
- `course` - Course or program name
- `date` - Completion date
- `score` - Achievement score
- Any other data (will be ignored)

### Upload Steps
1. Navigate to "Generate Certificates" page
2. Click "Browse files" or drag & drop your file
3. Wait for the file to upload and validate
4. You'll see either:
   - ✅ Success message with row count
   - ❌ Error message with specific issues

### Common Upload Errors
- **Missing columns**: Add `first_name` and `last_name` columns
- **Empty file**: Ensure your file has data rows
- **Wrong format**: Use only .csv or .xlsx files
- **File too large**: Maximum 5MB or 500 rows

## Selecting a Template

After successful upload, you'll see template options based on your course data:

### Automatic Template Matching
If your spreadsheet has a `course` column, templates are automatically suggested:
- Python Programming → Basic Certificate
- Data Analysis → Professional Certificate
- Workshop courses → Workshop Certificate
- International courses → Multilingual Certificate

### Manual Template Selection
1. Review the suggested template
2. Click on a different template card if desired
3. Each template shows:
   - Template name
   - Preview thumbnail
   - Best use case description

### Available Templates
1. **Basic Certificate** - Simple, clean design for general use
2. **Professional Certificate** - Formal design with logo space
3. **Multilingual Certificate** - Supports multiple languages
4. **Workshop Certificate** - Modern design for training events
5. **Programmatic Certificate** - Dynamically generated certificates with custom layouts (no PDF template required)

## Previewing Certificates

Before generating all certificates, preview how they'll look:

1. Click "Preview Certificate" button
2. A sample certificate opens using the first row of your data
3. Check:
   - Name formatting and positioning
   - Text fits within the certificate
   - Overall appearance meets expectations
4. Close preview to return
5. Change template if needed

### Special Note: Programmatic Certificates
If you select "Programmatic Certificate", these are generated dynamically by the system without requiring a PDF template file. They:
- Use built-in professional layouts
- Automatically format text for optimal appearance
- Support custom course information
- Generate faster than template-based certificates
- Are fully compatible with all system features

## Generating Certificates

Once satisfied with the preview:

1. Click "Generate All Certificates" button
2. Watch the progress bar:
   - Shows current progress (e.g., "45/100")
   - Displays recipient being processed
   - Estimates time remaining
3. Generation speed: ~0.5 seconds per certificate
4. Process continues even if page refreshes

### During Generation
- **Don't close the browser** - Generation will stop
- **Don't navigate away** - You'll lose progress
- You can minimize the window
- Coffee break for large batches! ☕

## Downloading Results

When generation completes:

1. Success message appears with statistics
2. "Download Certificates (ZIP)" button becomes available
3. Click to download the ZIP file containing:
   - Individual PDF certificates (named: FirstName_LastName.pdf)
   - Generation report (if errors occurred)
4. ZIP file is also saved to your Downloads folder

### What's in the ZIP File
```
certificates.zip
├── John_Smith.pdf
├── Jane_Doe.pdf
├── Michael_Johnson.pdf
├── Sarah_Williams.pdf
└── generation_report.txt (if any errors)
```

## Troubleshooting

### Common Issues & Solutions

#### "No data found in file"
- Check that your file isn't empty
- Ensure data starts from row 2 (row 1 = headers)
- Remove any blank rows at the top

#### "Required columns missing"
- Column names must be exactly `first_name` and `last_name`
- Case-sensitive: `First_Name` won't work
- No spaces: `first name` won't work

#### Names appear cut off on certificates
- Template automatically adjusts font size
- Very long names may still be truncated
- Consider using initials for middle names

#### Special characters show incorrectly
- Save CSV files with UTF-8 encoding
- Excel: Save As > CSV UTF-8
- Google Sheets: Download as CSV works correctly

#### Generation seems stuck
- Check the progress message
- Large files take time (500 certificates ≈ 4 minutes)
- If truly stuck, refresh page and try again

#### Can't download ZIP file
- Check browser's download settings
- Try a different browser
- Clear browser cache and cookies

## Best Practices

### Preparing Your Data
1. **Clean your data first**
   - Remove duplicates
   - Fix spelling errors
   - Standardize name formats

2. **Use consistent formatting**
   - Avoid ALL CAPS names
   - Use proper capitalization
   - Keep names reasonably short

3. **Test with small batches**
   - Try 5-10 rows first
   - Verify output quality
   - Then proceed with full dataset

### File Organization
1. **Name your files clearly**
   - `2025_Q1_Python_Course.csv`
   - Include date and course name

2. **Keep original data**
   - Don't delete source files
   - Archive generated certificates

3. **Track what's been done**
   - Note which files have been processed
   - Keep generation dates

### Performance Tips
1. **Optimal batch sizes**
   - 50-100 certificates: Ideal
   - 100-300: Still fast
   - 300-500: Plan for 3-5 minutes

2. **Best times to generate**
   - Avoid peak hours if possible
   - System is fastest with < 5 concurrent users

3. **Browser recommendations**
   - Chrome or Firefox preferred
   - Keep browser updated
   - Close unnecessary tabs

### Security Reminders
- Don't share your login credentials
- Log out when finished
- Don't upload sensitive personal data
- Downloads auto-delete after 1 hour

## Need More Help?

If you encounter issues not covered in this guide:

1. **Check the FAQ** (see FAQ.md)
2. **Contact your administrator**
3. **Provide details:**
   - Error message (exact text)
   - What you were trying to do
   - Browser and operating system
   - Screenshot if possible

---

**Remember**: The Certificate Generator is designed to be simple and efficient. Most issues can be resolved by checking your data format and following the required column naming conventions.

Happy certificate generating! 🎓