# Certificate Generator App - Design Document v2

## 1. Project Overview
A Streamlit-based certificate generator app with dual authentication (user/admin), hosted on Google Cloud Run. Users can bulk-generate PDF certificates from spreadsheets, while admins manage templates and passwords.

## 2. Technology Stack
- **Frontend/Backend**: Streamlit (all-in-one)
- **PDF Processing**: PyMuPDF (fitz) with form fields
- **Cloud Hosting**: Google Cloud Run
- **Storage**: Google Cloud Storage for templates
- **Containerization**: Docker
- **Rate Limiting**: 40 requests/minute

## 3. Authentication System

### Two-Level Access:
```python
passwords = {
    "user": "UserPass123",     # Regular access
    "admin": "AdminPass456"    # Full access + management
}
```

### User Features:
- Upload spreadsheet
- Select course/template
- Preview first certificate
- Generate bulk certificates
- Download ZIP file

### Admin Features (additional):
- All user features
- Upload/manage templates
- Map templates to courses
- Change both passwords
- View usage logs
- Test templates

## 4. Application Flow

### Main Interface (Streamlit Pages):
```
📱 app.py
├── 🔐 pages/1_login.py
├── 📋 pages/2_generate.py (user/admin)
└── ⚙️ pages/3_admin.py (admin only)
```

### User Workflow:
1. **Login Page** → Enter password
2. **Main App** → Upload CSV/XLSX
3. **Select Course** → Dropdown of available templates
4. **Preview** → Generate sample with first row
5. **Confirm** → Start bulk generation
6. **Progress Bar** → Real-time updates
7. **Download** → Get certificates.zip

### Admin Workflow:
All user features plus:
1. **Admin Tab** → Manage templates
2. **Upload Template** → PDF with form fields
3. **Map to Course** → Name the certificate
4. **Test Generation** → Try with dummy data
5. **Change Passwords** → Update user/admin passwords

## 5. PDF Certificate Generation

### Template Requirements:
- PDF with form fields (not placeholders)
- Fields named: `FirstName`, `LastName`
- Define bounding boxes for text areas

### Generation Process:
```python
def generate_certificate(template_path, first_name, last_name):
    doc = fitz.open(template_path)
    page = doc[0]
    
    # Fill form fields
    for field in page.widgets():
        if field.field_name == "FirstName":
            field.field_value = first_name
            field.update()
        elif field.field_name == "LastName":
            field.field_value = last_name
            field.update()
    
    # Auto-size text if needed
    adjust_font_size(field, text)
    
    return doc
```

### Font Sizing Algorithm:
```python
def adjust_font_size(field, text, max_width):
    size = 24  # Start size
    min_size = 14
    
    while text_width(text, size) > max_width and size > min_size:
        size -= 0.5
    
    return size
```

## 6. Error Handling & Validation

### Spreadsheet Validation:
- Required columns: First Name, Last Name
- Handle missing values → Skip with warning
- Duplicate names → Append _1, _2, etc.
- Unicode support for international names
- Max 500 rows per batch

### Template Validation:
- Must have required form fields
- PDF must be valid
- File size < 10MB

## 7. Progress Tracking

### Streamlit Native:
```python
progress_bar = st.progress(0)
status_text = st.empty()

for i, row in enumerate(df.iterrows()):
    # Generate certificate
    progress = (i + 1) / len(df)
    progress_bar.progress(progress)
    status_text.text(f'Processing {i+1}/{len(df)} certificates...')
```

## 8. File Structure
```
certificate-generator/
├── app.py                    # Main Streamlit app
├── pages/
│   ├── 1_login.py           # Authentication
│   ├── 2_generate.py        # Certificate generation
│   └── 3_admin.py           # Admin panel
├── utils/
│   ├── auth.py              # Password management
│   ├── pdf_generator.py     # Certificate creation
│   ├── validators.py        # Input validation
│   └── storage.py           # GCS integration
├── templates/               # Local template cache
├── temp/                    # Working directory
├── config.py               # App configuration
├── requirements.txt        # Dependencies
├── Dockerfile             # Container definition
└── .env                   # Passwords (not in git)
```

## 9. Security & Rate Limiting

### Rate Limiting (40 req/min):
```python
from streamlit_rate_limiter import RateLimiter

limiter = RateLimiter(
    max_requests=40,
    window_seconds=60
)

@limiter.limit
def generate_certificates():
    # Generation logic
```

### Security Measures:
- Session-based authentication
- File type validation (CSV/XLSX only)
- Filename sanitization
- Automatic temp file cleanup (1 hour)
- HTTPS only on Cloud Run
- No direct file system access

## 10. Google Cloud Deployment

### Setup Steps:
1. **Create Project**: `gcloud projects create cert-generator`
2. **Enable APIs**: Cloud Run, Cloud Storage
3. **Create Bucket**: For template storage
4. **Build Container**: `docker build -t cert-gen .`
5. **Deploy**: `gcloud run deploy --image cert-gen`

### Environment Variables:
```bash
USER_PASSWORD=UserPass123
ADMIN_PASSWORD=AdminPass456
GCS_BUCKET=cert-templates-bucket
```

## 11. Admin Interface Features

### Template Management:
```python
# Admin page snippet
st.header("Template Management")

# Upload new template
uploaded_file = st.file_uploader("Upload PDF Template", type=['pdf'])
course_name = st.text_input("Course Name")

if st.button("Add Template"):
    save_template_to_gcs(uploaded_file, course_name)
    st.success("Template added!")

# List existing templates
templates = list_templates()
for template in templates:
    col1, col2, col3 = st.columns([3, 1, 1])
    col1.text(template.name)
    if col2.button("Test", key=f"test_{template.id}"):
        test_template(template)
    if col3.button("Delete", key=f"del_{template.id}"):
        delete_template(template)
```

### Password Management:
```python
# Change passwords section
st.header("Password Management")
new_user_pass = st.text_input("New User Password", type="password")
new_admin_pass = st.text_input("New Admin Password", type="password")

if st.button("Update Passwords"):
    update_passwords(new_user_pass, new_admin_pass)
    st.success("Passwords updated!")
```

## 12. Monitoring & Logging

### Structured Logging:
```python
import structlog
logger = structlog.get_logger()

logger.info("certificate_generated", 
    user="session_id",
    template="cyber_safety",
    count=45,
    duration_seconds=12.3
)
```

### Metrics to Track:
- Total certificates generated
- Average processing time
- Error rates
- Popular templates
- Peak usage times

## 13. Cost Optimization

### Estimated Monthly Costs (Free Tier):
- Cloud Run: 2M requests free
- Cloud Storage: 5GB free
- Bandwidth: 1GB free North America
- **Total**: $0 for typical usage

### Scaling Costs:
- Beyond free tier: ~$0.40/million requests
- Storage: $0.02/GB/month
- Bandwidth: $0.12/GB

## 14. Performance Specifications

- **Max file size**: 5MB upload
- **Max rows**: 500 per batch
- **Processing time**: ~0.5 sec/certificate
- **Timeout**: 5 minutes max
- **Concurrent users**: 10
- **Rate limit**: 40 requests/minute

## 15. Future Enhancements

### Phase 2 Possibilities:
- Email certificates directly
- Bulk template operations
- Certificate verification QR codes
- Usage analytics dashboard
- API for external integration

## Deployment Commands

```bash
# Local development
streamlit run app.py

# Build Docker image
docker build -t cert-generator .

# Test locally
docker run -p 8080:8080 cert-generator

# Deploy to Cloud Run
gcloud run deploy cert-generator \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars USER_PASSWORD=xxx,ADMIN_PASSWORD=yyy
```

## Quick Start Checklist

- [ ] Set up Google Cloud project
- [ ] Create Cloud Storage bucket
- [ ] Create PDF templates with form fields
- [ ] Write Streamlit app with pages
- [ ] Implement PyMuPDF certificate generation
- [ ] Add progress tracking
- [ ] Create admin interface
- [ ] Set up rate limiting
- [ ] Deploy to Cloud Run
- [ ] Test with sample data