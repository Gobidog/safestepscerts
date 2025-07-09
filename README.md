# Certificate Generator App

A Streamlit-based certificate generator application with dual authentication (user/admin), hosted on Google Cloud Run. Users can bulk-generate PDF certificates from spreadsheets, while admins manage templates and passwords.

## Features

### User Features
- Upload CSV/XLSX spreadsheets
- Select certificate templates by course
- Preview certificates before bulk generation
- Download certificates as ZIP file
- Real-time progress tracking

### Admin Features
- All user features
- Upload and manage PDF templates
- Map templates to course names
- Change user/admin passwords
- View usage logs
- Test templates with dummy data

## Technology Stack

- **Frontend/Backend**: Streamlit (v1.31.0+)
- **PDF Processing**: PyMuPDF (fitz) with form fields
- **Cloud Hosting**: Google Cloud Run
- **Storage**: Google Cloud Storage
- **Containerization**: Docker
- **Rate Limiting**: 40 requests/minute

## Quick Start

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd certificate-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your passwords and GCS bucket name
```

4. Run the application:
```bash
streamlit run app.py
```

### Docker Development

```bash
# Build the container
docker build -t cert-generator .

# Run locally
docker run -p 8080:8080 -e USER_PASSWORD=user123 -e ADMIN_PASSWORD=admin456 cert-generator
```

## Project Structure

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
└── .env.example           # Environment template
```

## Authentication

The app uses two-level password authentication:
- **User Access**: Basic certificate generation features
- **Admin Access**: Full features including template management

Default passwords (change these!):
```python
USER_PASSWORD=UserPass123
ADMIN_PASSWORD=AdminPass456
```

## PDF Template Requirements

Templates must be PDF files with form fields (not placeholders):
- Required fields: `FirstName`, `LastName`
- Optional: Define bounding boxes for text areas
- Maximum file size: 10MB
- Fields will auto-size text to fit

## Deployment to Google Cloud Run

1. Set up Google Cloud project:
```bash
gcloud projects create cert-generator-app
gcloud config set project cert-generator-app
```

2. Enable required APIs:
```bash
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
```

3. Create storage bucket:
```bash
gsutil mb gs://cert-templates-bucket
```

4. Deploy the application:
```bash
gcloud run deploy cert-generator \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars USER_PASSWORD=xxx,ADMIN_PASSWORD=yyy,GCS_BUCKET=cert-templates-bucket
```

## Performance Specifications

- **Max upload size**: 5MB
- **Max rows per batch**: 500
- **Processing time**: ~0.5 sec/certificate
- **Request timeout**: 5 minutes
- **Concurrent users**: 10
- **Rate limit**: 40 requests/minute

## Security Features

- Session-based authentication
- File type validation (CSV/XLSX only)
- Filename sanitization
- Automatic temp file cleanup (1 hour)
- HTTPS only on Cloud Run
- No direct file system access

## Cost Estimates

Free tier coverage (monthly):
- Cloud Run: 2M requests
- Cloud Storage: 5GB
- Bandwidth: 1GB North America

Typical usage stays within free tier limits.

## License

[Your License Here]

## Support

For issues or questions, please open an issue in the repository.