# Sample Certificate Templates

This directory contains sample certificate templates for the SafeSteps Certificate Generator.

## Important Note for Streamlit Cloud Users

⚠️ **Templates uploaded through the admin panel are stored locally and will be lost when the app restarts on Streamlit Community Cloud.**

To ensure templates are always available:

1. **Upload these sample templates** after each restart
2. **Configure Google Cloud Storage** for persistent storage
3. **Download your templates** regularly for backup

## Available Sample Templates

1. `vapes_and_vaping.pdf` - Default certificate template with form fields:
   - `FullName` - Recipient's first name
   - `text_5plme` - Recipient's last name  
   - `Date_dm` - Certificate date

## Adding Your Own Templates

To add your own PDF templates:

1. Create a PDF with form fields using Adobe Acrobat or similar tools
2. Name the form fields appropriately (e.g., FirstName, LastName, Date)
3. Upload through the admin panel
4. Test using the "Test Template" button

## Template Requirements

- PDF format with fillable form fields
- Recommended fields: FirstName, LastName, Date
- Maximum file size: 10MB
- Form fields will auto-size text to fit

## For Production Use

For production deployments, we strongly recommend:
- Setting up Google Cloud Storage for template persistence
- Including templates in your deployment
- Regular backups of uploaded templates