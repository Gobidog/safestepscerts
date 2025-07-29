# Deployment Recovery Guide - SafeSteps Certificate Generator

## Overview

This guide provides step-by-step instructions for recovering from deployment synchronization failures where Streamlit Cloud runs outdated code despite new commits being pushed to the repository.

## Symptoms of Deployment Sync Failure

You may be experiencing a deployment sync failure if:

1. **Code changes not reflected**: Git commits are successful but Streamlit Cloud shows old code
2. **Version mismatch**: Footer shows old commit hash instead of latest
3. **Features missing**: New features or fixes don't appear on the deployed site
4. **Template management broken**: Admin features that work locally fail on cloud
5. **Unexpected errors**: Application behaves as if running older code version
6. **Progress bars show HTML**: Instead of visual components, raw HTML markup is displayed

## Common Causes

1. **Cached deployment**: Streamlit Cloud cached an older deployment
2. **Failed automatic redeploy**: Git webhook didn't trigger proper redeployment
3. **Dependency conflicts**: Version mismatches preventing successful deployment
4. **Configuration issues**: Missing or incorrect environment variables
5. **Build failures**: Silent failures during container building

## Step-by-Step Recovery Process

### Step 1: Verify the Problem

1. **Check Git status**:
   ```bash
   git log --oneline -n 5
   ```
   Note the latest commit hash.

2. **Check deployed version**:
   - Visit your Streamlit Cloud app
   - Look at the footer for the version/commit hash
   - Compare with your latest Git commit

3. **Verify code differences**:
   ```bash
   git diff HEAD~1 HEAD
   ```
   Confirm your changes are actually committed.

### Step 2: Force Redeployment

#### Method A: Through Streamlit Cloud Dashboard (Recommended)

1. **Access Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Log in to your account
   - Find your app in the dashboard

2. **Force reboot**:
   - Click the three dots menu (⋮) next to your app
   - Select "Reboot app"
   - Wait for the reboot to complete (2-5 minutes)

3. **Monitor logs**:
   - Click "Manage app" → "Logs"
   - Watch for deployment messages
   - Look for any error messages

#### Method B: Through Code Changes

1. **Make a meaningful change**:
   ```python
   # Add to app.py or any main file
   # Deployment sync fix - [current date]
   __deployment_sync_fix__ = "2025-01-29"
   ```

2. **Update requirements.txt**:
   ```bash
   # Pin specific versions to force rebuild
   streamlit==1.31.0
   PyMuPDF==1.23.26
   pandas==2.2.0
   ```

3. **Commit and push**:
   ```bash
   git add -A
   git commit -m "Force deployment sync - pin dependencies"
   git push origin main
   ```

#### Method C: Delete and Recreate App

If methods A and B fail:

1. **Delete the app**:
   - In Streamlit Cloud dashboard
   - Click three dots → "Delete app"
   - Confirm deletion

2. **Recreate the app**:
   - Click "New app"
   - Select same repository and branch
   - Configure all environment variables
   - Deploy

### Step 3: Verify Deployment

1. **Check deployment status**:
   - Watch the deployment logs
   - Ensure no errors during build
   - Wait for "Your app is ready" message

2. **Verify functionality**:
   - Test all critical features
   - Check version in footer
   - Verify template management works
   - Test authentication

3. **Monitor performance**:
   - Check response times
   - Verify no visual glitches
   - Test file uploads

### Step 4: Post-Recovery Actions

1. **Document the issue**:
   ```python
   # Add to deployment_verification.py
   deployment_notes = {
       "date": "2025-01-29",
       "issue": "Deployment sync failure",
       "resolution": "Forced redeployment via dashboard",
       "commit": "53e7c9a"
   }
   ```

2. **Set up monitoring**:
   - Create a simple health check endpoint
   - Monitor version numbers
   - Set up alerts for deployment failures

3. **Update documentation**:
   - Record the issue in your project log
   - Update this guide with any new findings
   - Share with team members

## Verification Steps

After recovery, verify these critical functions:

### 1. Authentication System
```python
# Test logins work correctly
# Admin: admin / Admin@SafeSteps2024 (local) or Gobi2004! (cloud)
# User: testuser / UserPass123 (local) or Safesteps! (cloud)
```

### 2. Template Management
- Upload a test template
- Verify it appears in the list
- Test template deletion
- Check template usage in generation

### 3. Certificate Generation
- Upload a test CSV
- Select a template
- Generate certificates
- Download results

### 4. Visual Components
- Progress bars render correctly
- No raw HTML visible
- UI elements display properly

## Prevention Strategies

### 1. Deployment Verification System

Add a deployment verification file to your project:

```python
# monitor_deployment.py
import streamlit as st
import subprocess
import os
from datetime import datetime

def get_deployment_info():
    """Get current deployment information"""
    try:
        # Get git commit hash
        commit = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD']
        ).decode('ascii').strip()[:8]
    except:
        commit = "unknown"
    
    return {
        "commit": commit,
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "streamlit_version": st.__version__
    }

# Display in footer
if __name__ == "__main__":
    info = get_deployment_info()
    st.sidebar.markdown(f"Version: {info['commit']}")
```

### 2. Dependency Management

Always pin critical dependencies:

```txt
# requirements.txt
streamlit==1.31.0  # Pin exact version
PyMuPDF==1.23.26   # Critical - fixes align parameter issue
pandas==2.2.0
python-dotenv==1.0.0
bcrypt==4.1.2
PyJWT==2.8.0
google-cloud-storage==2.10.0
Pillow==10.2.0
openpyxl==3.1.2
```

### 3. Git Commit Best Practices

Structure commits to trigger deployments:

```bash
# Good commit messages that trigger deployment
git commit -m "Fix: Template upload functionality [deploy]"
git commit -m "Update: Requirements.txt with pinned versions"
git commit -m "Feature: Add deployment verification system"

# Tag important deployments
git tag -a v1.2.3 -m "Stable release with template fixes"
git push origin v1.2.3
```

### 4. Environment Variable Management

Ensure all required variables are set:

```python
# config.py
required_vars = [
    "JWT_SECRET",
    "ADMIN_PASSWORD",
    "USER_PASSWORD",
    "GCS_BUCKET"
]

for var in required_vars:
    if not os.getenv(var):
        st.error(f"Missing required environment variable: {var}")
        st.stop()
```

## Troubleshooting Specific Issues

### Issue: PyMuPDF Align Parameter Error

**Symptom**: `TypeError: insert_textbox() got an unexpected keyword argument 'align'`

**Solution**:
1. Pin PyMuPDF to version 1.23.26 in requirements.txt
2. Remove the align parameter from PDF generation code
3. Force redeployment

### Issue: Progress Bars Show HTML

**Symptom**: Raw HTML like `<progress value="50" max="100">` displayed

**Solution**:
1. Update Streamlit to latest version (1.31.0+)
2. Use `st.progress()` instead of HTML progress elements
3. Clear browser cache after deployment

### Issue: Authentication Credentials Don't Work

**Symptom**: Correct passwords rejected on cloud deployment

**Solution**:
1. Verify JWT_SECRET is set in Streamlit Cloud secrets
2. Check if using correct cloud passwords (may differ from local)
3. Ensure users.json is properly initialized

## Emergency Contacts and Resources

### Streamlit Cloud Support
- Documentation: https://docs.streamlit.io/streamlit-cloud
- Community Forum: https://discuss.streamlit.io/
- Status Page: https://status.streamlit.io/

### Quick Commands Reference

```bash
# Check deployment status
git log --oneline -n 1
git status

# Force clean deployment
git add -A
git commit -m "Force deployment sync [deploy]"
git push origin main

# Verify deployment
curl https://your-app.streamlit.app/ -I
```

## Recovery Checklist

- [ ] Identified deployment sync symptoms
- [ ] Verified Git commits are pushed
- [ ] Attempted dashboard reboot
- [ ] Checked deployment logs for errors
- [ ] Pinned dependency versions if needed
- [ ] Forced redeployment successfully
- [ ] Verified all features working
- [ ] Documented issue and resolution
- [ ] Updated monitoring/verification

## Lessons Learned

1. **Always pin critical dependencies** - Especially PyMuPDF which has breaking changes
2. **Monitor deployment versions** - Add version display in UI footer
3. **Test immediately after push** - Don't assume automatic deployment worked
4. **Keep deployment logs** - Document what worked for future reference
5. **Have rollback plan** - Know how to revert if new deployment fails

---

**Last Updated**: 2025-01-29
**Status**: Comprehensive guide based on successful recovery from deployment sync failure