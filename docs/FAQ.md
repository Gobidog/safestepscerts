# Certificate Generator - Frequently Asked Questions

## General Questions

### What is the Certificate Generator?
The Certificate Generator is a web-based application that allows you to create professional PDF certificates in bulk. You upload a spreadsheet with recipient names, select a template, and the system generates individual PDF certificates for each person.

### Who can use this application?
There are two user levels:
- **Regular Users**: Can upload spreadsheets and generate certificates
- **Administrators**: Can also manage templates and change passwords

### What browsers are supported?
The application works best with:
- Google Chrome (recommended)
- Mozilla Firefox
- Microsoft Edge
- Safari

Mobile browsers are not officially supported due to file handling limitations.

## File Upload Questions

### What file formats can I upload?
- CSV (.csv) - Comma-separated values
- Excel (.xlsx) - Microsoft Excel 2007 and newer

Older Excel formats (.xls) are not supported.

### What columns are required in my spreadsheet?
Your spreadsheet must have these exact column names:
- `first_name` (exactly as shown, lowercase with underscore)
- `last_name` (exactly as shown, lowercase with underscore)

Other columns can be present but will be ignored.

### Why does it say "Required columns missing"?
Common causes:
1. Column names have different capitalization (e.g., `First_Name` instead of `first_name`)
2. Column names have spaces (e.g., `first name` instead of `first_name`)
3. Column names are misspelled
4. The file has no header row

### Can I use Unicode characters in names?
Yes! The system supports international characters including:
- Accented characters (é, ñ, ü)
- Asian characters (中文, 日本語, 한국어)
- Arabic script (العربية)
- Cyrillic (Русский)

Make sure your CSV is saved with UTF-8 encoding.

### What's the maximum file size?
- Maximum file size: 5MB
- Maximum rows: 500 recipients

For larger batches, split your file into multiple uploads.

## Certificate Generation Questions

### How long does generation take?
- Single certificate: ~0.5 seconds
- 100 certificates: ~50 seconds
- 500 certificates: ~4-5 minutes

A progress bar shows the current status during generation.

### Can I preview before generating all certificates?
Yes! After uploading your file and selecting a template, click "Preview Certificate" to see how the first recipient's certificate will look.

### What happens to duplicate names?
If multiple people have the same name, the system adds numbers to filenames:
- John_Smith.pdf
- John_Smith_1.pdf
- John_Smith_2.pdf

### Why are some names cut off?
The system automatically adjusts font size to fit names within the designated area. Very long names may still be truncated. Consider:
- Using initials for middle names
- Abbreviating titles
- Using a template with more space for names

## Template Questions

### What templates are available?
Standard templates include:
1. **Basic Certificate** - Simple, professional design
2. **Professional Certificate** - Formal with logo space
3. **Multilingual Certificate** - Supports multiple languages
4. **Workshop Certificate** - Modern design for training

### How are templates assigned?
If your spreadsheet has a `course` column, templates are automatically suggested based on course names. You can always manually select a different template.

### Can I upload custom templates?
Only administrators can upload new templates. Templates must be PDF files with form fields for `FirstName` and `LastName`.

## Download Questions

### What format are certificates delivered in?
Certificates are delivered as a ZIP file containing:
- Individual PDF files for each recipient
- Files named as: FirstName_LastName.pdf

### How long are downloads available?
- Download links expire after 1 hour
- Files are automatically cleaned up after 2 hours
- Download your certificates promptly

### Can I regenerate certificates?
Yes, you can upload the same spreadsheet again and regenerate certificates. Each generation creates new files.

## Account Questions

### What are the default passwords?
Default passwords are set by your administrator. Contact them for login credentials.

### I forgot my password. How do I reset it?
Contact your administrator to reset passwords. There is no self-service password reset.

### How long do sessions last?
Sessions expire after 30 minutes of inactivity. You'll need to log in again to continue.

### Can I have multiple users logged in?
Yes, the system supports up to 10 concurrent users.

## Troubleshooting Questions

### The page is stuck on "Generating certificates..."
1. Don't refresh the page - generation continues in the background
2. Check the progress counter (e.g., "45/100")
3. For large batches, this is normal
4. If truly stuck for over 10 minutes, refresh and try again

### I get "File upload failed"
Common solutions:
1. Check file size is under 5MB
2. Ensure file is .csv or .xlsx format
3. Try removing special characters from filename
4. Clear browser cache and try again

### Certificates won't download
1. Check your browser's download settings
2. Disable pop-up blockers
3. Try a different browser
4. Check if your Downloads folder is full

### Special characters appear as question marks
1. Save your CSV file with UTF-8 encoding
2. In Excel: Save As > CSV UTF-8
3. In Google Sheets: File > Download > CSV (automatic UTF-8)

## Security Questions

### Is my data secure?
- All connections use HTTPS encryption
- Files are automatically deleted after 2 hours
- No personal data is permanently stored
- Access requires authentication

### Who can see my uploaded data?
Only you can see your uploaded data during your session. Administrators cannot view your spreadsheet contents or generated certificates.

### Are certificates stored permanently?
No, all generated certificates and uploaded files are automatically deleted after 2 hours.

## Performance Questions

### Why is generation slow?
Factors affecting speed:
- Number of recipients
- Server load (number of concurrent users)
- Template complexity
- Internet connection speed

### Can I speed up generation?
- Process smaller batches (50-100 at a time)
- Use simpler templates
- Avoid peak usage hours
- Ensure stable internet connection

## Technical Questions

### What technology powers this application?
- Frontend/Backend: Streamlit
- PDF Processing: PyMuPDF
- Hosting: Google Cloud Run
- Storage: Google Cloud Storage

### Can this be self-hosted?
Yes, the application can be deployed on any Docker-compatible platform. See the Deployment Guide for details.

### Is there an API available?
Currently, there is no public API. The application is designed for web interface use only.

### What are the system requirements?
For users:
- Modern web browser
- Stable internet connection
- Ability to upload files and download ZIP files

## Getting Help

### Where can I get more help?
1. Check this FAQ first
2. Read the User Guide for detailed instructions
3. Contact your administrator
4. For technical issues, provide:
   - Exact error message
   - What you were trying to do
   - Browser and operating system
   - Screenshot if possible

### How do I report a bug?
Contact your administrator with:
- Detailed description of the issue
- Steps to reproduce the problem
- Screenshots or error messages
- Time and date of occurrence

---

**Note**: This FAQ is regularly updated. If your question isn't answered here, please contact your administrator for assistance.