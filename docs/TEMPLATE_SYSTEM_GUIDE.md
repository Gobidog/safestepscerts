# SafeSteps Template System Guide

## Overview
This guide explains the template upload and usage system for the SafeSteps Certificate Generator, including recent fixes and improvements.

## Recent Fixes (2025-07-29)

### Issues Resolved
1. **Template Upload Not Saving** - Admin template page now properly saves uploaded templates using the storage manager
2. **Incorrect Template Paths** - Certificate generation now uses storage manager to retrieve correct template paths
3. **Template Listing** - Admin page now shows actual templates from storage instead of hardcoded data
4. **Template Validation** - Added template validation tool to check PDF compatibility before upload
5. **Better Error Handling** - Improved error messages throughout the template workflow

### Key Improvements
- Full integration with storage manager for consistent template handling
- Support for both local storage and Google Cloud Storage
- Template preview generation
- Form field auto-detection and validation
- Metadata support for templates (display name, description, upload info)

## Template Requirements

### PDF Form Fields
Templates must be PDF files with fillable form fields. The system auto-detects and maps these fields:

**Required Fields (at least one):**
- First name field (detected patterns: "FirstName", "first", "fname", "given", "fullname", "name")
- Last name field (detected patterns: "LastName", "last", "lname", "surname", "family", or generic fields like "text_*")

**Optional Fields:**
- Date field (auto-populated with current date)
- Additional custom fields

### Creating Compatible Templates
1. Use Adobe Acrobat, LibreOffice, or similar tools to create PDFs with form fields
2. Name fields appropriately for auto-detection
3. Test with the validation tool before uploading

## Admin Template Management

### Uploading Templates
1. Navigate to Admin Dashboard → Templates
2. Click "📤 Upload New Template"
3. Select your PDF file
4. Enter a display name (user-friendly)
5. Optionally enter a filename (auto-generated if blank)
6. Add a description to help users choose the right template
7. Click "💾 Save Template"

### Validating Templates
1. Use the "🔍 Validate Template" section
2. Upload a PDF to check compatibility
3. Review detected form fields
4. Ensure at least one name field is detected

### Managing Existing Templates
- **Preview**: Generate a sample certificate with test data
- **Delete**: Remove templates no longer needed
- View metadata: size, upload date, description

## User Workflow

### Template Selection (Step 3)
1. Users see all available templates with:
   - Display name
   - Description
   - File size
   - Upload date
2. Click to select a template
3. System validates template accessibility before proceeding

### Certificate Generation (Step 4)
1. System retrieves template using storage manager
2. Validates template has required fields
3. Maps spreadsheet columns to PDF fields
4. Generates certificates with auto-sized text
5. Logs usage for analytics

## Storage Configuration

### Local Storage (Development)
```yaml
# config.yaml
storage:
  use_local_storage: true
  local_storage_path: ./storage
```

Templates stored in: `./storage/templates/`

### Google Cloud Storage (Production)
```yaml
# config.yaml
storage:
  use_local_storage: false
  gcs_bucket_name: your-bucket-name
  gcs_project_id: your-project-id
```

Templates stored in: `gs://your-bucket-name/templates/`

## Troubleshooting

### Common Issues

1. **"No templates available"**
   - Solution: Upload templates through admin interface
   - Check storage permissions
   - Verify storage configuration

2. **"Template validation failed"**
   - Solution: Ensure PDF has form fields
   - Use validation tool to check field names
   - Try creating fields with standard names

3. **"Template file not found"**
   - Solution: Template may have been deleted
   - Re-upload the template
   - Check storage connectivity

4. **Certificate generation fails**
   - Check template has required name fields
   - Verify spreadsheet has matching column names
   - Review error messages for specific field issues

### Testing the System
Run the test script to verify everything works:
```bash
python test_template_system.py
```

This tests:
- Storage manager operations
- PDF generator functionality
- Complete workflow integration

## Best Practices

1. **Template Naming**
   - Use descriptive display names
   - Keep filenames simple (auto-generated works well)
   - Add clear descriptions

2. **Field Design**
   - Use standard field names for auto-detection
   - Make fields large enough for long names
   - Test with various name lengths

3. **Storage Management**
   - Regularly clean up unused templates
   - Monitor storage usage
   - Back up important templates

4. **Security**
   - Only admins can upload/delete templates
   - Templates are validated before use
   - File uploads are sanitized

## API Reference

### Storage Manager Methods
```python
# Save template
storage.save_template(file_buffer, filename, metadata)

# List all templates
templates = storage.list_templates()

# Get template path for PDF generator
path = storage.get_template_path(template_name)

# Delete template
storage.delete_template(template_name)
```

### PDF Generator Methods
```python
# Initialize with template
generator = PDFGenerator(template_path)

# Validate template
info = generator.validate_template()

# Generate single certificate
generator.generate_certificate(first_name, last_name, output_path)

# Generate batch
results, zip_path = generator.generate_batch(recipients)
```

## Deployment Considerations

### Streamlit Cloud
1. Ensure `STREAMLIT_STORAGE_PATH` environment variable is set
2. Templates persist in local storage on the Streamlit Cloud instance
3. Consider backup strategy for templates

### Google Cloud Run
1. Configure GCS bucket and credentials
2. Templates persist in Google Cloud Storage
3. Automatic backup and versioning available

## Future Enhancements
- Template versioning
- Template categories/tags
- Custom field mapping UI
- Template sharing between projects
- Bulk template operations