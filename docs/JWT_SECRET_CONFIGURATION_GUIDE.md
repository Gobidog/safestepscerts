# JWT_SECRET Configuration Guide

## Overview

As of July 2025, the SafeSteps Certificate Generator includes enhanced configuration validation that prevents deployment issues on Streamlit Cloud. The application will now fail immediately with clear, actionable error messages if JWT_SECRET is not configured.

## Why JWT_SECRET is Required

JWT_SECRET is critical for:
- **Session persistence**: Maintains user login state across app restarts
- **Security**: Signs and validates authentication tokens
- **CSRF protection**: Secures forms against cross-site request forgery
- **Data integrity**: Ensures session data hasn't been tampered with

Without JWT_SECRET, the application cannot maintain secure sessions and will not start.

## Configuration Instructions

### For Streamlit Cloud

When you deploy to Streamlit Cloud without configuring JWT_SECRET, you'll see:

```
🚨 Configuration Error
JWT_SECRET environment variable is not set!

📱 Streamlit Cloud Users:
1. Go to your app settings
2. Click 'Secrets' in the menu
3. Add: JWT_SECRET = "your-generated-secret"
4. Redeploy your app
```

To fix this:

1. **Generate a secure JWT_SECRET**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   
2. **Add to Streamlit Cloud Secrets**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Find your app and click the three dots menu (⋮)
   - Select "Settings" → "Secrets"
   - Add:
     ```toml
     JWT_SECRET = "your-generated-secret-here"
     ```
   - Click "Save"

3. **App will automatically restart** with the configuration

### For Local Development

1. **Create a .env file**:
   ```bash
   cp .env.example .env
   ```

2. **Generate and add JWT_SECRET**:
   ```bash
   # Generate secret
   python -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))"
   
   # Add to .env file
   echo 'JWT_SECRET=your-generated-secret' >> .env
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

### For Docker Deployment

```bash
docker run -p 8080:8080 \
  -e JWT_SECRET="your-generated-secret" \
  -e ADMIN_PASSWORD="your-admin-password" \
  cert-generator
```

### For Google Cloud Run

```bash
gcloud run deploy cert-generator \
  --set-env-vars JWT_SECRET="your-generated-secret"
```

## Security Best Practices

1. **Generate Strong Secrets**:
   - Use at least 32 characters
   - Use cryptographically secure random generation
   - Never use predictable values

2. **Keep Secrets Secret**:
   - Never commit JWT_SECRET to version control
   - Don't share JWT_SECRET between environments
   - Rotate secrets periodically (every 90 days)

3. **Handle Secret Rotation**:
   - Changing JWT_SECRET invalidates all existing sessions
   - Plan rotations during maintenance windows
   - Notify users before rotation

## Troubleshooting

### "Configuration Error" persists after adding JWT_SECRET

1. **Verify the secret is saved** in Streamlit Cloud secrets
2. **Wait for app restart** (usually automatic, but can take 1-2 minutes)
3. **Check for typos** in the secret name (must be exactly `JWT_SECRET`)
4. **Hard refresh** your browser (Ctrl+F5 or Cmd+Shift+R)

### Sessions still lost after restart

1. **Verify JWT_SECRET hasn't changed** between deployments
2. **Check that the same secret** is used across all instances
3. **Ensure secret persistence** in your deployment platform

### Local development works but Streamlit Cloud doesn't

1. **Confirm secrets are configured** in Streamlit Cloud (not just locally)
2. **Use the Streamlit Cloud secrets format** (TOML syntax)
3. **Check for environment detection** - the app detects Streamlit Cloud automatically

## Technical Details

The configuration validation happens in two places:

1. **app.py** - Early validation on startup:
   ```python
   try:
       from config import validate_environment
       validate_environment()
   except EnvironmentError as e:
       st.error("🚨 Configuration Error")
       st.error(str(e))
       st.stop()
   ```

2. **config.py** - Platform-aware error messages:
   ```python
   if "STREAMLIT" in os.environ:
       # Show Streamlit Cloud specific instructions
   ```

This ensures users get helpful, platform-specific guidance instead of cryptic authentication errors.

## Additional Resources

- [Streamlit Cloud Secrets Documentation](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)
- [Environment Variables Security](https://12factor.net/config)