# Certificate Generator App

A Streamlit-based certificate generator application with dual authentication (user/admin), hosted on Google Cloud Run. Users can bulk-generate PDF certificates from spreadsheets, while admins manage templates and passwords.

## Features

### User Features
- Upload CSV/XLSX spreadsheets
- Select certificate templates by course
- Preview certificates before bulk generation
- Download certificates as ZIP file
- Real-time progress tracking
- Session management with automatic timeout

### Admin Features
- All user features
- Upload and manage PDF templates
- Map templates to course names
- Change user/admin passwords
- View usage statistics and activity logs
- Test templates with dummy data
- Delete templates
- Monitor system performance
- Export configuration settings

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
# Edit .env with your values
```

**Required environment variables:**

⚠️ **CRITICAL**: The `JWT_SECRET` environment variable MUST be set for session persistence. Without it, all user sessions will be lost when the application restarts!

```bash
# Generate secure values
python -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('USER_PASSWORD=' + secrets.token_urlsafe(16))"
python -c "import secrets; print('ADMIN_PASSWORD=' + secrets.token_urlsafe(16))"

# Add to .env file
JWT_SECRET=<generated_jwt_secret>  # REQUIRED for session persistence!
USER_PASSWORD=<generated_user_password>
ADMIN_PASSWORD=<generated_admin_password>
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
docker run -p 8080:8080 \
  -e JWT_SECRET="your-persistent-jwt-secret-here" \
  -e USER_PASSWORD="user123" \
  -e ADMIN_PASSWORD="admin456" \
  cert-generator
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
│   └── storage.py           # GCS integration with local fallback
├── templates/               # Local template cache
├── temp/                    # Working directory
├── config.py               # App configuration
├── requirements.txt        # Dependencies
├── Dockerfile             # Container definition
└── .env.example           # Environment template
```

## Authentication

The app uses two-level password authentication with bcrypt hashing:
- **User Access**: Basic certificate generation features
- **Admin Access**: Full features including template management

## Security Requirements

### 🔴 CRITICAL: JWT Secret Configuration
⚠️ **IMPORTANT**: You MUST set a persistent JWT_SECRET for production:
```bash
# Generate a secure JWT secret (32+ characters)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in environment
JWT_SECRET=your_generated_secret_here
```

**WARNING**: Without setting JWT_SECRET, all user sessions will be lost when the application restarts!

### Password Configuration
⚠️ **IMPORTANT**: Passwords MUST be set via environment variables:
```bash
USER_PASSWORD=your_secure_user_password
ADMIN_PASSWORD=your_secure_admin_password
```

The application will NOT start without these environment variables set. Passwords are hashed using bcrypt for security.

### Security Features
- **CSRF Protection**: Forms are protected with JWT-based CSRF tokens when `ENABLE_CSRF_PROTECTION=true` (default)
- **Rate Limiting**: 100 requests per hour per session (configurable)
- **Session Management**: 30-minute timeout with activity tracking
- **File Validation**: Content validation, not just extension checking
- **Audit Logging**: All admin actions are logged
- **Password Security**: Bcrypt hashing with strength requirements (8+ chars, mixed case, numbers)

## PDF Template Requirements

Templates must be PDF files with form fields (not placeholders):
- Required fields: `FirstName`, `LastName`
- Optional: Define bounding boxes for text areas
- Maximum file size: 10MB
- Fields will auto-size text to fit
- Form fields are flattened during generation to remove blue backgrounds

## Deployment Options

### Option 1: Streamlit Community Cloud (FREE - Recommended)

1. Fork this repository or use your own: https://github.com/Gobidog/safestepscerts
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app" and select your repository
4. Set the following in the "Advanced settings":
   - Main file path: `app.py`
   - Python version: 3.11
5. Add these secrets in the Streamlit Cloud dashboard:
   ```toml
   USER_PASSWORD = "your_user_password"
   ADMIN_PASSWORD = "your_admin_password"
   ```
6. Deploy! Your app will be available at `https://your-app.streamlit.app`

**⚠️ Important Note**: Templates uploaded via the admin panel will not persist on Streamlit Cloud. Upload the sample templates from `sample_templates/` directory after each restart, or configure Google Cloud Storage for persistence.

### Option 2: Render.com (FREE tier)

1. Push code to GitHub
2. Create account at [render.com](https://render.com)
3. New > Web Service > Connect your GitHub repo
4. Use these settings:
   - Environment: Docker
   - Instance Type: Free
5. Add environment variables:
   - `USER_PASSWORD`
   - `ADMIN_PASSWORD`
6. Deploy!

### Option 3: Google Cloud Run

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
- **Processing time**: ~0.5 sec/certificate (sequential), ~0.1 sec/certificate (parallel)
- **Parallel processing**: Up to 8 concurrent PDF generations using ThreadPoolExecutor
- **Request timeout**: 5 minutes
- **Concurrent users**: 10+ (limited by Streamlit hosting)
- **Rate limit**: 100 requests/hour per session (configurable)
- **Memory usage**: ~50-100MB per worker thread
- **Certificate generation speed**: 500 certificates in ~10-15 seconds with 8 workers

## Storage Configuration

The app supports both Google Cloud Storage and local file storage:

- **Production**: Uses Google Cloud Storage for templates and logs
- **Development**: Falls back to local storage in `./local_storage`
- **Automatic cleanup**: Removes temporary files older than 2 hours
- **Template caching**: Downloaded templates cached for 5 minutes

Set `USE_LOCAL_STORAGE=true` in `.env` to force local storage mode.

## Security Features

- **Authentication**: Bcrypt password hashing with complexity requirements
- **Session Management**: JWT-based sessions with 30-minute timeout
- **CSRF Protection**: JWT tokens for form submission protection
- **Rate Limiting**: Configurable per-session rate limits
- **File Security**: 
  - Content validation (not just extension)
  - Filename sanitization
  - Path traversal prevention
  - Size limits (5MB default)
- **Audit Logging**: All admin actions tracked
- **Automatic Cleanup**: Temp files removed after 2 hours
- **HTTPS Only**: Enforced on Cloud Run
- **No Direct File Access**: All operations sandboxed

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