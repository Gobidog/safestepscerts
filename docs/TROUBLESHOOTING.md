# Certificate Generator - Troubleshooting Guide

## Quick Troubleshooting Checklist

Before diving into specific issues, try these steps:

1. ✓ Clear your browser cache and cookies
2. ✓ Try a different browser (Chrome recommended)
3. ✓ Check your internet connection
4. ✓ Ensure you're using the correct login credentials
5. ✓ Verify your file meets requirements (CSV/XLSX, <5MB, required columns)

## Common Issues and Solutions

### Login Issues

#### "Invalid username or password"
**Symptoms**: Can't log in despite using correct credentials

**Solutions**:
1. Verify credentials with your administrator
2. Check CAPS LOCK is off
3. Try copy-pasting password to avoid typos
4. Clear browser cookies for this site
5. Try incognito/private browsing mode

**Still not working?**
- Password may have been changed by admin
- Account may be temporarily locked
- Contact administrator for password reset

#### "Session expired - Please login again"
**Symptoms**: Logged out automatically while working

**Cause**: 30-minute inactivity timeout

**Solutions**:
1. Log in again with your credentials
2. Save your work frequently
3. Keep the tab active if working on large batches

#### Sessions Lost After Application Restart (Admin Issue)
**Symptoms**: All users logged out when application restarts

**Cause**: JWT_SECRET not configured in environment variables

**Solutions for Admins**:
1. Ensure JWT_SECRET is set in environment:
   ```bash
   # Generate a persistent secret
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
2. Add to deployment configuration
3. Use same JWT_SECRET across all instances
4. Never change JWT_SECRET unless absolutely necessary

⚠️ **Warning**: Without JWT_SECRET set, all sessions will be lost whenever the application restarts!

### File Upload Issues

#### "No file selected" or upload button not working
**Symptoms**: Can't select or upload files

**Solutions**:
1. Check file explorer opens when clicking "Browse"
2. Try drag-and-drop instead
3. Ensure file size is under 5MB
4. Check browser permissions for file access
5. Disable browser extensions temporarily

#### "Invalid file format"
**Symptoms**: File rejected immediately after selection

**Causes & Solutions**:

| Issue | Solution |
|-------|----------|
| Wrong file type | Use only .csv or .xlsx files |
| Corrupted file | Re-save in Excel or Google Sheets |
| Old Excel format | Save as .xlsx (not .xls) |
| Numbers/Pages file | Export to CSV or Excel format |

#### "Required columns 'first_name' and 'last_name' not found"
**Symptoms**: File uploads but validation fails

**Solutions by cause**:

1. **Wrong column names**:
   ```
   ❌ First Name, Last Name
   ❌ firstname, lastname  
   ❌ first_Name, last_Name
   ✓ first_name, last_name
   ```

2. **Extra spaces**:
   - Remove spaces in column headers
   - Trim column names in Excel

3. **Hidden characters**:
   - Copy column names to Notepad
   - Retype them manually
   - Save file as CSV UTF-8

4. **Wrong row**:
   - Ensure headers are in row 1
   - Remove any title rows above headers

#### "File contains no data"
**Symptoms**: File accepted but shows 0 rows

**Solutions**:
1. Check file actually has data rows
2. Remove blank rows at the top
3. Ensure data starts in row 2 (after headers)
4. Save and close file in Excel before uploading
5. Try CSV format instead of XLSX

#### "File exceeds maximum size"
**Symptoms**: Large files rejected

**Solutions**:
1. Check file size (must be <5MB)
2. Remove unnecessary columns
3. Split into multiple smaller files:
   - 250 rows per file recommended
   - Use Excel's filter feature to split

### Certificate Generation Issues

#### "Generation failed" or stuck on progress
**Symptoms**: Progress bar stops or shows error

**Solutions by scenario**:

1. **Stuck at 0%**:
   - Refresh page and try again
   - Check template was selected
   - Verify preview worked first

2. **Stuck midway**:
   - Wait 2-3 minutes (may be processing)
   - Note the last successful number
   - Check for special characters in names at that position

3. **Network error**:
   - Check internet connection
   - Try smaller batch
   - Disable VPN if using one

#### "Some certificates failed to generate"
**Symptoms**: Partial success with some errors

**Common causes**:
1. **Empty names**: Check for blank cells
2. **Special characters**: Remove or replace: `/ \ : * ? " < > |`
3. **Extremely long names**: Shorten to reasonable length
4. **Control characters**: Clean data in Excel first

**Data cleaning in Excel**:
```excel
=TRIM(CLEAN(A2))  // Removes extra spaces and control characters
```

#### "Preview looks wrong"
**Symptoms**: Names cut off, wrong position, or formatting issues

**Solutions**:
1. Try a different template
2. Shorten very long names
3. Check for extra spaces in names
4. Verify template has form fields (admin task)

### Download Issues

#### "Download button not working"
**Symptoms**: Clicking download does nothing

**Solutions**:
1. **Pop-up blocked**: Allow pop-ups for this site
2. **Download blocked**: Check browser security settings
3. **Full disk**: Ensure space in Downloads folder
4. **Try alternative**:
   - Right-click > Save As
   - Different browser
   - Disable ad blockers

#### "ZIP file is corrupted"
**Symptoms**: Can't open downloaded ZIP file

**Solutions**:
1. Re-download (don't use download manager)
2. Check file size (shouldn't be 0 KB)
3. Try different extraction tool:
   - Windows: Built-in or 7-Zip
   - Mac: Built-in or The Unarchiver
4. Download again before 1-hour expiry

#### "Certificates missing from ZIP"
**Symptoms**: ZIP contains fewer files than expected

**Possible causes**:
1. Some generations failed (check summary)
2. Duplicate names (combined in same file)
3. Download interrupted

**Solution**: Check generation summary for actual count

### Performance Issues

#### "Application is very slow"
**Symptoms**: Long loading times, timeouts

**Solutions by area**:

1. **Login slow**:
   - Clear browser cache
   - Try different network
   - Non-peak hours (9-10 AM, 2-3 PM)

2. **Upload slow**:
   - Reduce file size
   - Check internet upload speed
   - Try wired connection

3. **Generation slow**:
   - Normal for large batches
   - 100 certificates = ~1 minute
   - 500 certificates = ~5 minutes

#### "Timeout errors"
**Symptoms**: "Request timeout" or similar messages

**Solutions**:
1. Process smaller batches (50-100 rows)
2. Improve internet connection
3. Try during off-peak hours
4. Contact admin if persistent

### Display Issues

#### "Page layout broken"
**Symptoms**: Buttons misaligned, text overlapping

**Solutions**:
1. **Browser zoom**: Reset to 100% (Ctrl/Cmd + 0)
2. **Window size**: Use full-screen mode
3. **Browser**: Update to latest version
4. **Extensions**: Disable styling extensions
5. **Cache**: Hard refresh (Ctrl/Cmd + Shift + R)

#### "Can't see all options"
**Symptoms**: Missing buttons or cut-off content

**Solutions**:
1. Increase window size
2. Check minimum resolution (1280x720)
3. Try different browser
4. Disable browser toolbars

### Admin-Specific Issues

#### "Can't upload templates"
**Symptoms**: Template upload fails

**Validation checklist**:
- [ ] PDF has form fields (not just text)
- [ ] Fields named exactly: `FirstName`, `LastName`
- [ ] File size under 10MB
- [ ] PDF not password protected
- [ ] PDF version 1.4 or higher

**Creating proper templates**:
1. Use Adobe Acrobat (not Reader)
2. Add form fields with exact names
3. Test with small batch first

#### "Password change not working"
**Symptoms**: Can't update passwords

**Requirements**:
- Current admin password must be correct
- New password minimum 8 characters
- Both password fields must match
- No spaces in password

#### "Statistics not updating"
**Symptoms**: Usage counts seem wrong

**Solutions**:
1. Wait 5 minutes for update
2. Refresh page (F5)
3. Clear browser cache
4. Check timezone settings

### Error Messages Explained

| Error Message | Meaning | Solution |
|---------------|---------|----------|
| "Invalid file format" | Wrong file type | Use .csv or .xlsx only |
| "Required columns missing" | Headers incorrect | Check column names exactly |
| "File too large" | Over 5MB limit | Reduce file size |
| "No data found" | Empty file | Add data rows |
| "Session expired" | Timeout after 30 min | Log in again |
| "Generation failed" | Processing error | Check data and retry |
| "Network error" | Connection issue | Check internet |
| "Permission denied" | Access restricted | Check user type |
| "Template not found" | Missing template | Contact admin |
| "Rate limit exceeded" | Too many requests | Wait 1 minute |
| "Invalid or missing CSRF token" | Security token expired | Refresh page and retry |
| "Please login to access this page" | Session lost or expired | Log in again |
| "TypeError: insert_textbox() got an unexpected keyword argument 'align'" | PyMuPDF version mismatch | Update requirements.txt with PyMuPDF==1.23.26 |
| Progress bars show HTML markup | Streamlit rendering issue | Update Streamlit version or force redeploy |

### Advanced Troubleshooting

#### Browser Console Errors
To check for technical errors:

1. Open browser console:
   - Chrome/Edge: F12 or Ctrl+Shift+J
   - Firefox: F12 or Ctrl+Shift+K
   - Safari: Cmd+Option+C

2. Look for red error messages

3. Common console errors:
   - `NetworkError`: Connection issues
   - `403 Forbidden`: Authentication problem
   - `500 Internal Server`: Server issue
   - `WebSocket closed`: Session timeout

#### Network Diagnostics
1. Check connection speed: fast.com
2. Ping test to server
3. Try mobile hotspot
4. Disable VPN/proxy

#### Data Validation
```python
# Python script to validate CSV
import pandas as pd

df = pd.read_csv('your_file.csv')
print("Columns:", df.columns.tolist())
print("Rows:", len(df))
print("Missing values:", df.isnull().sum())
print("Duplicates:", df.duplicated().sum())
```

### When to Contact Administrator

Contact your admin when:
- Password needs reset
- Need new template uploaded
- Consistent timeout errors
- Access permission issues
- System-wide problems
- Error persists after troubleshooting

**Information to provide**:
1. Exact error message
2. What you were doing
3. Time of occurrence
4. Browser and OS
5. Screenshot
6. Steps to reproduce

### Preventive Measures

1. **Data Preparation**:
   - Clean data before upload
   - Use consistent formatting
   - Test with small batch first

2. **Best Practices**:
   - Save work frequently
   - Download immediately
   - Keep files under 2MB
   - Use Chrome browser

3. **Regular Maintenance**:
   - Clear cache weekly
   - Update browser monthly
   - Check for announcements

### Deployment Sync Issues

#### Application Running Old Code on Streamlit Cloud
**Symptoms**: Git commits successful but changes not reflected on deployed site

**Solutions**:
1. **Force redeployment**:
   - Go to Streamlit Cloud dashboard
   - Click three dots (⋮) → "Reboot app"
   - Wait 2-5 minutes for deployment

2. **Check deployment logs**:
   - Click "Manage app" → "Logs"
   - Look for error messages
   - Verify latest commit hash

3. **Pin dependencies**:
   ```txt
   # requirements.txt
   streamlit==1.31.0
   PyMuPDF==1.23.26  # Critical version
   ```

4. **If still failing**:
   - Delete and recreate the app
   - See [Deployment Recovery Guide](DEPLOYMENT_RECOVERY_GUIDE.md)

#### PyMuPDF Align Parameter Error
**Symptoms**: `TypeError: insert_textbox() got an unexpected keyword argument 'align'`

**Cause**: PyMuPDF version incompatibility

**Solution**:
1. Pin PyMuPDF version in requirements.txt:
   ```txt
   PyMuPDF==1.23.26
   ```
2. Remove align parameter from code if present
3. Force redeploy application

#### Progress Bars Display Raw HTML
**Symptoms**: See `<progress value="50" max="100">` instead of visual progress bar

**Solutions**:
1. Update Streamlit to 1.31.0 or higher
2. Clear browser cache (Ctrl+F5)
3. Use `st.progress()` instead of HTML elements
4. Force application redeployment

### Circular Import Errors

#### Application Won't Start Due to Import Cycle
**Symptoms**: `ImportError: cannot import name 'config' from partially initialized module`

**Cause**: Circular dependency between config.py and utils modules

**Solution**:
1. Implement lazy imports in affected modules
2. Move imports inside functions instead of module level
3. Use import guards:
   ```python
   def get_config():
       from config import config
       return config
   ```

---

**Remember**: Most issues can be resolved by checking data format and following the file requirements. When in doubt, start with a small test file to verify the process works. For deployment issues, see the [Deployment Recovery Guide](DEPLOYMENT_RECOVERY_GUIDE.md).