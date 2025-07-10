# Certificate Generator - Google Cloud Run Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Project Setup](#project-setup)
3. [Environment Preparation](#environment-preparation)
4. [Building the Container](#building-the-container)
5. [Deploying to Cloud Run](#deploying-to-cloud-run)
6. [Post-Deployment Configuration](#post-deployment-configuration)
7. [Testing the Deployment](#testing-the-deployment)
8. [Monitoring and Maintenance](#monitoring-and-maintenance)
9. [Troubleshooting Deployment Issues](#troubleshooting-deployment-issues)
10. [Cost Optimization](#cost-optimization)

## Prerequisites

### Required Tools
- Google Cloud SDK (gcloud CLI)
- Docker Desktop (for local testing)
- Git
- Python 3.11+

### Google Cloud Requirements
- Active Google Cloud account
- Billing enabled
- Project with following APIs enabled:
  - Cloud Run API
  - Cloud Storage API
  - Container Registry API
  - Cloud Build API

### Local Development Setup
```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize gcloud
gcloud init

# Verify installation
gcloud --version
```

## Project Setup

### 1. Create Google Cloud Project
```bash
# Create new project
gcloud projects create cert-generator-prod

# Set as active project
gcloud config set project cert-generator-prod

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 2. Create Storage Bucket
```bash
# Create bucket for templates
gsutil mb -p cert-generator-prod -c standard -l us-central1 gs://cert-templates-prod

# Set bucket permissions
gsutil iam ch allUsers:objectViewer gs://cert-templates-prod

# Create lifecycle rule for cleanup
cat > lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 7,
          "matchesPrefix": ["temp/"]
        }
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://cert-templates-prod
```

### 3. Set Up Service Account
```bash
# Create service account
gcloud iam service-accounts create cert-generator-sa \
  --display-name="Certificate Generator Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding cert-generator-prod \
  --member="serviceAccount:cert-generator-sa@cert-generator-prod.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Download service account key (for local testing)
gcloud iam service-accounts keys create ./service-account-key.json \
  --iam-account=cert-generator-sa@cert-generator-prod.iam.gserviceaccount.com
```

## Environment Preparation

### 1. Clone Repository
```bash
git clone <your-repository-url>
cd certificate-generator
```

### 2. Create Production Environment File
```bash
# Create .env.production
cat > .env.production << EOF
# Authentication
USER_PASSWORD=GenerateSecurePasswordHere
ADMIN_PASSWORD=GenerateSecureAdminPasswordHere

# Google Cloud Storage
GCS_BUCKET=cert-templates-prod
USE_LOCAL_STORAGE=false

# Application Settings
MAX_UPLOAD_SIZE=5242880
SESSION_TIMEOUT=1800
RATE_LIMIT=40
WORKERS=4

# Security
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
ALLOWED_HOSTS=cert-generator-prod-xxxx.a.run.app

# Monitoring
ENABLE_LOGGING=true
LOG_LEVEL=INFO
EOF
```

### 3. Update Dockerfile for Production
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmupdf-dev \
    mupdf-tools \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p templates temp local_storage/templates local_storage/generated

# Cloud Run uses PORT environment variable
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run as non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT}/_stcore/health || exit 1

# Start the application
CMD streamlit run app.py \
    --server.port=${PORT} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.serverAddress=0.0.0.0 \
    --browser.gatherUsageStats=false
```

## Building the Container

### 1. Local Build and Test
```bash
# Build the container
docker build -t cert-generator:latest .

# Test locally
docker run -p 8080:8080 \
  -e USER_PASSWORD=testuser123 \
  -e ADMIN_PASSWORD=testadmin456 \
  -e USE_LOCAL_STORAGE=true \
  cert-generator:latest

# Verify at http://localhost:8080
```

### 2. Build for Cloud Run
```bash
# Configure Docker for Google Container Registry
gcloud auth configure-docker

# Build and push to GCR
docker build -t gcr.io/cert-generator-prod/cert-generator:latest .
docker push gcr.io/cert-generator-prod/cert-generator:latest

# Alternative: Use Cloud Build
gcloud builds submit --tag gcr.io/cert-generator-prod/cert-generator:latest
```

## Deploying to Cloud Run

### 1. Initial Deployment
```bash
gcloud run deploy cert-generator \
  --image gcr.io/cert-generator-prod/cert-generator:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --min-instances 1 \
  --timeout 300 \
  --concurrency 10 \
  --service-account cert-generator-sa@cert-generator-prod.iam.gserviceaccount.com \
  --set-env-vars "GCS_BUCKET=cert-templates-prod,USE_LOCAL_STORAGE=false" \
  --set-secrets "USER_PASSWORD=user-password:latest,ADMIN_PASSWORD=admin-password:latest"
```

### 2. Create Secrets (More Secure than Env Vars)
```bash
# Create secrets in Secret Manager
echo -n "YourSecureUserPassword" | gcloud secrets create user-password --data-file=-
echo -n "YourSecureAdminPassword" | gcloud secrets create admin-password --data-file=-

# Grant access to service account
gcloud secrets add-iam-policy-binding user-password \
  --member="serviceAccount:cert-generator-sa@cert-generator-prod.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding admin-password \
  --member="serviceAccount:cert-generator-sa@cert-generator-prod.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 3. Configure Domain (Optional)
```bash
# Map custom domain
gcloud run domain-mappings create \
  --service cert-generator \
  --domain certificates.yourdomain.com \
  --region us-central1

# Verify domain ownership and update DNS as instructed
```

## Post-Deployment Configuration

### 1. Upload Initial Templates
```bash
# Upload sample templates to GCS
gsutil cp templates/*.pdf gs://cert-templates-prod/templates/

# Set proper permissions
gsutil acl ch -r -u AllUsers:R gs://cert-templates-prod/templates/
```

### 2. Configure Monitoring
```bash
# Create uptime check
gcloud monitoring uptime-checks create cert-generator-health \
  --display-name="Certificate Generator Health Check" \
  --resource-type="cloud-run-revision" \
  --service=cert-generator \
  --location=us-central1

# Create alerting policy
gcloud alpha monitoring policies create \
  --notification-channels=your-channel-id \
  --display-name="Certificate Generator Alerts" \
  --condition-display-name="High Error Rate" \
  --condition-threshold-value=5 \
  --condition-threshold-duration=60s
```

### 3. Set Up Logging
```bash
# Create log sink for long-term storage
gcloud logging sinks create cert-generator-sink \
  storage.googleapis.com/cert-generator-logs \
  --log-filter='resource.type="cloud_run_revision" AND resource.labels.service_name="cert-generator"'

# Create log-based metrics
gcloud logging metrics create certificate_generations \
  --description="Count of certificate generations" \
  --log-filter='textPayload:"Generated certificate for"'
```

## Testing the Deployment

### 1. Functional Tests
```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe cert-generator --region us-central1 --format 'value(status.url)')

# Test health endpoint
curl ${SERVICE_URL}/_stcore/health

# Test login (using browser)
echo "Open in browser: ${SERVICE_URL}"
```

### 2. Load Testing
```bash
# Install hey (HTTP load generator)
go install github.com/rakyll/hey@latest

# Run load test
hey -n 1000 -c 10 -m GET ${SERVICE_URL}/_stcore/health

# Monitor in Cloud Console during test
```

### 3. Verification Checklist
- [ ] Application loads without errors
- [ ] User login works
- [ ] Admin login works
- [ ] File upload validates correctly
- [ ] Certificate generation completes
- [ ] Downloads work properly
- [ ] Templates load from GCS
- [ ] Logs appear in Cloud Logging
- [ ] Metrics show in Monitoring

## Monitoring and Maintenance

### 1. Key Metrics to Monitor
- **Request count**: Normal vs spike patterns
- **Latency**: 95th percentile < 2 seconds
- **Error rate**: Should be < 1%
- **CPU utilization**: Target 60-80%
- **Memory usage**: Should be < 80%
- **Cold starts**: Minimize with min instances
- **GCS operations**: Monitor quota usage

### 2. Regular Maintenance Tasks
```bash
# Weekly: Check for security updates
gcloud container images scan cert-generator:latest

# Monthly: Review and clean old logs
gsutil -m rm -r gs://cert-generator-logs/logs/2024/**

# Quarterly: Update base image and dependencies
docker build --no-cache -t gcr.io/cert-generator-prod/cert-generator:latest .

# Annually: Rotate service account keys
gcloud iam service-accounts keys create ./new-key.json \
  --iam-account=cert-generator-sa@cert-generator-prod.iam.gserviceaccount.com
```

### 3. Automated Backups
```bash
# Create Cloud Scheduler job for template backups
gcloud scheduler jobs create storage cert-templates-backup \
  --schedule="0 2 * * *" \
  --uri="https://storage.googleapis.com/storage/v1/b/cert-templates-prod/o" \
  --message-body='{"destination":"gs://cert-backups-prod/templates/"}' \
  --time-zone="UTC"
```

## Troubleshooting Deployment Issues

### Common Issues and Solutions

#### "Container failed to start"
```bash
# Check logs
gcloud run services logs read cert-generator --region us-central1 --limit 50

# Common causes:
# - Missing environment variables
# - Port mismatch (must use $PORT)
# - Dependency issues
```

#### "502 Bad Gateway"
```bash
# Increase timeout
gcloud run services update cert-generator --timeout 600

# Check memory limits
gcloud run services update cert-generator --memory 4Gi
```

#### "Out of Memory"
```bash
# Monitor memory usage
gcloud monitoring dashboards create --config-from-file=dashboard.yaml

# Scale up if needed
gcloud run services update cert-generator --memory 4Gi --cpu 4
```

#### "Slow Performance"
```bash
# Enable CPU boost during startup
gcloud run services update cert-generator --cpu-boost

# Increase min instances to reduce cold starts
gcloud run services update cert-generator --min-instances 2
```

### Debug Commands
```bash
# Get service details
gcloud run services describe cert-generator --region us-central1

# List recent revisions
gcloud run revisions list --service cert-generator --region us-central1

# Stream logs in real-time
gcloud run services logs tail cert-generator --region us-central1

# Check IAM permissions
gcloud projects get-iam-policy cert-generator-prod
```

## Cost Optimization

### 1. Resource Optimization
```yaml
# Optimal settings for most use cases
memory: 1Gi  # Start low, increase if needed
cpu: 1       # 1 CPU is usually sufficient
min-instances: 0  # Set to 1 for faster response
max-instances: 5  # Adjust based on load
concurrency: 10   # Streamlit works well with 10
```

### 2. Storage Optimization
```bash
# Set lifecycle rules for temporary files
gsutil lifecycle set lifecycle-rules.json gs://cert-templates-prod

# Enable Nearline storage for old backups
gsutil rewrite -s nearline gs://cert-backups-prod/**
```

### 3. Cost Monitoring
```bash
# Set up budget alerts
gcloud billing budgets create \
  --billing-account=YOUR-BILLING-ACCOUNT-ID \
  --display-name="Certificate Generator Budget" \
  --budget-amount=100USD \
  --threshold-rule=percent=90

# Export billing data to BigQuery
gcloud billing accounts get-iam-policy YOUR-BILLING-ACCOUNT-ID
```

### 4. Free Tier Optimization
- Cloud Run: 2 million requests/month free
- Cloud Storage: 5GB free storage
- Egress: 1GB North America free
- Cloud Build: 120 build-minutes/day free

## Security Hardening

### 1. Network Security
```bash
# Restrict access by IP (if needed)
gcloud run services update cert-generator \
  --ingress internal-and-cloud-load-balancing

# Enable Cloud Armor
gcloud compute security-policies create cert-generator-policy \
  --description "Certificate Generator Security Policy"
```

### 2. Authentication Hardening
```yaml
# Consider adding Identity-Aware Proxy
gcloud iap settings set cert-generator \
  --member-allowlist=user:admin@company.com
```

### 3. Secrets Rotation
```bash
# Automate password rotation
cat > rotate-passwords.sh << 'EOF'
#!/bin/bash
NEW_USER_PASS=$(openssl rand -base64 32)
NEW_ADMIN_PASS=$(openssl rand -base64 32)

echo -n "$NEW_USER_PASS" | gcloud secrets versions add user-password --data-file=-
echo -n "$NEW_ADMIN_PASS" | gcloud secrets versions add admin-password --data-file=-

gcloud run services update cert-generator --update-secrets \
  USER_PASSWORD=user-password:latest,ADMIN_PASSWORD=admin-password:latest
EOF

chmod +x rotate-passwords.sh
```

## Deployment Checklist

### Pre-Deployment
- [ ] All tests pass locally
- [ ] Dockerfile builds successfully
- [ ] Environment variables documented
- [ ] Secrets created in Secret Manager
- [ ] GCS bucket configured
- [ ] Service account permissions set

### Deployment
- [ ] Image pushed to Container Registry
- [ ] Cloud Run service created
- [ ] Environment variables configured
- [ ] Secrets mounted
- [ ] Health check passes

### Post-Deployment
- [ ] Application accessible
- [ ] Login functionality works
- [ ] File uploads successful
- [ ] Certificate generation works
- [ ] Monitoring configured
- [ ] Alerts set up
- [ ] Backup scheduled
- [ ] Documentation updated

---

**Important**: Always test in a staging environment before deploying to production. Keep this guide updated as the deployment process evolves.