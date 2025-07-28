# Quick Troubleshooting Reference

## Most Common Issues - Quick Fixes

### ✅ PDF GENERATION FIXED (July 2025)
**Issue**: Admin certificate generation crashed with TypeError
**Status**: ✅ **COMPLETELY RESOLVED**
- PDFGenerator constructor now properly uses template_path parameter
- Template path validation prevents file-not-found errors
- Admin workflow fully functional end-to-end

### ✅ ENVIRONMENT LOADING STANDARDIZED
**Issue**: Inconsistent dotenv loading across contexts
**Status**: ✅ **COMPLETELY RESOLVED**
- Unified environment loading with graceful fallback
- JWT_SECRET consistency maintained across all contexts
- Error handling prevents application crashes

### ✅ TEMPLATE SYSTEM HARDENED
**Issue**: KeyError crashes for templates without display_name
**Status**: ✅ **COMPLETELY RESOLVED**
- Graceful fallback for incomplete template metadata
- All template combinations tested and working

### 1. Sessions Lost on Restart ⚠️ CRITICAL
```bash
# Generate persistent JWT secret
JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Set in environment (Cloud Run)
gcloud run services update certificate-generator \
  --set-env-vars="JWT_SECRET=$JWT_SECRET"

# Or add to .env file
echo "JWT_SECRET=$JWT_SECRET" >> .env
```

### 2. Templates Disappear
```bash
# Configure GCS
gcloud run services update certificate-generator \
  --set-env-vars="GCS_BUCKET_NAME=your-bucket,USE_LOCAL_STORAGE=false"
```

### 3. Frontend Won't Load
```bash
# Clear browser cache: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
# Or upgrade dependencies:
pip install --upgrade streamlit pandas PyMuPDF
```

### 4. Navigation Menu Not Visible
```css
# ISSUE: Admin navigation menu completely missing
# CAUSE: CSS rule hiding entire header element
# FIX: Comment out problematic rule and use specific selector

/* WRONG - hides navigation menu */
header {visibility: hidden;}

/* CORRECT - hides only Streamlit toolbar */
/* header {visibility: hidden;} -- REMOVED */
[data-testid="stToolbar"] {visibility: hidden;}
```

### 5. Navigation API Issues
```python
# Use correct API for your Streamlit version
import streamlit as st

# Streamlit 1.28+
if st.button("Navigate"):
    st.switch_page("pages/target.py")

# Older versions
if st.button("Navigate"):
    st.experimental_rerun()
```

## Emergency Commands

### Quick Restart
```bash
gcloud run services update certificate-generator --no-traffic
gcloud run services update certificate-generator --traffic=LATEST=100
```

### Reset All Sessions
```bash
# WARNING: Logs out all users
NEW_JWT=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
gcloud run services update certificate-generator \
  --set-env-vars="JWT_SECRET=$NEW_JWT"
```

### Check App Health
```bash
curl -I https://your-app-url.run.app/_stcore/health
```

### View Recent Errors
```bash
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" --limit 10
```

## Pre-Deployment Checklist
- [ ] JWT_SECRET set in environment
- [ ] GCS bucket configured (USE_LOCAL_STORAGE=false)
- [ ] Dependencies upgraded and tested
- [ ] Browser cache cleared
- [ ] Navigation tested on all pages
- [ ] **PDF generation workflow verified** ✅ **NOW WORKING**
- [ ] **Admin certificate generation tested** ✅ **NO CRASHES**
- [ ] **Environment loading tested across contexts** ✅ **STANDARDIZED**
- [ ] **Template system robustness confirmed** ✅ **HARDENED**

## Need More Help?
See full guide: `/docs/STREAMLIT_TROUBLESHOOTING.md`