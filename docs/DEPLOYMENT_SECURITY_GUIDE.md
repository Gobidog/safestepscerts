# Production Deployment Security Guide

## 🚨 CRITICAL Security Requirements

This guide covers essential security configurations required before deploying the Certificate Generator to production.

## 1. Environment Variables Setup

### Required Security Variables

```bash
# JWT Secret - MUST be set for session persistence
# ⚠️ CRITICAL: Without this, all sessions are lost on restart!
JWT_SECRET=<generate-with-command-below>

# Production Passwords - MUST change from defaults
# Passwords must be 8+ chars with uppercase, lowercase, and numbers
USER_PASSWORD=<generate-secure-password>
ADMIN_PASSWORD=<generate-secure-password>

# Additional Security Settings
ENABLE_CSRF_PROTECTION=true  # Required for production
RATE_LIMIT_REQUESTS=100      # Requests per hour per session
RATE_LIMIT_WINDOW_SECONDS=3600
```

### Generate Secure Values

```bash
# Generate JWT Secret (32+ characters)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate Secure Passwords (16+ characters)
python -c "import secrets; print(secrets.token_urlsafe(16))"
```

### ⚠️ WARNING: Default Passwords

The application will NOT start if USER_PASSWORD or ADMIN_PASSWORD are not set in environment variables. This prevents accidental deployment with default credentials.

## 2. Google Cloud Storage Configuration

Templates are stored in memory by default and will be LOST on container restart. Configure GCS for persistence:

### Option A: Service Account Key (Development)

```bash
# Set in .env
GCS_BUCKET_NAME=your-cert-templates-bucket
GCS_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
USE_LOCAL_STORAGE=false
```

### Option B: Workload Identity (Recommended for Cloud Run)

1. Create a GCS bucket:
```bash
gsutil mb gs://your-cert-templates-bucket
```

2. Create a service account:
```bash
gcloud iam service-accounts create cert-generator-sa \
  --display-name="Certificate Generator Service Account"
```

3. Grant storage permissions:
```bash
gsutil iam ch serviceAccount:cert-generator-sa@YOUR-PROJECT.iam.gserviceaccount.com:objectAdmin \
  gs://your-cert-templates-bucket
```

4. Deploy with service account:
```bash
gcloud run deploy certificate-generator \
  --service-account=cert-generator-sa@YOUR-PROJECT.iam.gserviceaccount.com \
  --set-env-vars="GCS_BUCKET_NAME=your-cert-templates-bucket,GCS_PROJECT_ID=YOUR-PROJECT,USE_LOCAL_STORAGE=false"
```

## 3. Cloud Run Deployment

### Build and Deploy Commands

```bash
# 1. Build container
gcloud builds submit --tag gcr.io/YOUR-PROJECT/certificate-generator

# 2. Create .env.production from .env.production.example
cp .env.production.example .env.production
# Edit .env.production with your secure values

# 3. Deploy with environment variables
gcloud run deploy certificate-generator \
  --image gcr.io/YOUR-PROJECT/certificate-generator \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars-from-file=.env.production \
  --memory=1Gi \
  --cpu=1 \
  --timeout=300 \
  --max-instances=10
```

### Security Best Practices for Cloud Run

1. **Enable Cloud Armor** (DDoS protection):
```bash
gcloud compute security-policies create cert-gen-policy \
  --description "Security policy for certificate generator"
```

2. **Set up Identity-Aware Proxy** (if internal use only):
```bash
gcloud run services add-iam-policy-binding certificate-generator \
  --member="domain:yourdomain.com" \
  --role="roles/run.invoker"
```

3. **Configure VPC Connector** (for private resources):
```bash
gcloud run services update certificate-generator \
  --vpc-connector=projects/YOUR-PROJECT/locations/us-central1/connectors/vpc-connector
```

## 4. Security Checklist

Before deploying to production, verify:

- [ ] JWT_SECRET is set and persistent (not using default generation)
- [ ] USER_PASSWORD is changed from default and secure
- [ ] ADMIN_PASSWORD is changed from default and secure
- [ ] GCS is configured for template persistence
- [ ] ENABLE_CSRF_PROTECTION=true
- [ ] DEBUG=false
- [ ] Rate limiting is configured appropriately
- [ ] HTTPS is enforced (Cloud Run does this automatically)
- [ ] Session timeout is appropriate for your use case
- [ ] File upload limits are set correctly
- [ ] Password strength requirements enforced (8+ chars, mixed case, numbers)
- [ ] Audit logging enabled for admin actions
- [ ] File content validation enabled (not just extension checking)
- [ ] Path traversal protection in place
- [ ] Error messages don't leak sensitive information

## 5. Post-Deployment Verification

### Test Session Persistence

1. Deploy the application
2. Login and create a session
3. Upload a template
4. Restart the Cloud Run service:
   ```bash
   gcloud run services update certificate-generator --no-traffic
   ```
5. Verify you're still logged in (JWT secret working)
6. Verify templates still exist (GCS working)

### Security Audit Commands

```bash
# Check environment variables (without showing values)
gcloud run services describe certificate-generator --format="value(spec.template.spec.containers[0].env[].name)"

# Check service account permissions
gcloud projects get-iam-policy YOUR-PROJECT \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:cert-generator-sa@*"

# Monitor for errors
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" --limit 50
```

## 6. Monitoring and Alerts

Set up monitoring for security events:

```bash
# Create alert for failed login attempts
gcloud logging metrics create failed_logins \
  --description="Failed login attempts" \
  --log-filter='jsonPayload.message=~"Failed login attempt"'

# Create alert for session hijacking attempts
gcloud logging metrics create session_hijacking \
  --description="Potential session hijacking" \
  --log-filter='jsonPayload.message=~"session hijacking"'
```

## 7. Backup and Recovery

### Template Backup Strategy

```bash
# Backup templates from GCS
gsutil -m cp -r gs://your-cert-templates-bucket/templates ./backup/

# Restore templates to GCS
gsutil -m cp -r ./backup/templates gs://your-cert-templates-bucket/
```

### Database Considerations

Currently, passwords are hashed in memory. For production scale, consider:
- External session store (Redis/Memorystore)
- User database (Cloud SQL/Firestore)
- Audit log persistence (BigQuery)

## 8. Emergency Procedures

### Disable Access Quickly

```bash
# Set traffic to 0%
gcloud run services update-traffic certificate-generator --to-revisions=LATEST=0

# Or delete the service
gcloud run services delete certificate-generator
```

### Rotate Credentials

If credentials are compromised:

1. Generate new JWT_SECRET
2. Generate new passwords
3. Update Cloud Run environment
4. Force all users to re-login

```bash
# Update all at once
gcloud run services update certificate-generator \
  --set-env-vars="JWT_SECRET=NEW_SECRET,USER_PASSWORD=NEW_PASS,ADMIN_PASSWORD=NEW_ADMIN"
```

## Common Issues and Solutions

### Issue: Sessions lost on restart
**Solution**: Ensure JWT_SECRET is set in environment variables

⚠️ **CRITICAL**: The JWT_SECRET must be:
- Set explicitly in environment (not auto-generated)
- The same across all application instances
- Never changed once in production
- At least 32 characters long

### Issue: Templates disappear
**Solution**: Configure GCS properly and ensure USE_LOCAL_STORAGE=false

### Issue: Rate limiting too restrictive
**Solution**: Adjust RATE_LIMIT_REQUESTS and RATE_LIMIT_WINDOW_SECONDS

### Issue: File uploads failing
**Solution**: Check MAX_UPLOAD_SIZE_MB and Cloud Run timeout settings

## Support

For security issues, contact your security team immediately. Do not post security vulnerabilities in public forums.