# Streamlit Cloud Deployment Instructions

Your SafeSteps Certificate Generator is now ready for deployment to Streamlit Cloud!

## Deployment Steps

1. **Go to Streamlit Cloud**
   - Visit https://share.streamlit.io/
   - Sign in with your GitHub account

2. **Deploy New App**
   - Click "New app"
   - Select your repository: `Gobidog/safestepscerts`
   - Branch: `main`
   - Main file path: `app.py`

3. **Configure Secrets**
   - Click "Advanced settings"
   - In the "Secrets" section, add the following (copy from `.streamlit/secrets.toml.example`):

   ```toml
   # Generate a secure JWT secret (use a password generator)
   JWT_SECRET = "your-very-secure-jwt-secret-key-here"

   # Optional: Override default passwords
   # USER_PASSWORD = "your-custom-user-password"
   # ADMIN_PASSWORD = "your-custom-admin-password"

   # Optional: For Google Cloud Storage
   # [gcp]
   # BUCKET_NAME = "your-bucket-name"
   # PROJECT_ID = "your-project-id"
   # SERVICE_ACCOUNT_KEY = '''{ your-service-account-json }'''
   ```

4. **Deploy**
   - Click "Deploy!"
   - Wait for the app to build and deploy (usually 2-5 minutes)

## Post-Deployment

1. **Access Your App**
   - Your app will be available at: `https://[your-app-name].streamlit.app/`
   - Default credentials (unless overridden in secrets):
     - Admin: `admin` / `Admin@SafeSteps2024`
     - User: `testuser` / `UserPass123`

2. **First-Time Setup**
   - Log in as admin
   - Upload certificate templates
   - Create additional users if needed

3. **Monitor App**
   - Check app logs in Streamlit Cloud dashboard
   - Monitor usage and performance

## Important Notes

- **JWT_SECRET**: Must be set in secrets for production security
- **File Storage**: Uses local storage by default, configure GCS for persistence
- **Rate Limiting**: App has built-in rate limiting (40 requests/minute)
- **Session Timeout**: Sessions expire after 24 hours

## Troubleshooting

- If app fails to start, check logs in Streamlit Cloud dashboard
- Ensure all dependencies in requirements.txt are compatible
- Verify secrets are properly formatted (TOML syntax)

## Security Checklist

✅ JWT_SECRET is set to a strong, unique value
✅ Default passwords are changed in production
✅ GCS is configured for persistent storage (optional)
✅ Rate limiting is active
✅ HTTPS is enforced (automatic on Streamlit Cloud)