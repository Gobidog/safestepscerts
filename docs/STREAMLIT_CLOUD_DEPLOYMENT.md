# Streamlit Cloud Deployment Guide

⚠️ **IMPORTANT**: As of July 2025, the application includes enhanced configuration validation that will immediately alert you if JWT_SECRET is not configured, preventing deployment confusion.

## Prerequisites

Before deploying to Streamlit Cloud, ensure you have:
- A GitHub repository with your application code
- A Streamlit Cloud account (free at share.streamlit.io)
- Generated a secure JWT_SECRET token (instructions below)

## Step 1: Generate JWT_SECRET

Generate a secure JWT_SECRET token by running:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Save this token - you'll need it in Step 3.

## Step 2: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. Select the branch and main file (app.py)
5. Click "Deploy"

**Expected behavior**: The app will deploy but show a configuration error. This is normal and expected! The error message will guide you to configure JWT_SECRET in the next step.

## Step 3: Configure Secrets (CRITICAL)

🔴 **The app will not work until you complete this step!**

After deployment, you MUST configure the JWT_SECRET. The app will display clear instructions, but here's what to do:

1. When you first visit your deployed app, you'll see:
   ```
   🚨 Configuration Error
   JWT_SECRET environment variable is not set!
   
   📱 Streamlit Cloud Users:
   1. Go to your app settings
   2. Click 'Secrets' in the menu
   3. Add: JWT_SECRET = "your-generated-secret"
   4. Redeploy your app
   ```

2. Go to your app's dashboard on Streamlit Cloud
3. Click the three dots menu (⋮) next to your app
4. Select "Settings"
5. Click on "Secrets" in the left sidebar
6. Add the following configuration:

```toml
# Required for authentication
JWT_SECRET = "your-generated-secret-from-step-1"

# Optional: Override default passwords
ADMIN_PASSWORD = "YourSecureAdminPassword123!"
USER_PASSWORD = "YourSecureUserPassword123!"

# Optional: Cloud storage configuration
USE_LOCAL_STORAGE = "true"
# GCS_PROJECT_ID = "your-project-id"
# GCS_BUCKET_NAME = "your-bucket-name"
```

6. Click "Save"
7. Your app will automatically restart with the new configuration

## Step 4: Verify Deployment

1. Visit your deployed app URL
2. You should see the login page without any configuration errors
3. Test login with the default credentials:
   - Admin: `admin` / `Admin@SafeSteps2024` (or your custom ADMIN_PASSWORD)
   - User: `testuser` / `Test@User2024`

## Common Issues

### "Configuration Error: JWT_SECRET not set"

**This is the expected behavior on first deployment!** The application now includes smart configuration validation that:
- Detects when JWT_SECRET is missing
- Shows platform-specific instructions
- Prevents confusing authentication errors later

Simply follow the instructions shown in the error message or Step 3 above.

### "Invalid username/password"

If using custom passwords, ensure they're correctly set in Streamlit Cloud secrets and match what you're entering.

### App crashes on startup

Check the logs in Streamlit Cloud dashboard for specific error messages. Common causes:
- Missing dependencies in requirements.txt
- Incorrect Python version
- File path issues (use relative paths)

## Security Best Practices

1. **Never commit secrets to GitHub** - Always use Streamlit Cloud secrets
2. **Use strong passwords** - Generate secure passwords for production
3. **Rotate JWT_SECRET regularly** - Update every 90 days
4. **Monitor access logs** - Check app logs for suspicious activity
5. **Limit admin accounts** - Only create admin users when necessary

## Environment Variables Reference

| Variable | Required | Description | Default | Notes |
|----------|----------|-------------|---------|---------|
| JWT_SECRET | **Yes** | Secret key for JWT tokens | None - MUST be set | App shows clear error if missing |
| ADMIN_PASSWORD | No | Admin user password | Admin@SafeSteps2024 | Used for default admin account |
| USER_PASSWORD | No | Default user password | UserPass123 | Used for default test user |
| USE_LOCAL_STORAGE | No | Use local file storage | true | Set to false for GCS |
| GCS_PROJECT_ID | No | Google Cloud project ID | None | Required if USE_LOCAL_STORAGE=false |
| GCS_BUCKET_NAME | No | GCS bucket for templates | None | Required if USE_LOCAL_STORAGE=false |

## Support

If you encounter issues:
1. Check the app logs in Streamlit Cloud dashboard
2. Verify all required secrets are configured
3. Ensure your repository is up to date
4. Contact your administrator for assistance