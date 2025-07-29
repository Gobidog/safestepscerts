# Certificate Generator Project - AI Development Rules

This file contains project-specific rules for AI development on the Certificate Generator app.

## Project Context

Building a Streamlit-based certificate generator with:
- Dual authentication (user/admin)
- PDF certificate generation from spreadsheets
- Google Cloud Run deployment
- Template management system

## Project-Specific Rules

### 1. Multi-Agent Development
This project is being developed using a multi-agent approach with 5 specialized agents:
- Infrastructure Agent
- Auth & Admin Agent
- PDF Generation Agent
- Storage & Integration Agent
- Documentation & Testing Agent

All agents must:
- Update `/tmp/claude-team/progress.md` every 5 minutes
- Document blockers in `/tmp/claude-team/issues.md`
- Communicate via `/tmp/claude-team/handoff.md`
- Work only in their assigned directories

### 2. Streamlit Best Practices
- Use session state for authentication persistence
- Implement proper page routing with pages/ directory
- Handle file uploads with proper validation
- Use st.progress() for user feedback
- Clear temp files after processing

### 3. PDF Generation Rules
- Always use PyMuPDF (fitz) for PDF operations
- Form fields must be named `FirstName` and `LastName`
- Implement auto-sizing for text that exceeds boundaries
- Handle Unicode characters properly
- Save generated PDFs to temp directory first

### 4. Security Requirements
- Never store passwords in code
- Use environment variables for sensitive data
- **JWT_SECRET must be configured** - App won't start without it
- Validate all file uploads (type, size, content)
- Implement rate limiting (40 req/min)
- Sanitize all filenames
- Auto-cleanup temp files after 1 hour

### 5. Google Cloud Integration
- Use Google Cloud Storage for template persistence
- Implement local fallback for development
- Keep container size minimal
- Use structured logging for monitoring
- Handle GCS authentication properly

### 6. Error Handling
- Never let exceptions reach the user
- Provide clear error messages
- Log all errors with context
- Handle missing form fields gracefully
- Validate spreadsheet format before processing

### 7. Testing Requirements
- Test with Unicode names
- Test with 500+ row spreadsheets
- Test rate limiting
- Test template upload/deletion
- Test password changes
- Test dashboard navigation buttons (Templates, Users)
- Test SpreadsheetValidator.validate_file() with various file formats
- Test certificate generation end-to-end workflow
- Verify Docker build works

### 8. Code Organization
```
utils/
├── auth.py         # Authentication only
├── user_store.py   # User data management
├── pdf_generator.py # PDF operations only
├── validators.py   # All validation logic (includes validate_file method)
└── storage.py     # GCS and file operations

pages/
├── 1_login.py     # Authentication page
├── 2_generate.py  # Main generation UI
└── 3_admin.py    # Admin features only
```

**Recent Critical Fixes (2025-07-29):**
- ✅ **JWT_SECRET Configuration Fix** - Application now provides clear, immediate error messages when JWT_SECRET is not configured on Streamlit Cloud
- ✅ **Authentication System FIXED** - All documented logins now work correctly (admin: `Admin@SafeSteps2024`, testuser: `UserPass123`)
- ✅ **Password Reset Utility** - Created comprehensive password reset tool with backup functionality
- ✅ **SpreadsheetValidator.validate_file()** - Added missing method for Streamlit UploadedFile handling
- ✅ **Dashboard Navigation** - Fixed "Go to Templates" and "Go to Users" buttons using session state
- ✅ **Certificate Generation Workflow** - Restored end-to-end functionality with proper validation
- ✅ **Template Upload System FIXED** - Complete overhaul of template management:
  - Admin template page now properly saves uploaded templates
  - Template listing shows actual templates from storage (not hardcoded)
  - Certificate generation uses storage manager for correct template paths
  - Added template validation tool to check PDF compatibility
  - Template preview generation with test data
  - Proper error handling throughout workflow
  - Support for both local and GCS storage
- ✅ **Template Creation Utility** - Added `utils/create_sample_template.py` to generate compatible PDF templates
- ✅ **Comprehensive Testing** - Created `test_template_system.py` for end-to-end verification
- ✅ **Deployment Sync Fix** - Resolved Streamlit Cloud running outdated code:
  - Pinned PyMuPDF==1.23.26 to fix align parameter error
  - Fixed progress bar HTML rendering issues
  - Added deployment verification system
  - Forced cloud redeployment to sync with latest code
- ✅ **Circular Import Resolution** - Fixed import cycle between config.py and utils/auth.py using lazy loading pattern

### 9. Dependencies
Core dependencies (check versions with Context7):
- streamlit >= 1.31.0 (required for proper progress bar rendering)
- PyMuPDF == 1.23.26 (**CRITICAL - DO NOT UPDATE** - newer versions break align parameter)
- pandas >= 2.0.0
- google-cloud-storage >= 2.10.0

**⚠️ IMPORTANT**: Always pin PyMuPDF to version 1.23.26 in requirements.txt. Newer versions remove the align parameter from insert_textbox() causing deployment failures.

### 10. Performance Targets
- Certificate generation: < 0.5 sec each
- Bulk export: < 30 sec for 500 certificates
- Page load: < 2 seconds
- Docker image: < 500MB

## Agent Communication Protocol

### Progress Updates Format:
```markdown
## [Agent Name] [HH:MM]
✓ Completed: [list of completed tasks]
⚡ Current: [current task]
⏳ Remaining: [number] tasks
🚨 Blocked: [blockers or None]
```

### Handoff Format:
```markdown
## [Source Agent] → [Target Agent] [HH:MM]
### Task: [What needs to be done]
- Details: [Specific information]
- Dependencies: [What it depends on]
- Priority: [CRITICAL/HIGH/MEDIUM/LOW]
```

## Deployment Checklist
Before marking deployment ready:
- [ ] All tests pass
- [ ] Docker builds successfully
- [ ] Environment variables documented
- [ ] Rate limiting tested
- [ ] Admin features work
- [ ] Templates upload correctly
- [ ] Certificates generate properly
- [ ] Cleanup jobs run

## Emergency Contacts
- If agents conflict: Check /tmp/claude-team/issues.md
- If builds fail: Verify requirements.txt versions (especially PyMuPDF==1.23.26)
- If GCS fails: Check local fallback works
- If rate limit hit: Implement exponential backoff
- If deployment doesn't sync: See docs/DEPLOYMENT_RECOVERY_GUIDE.md

## Lessons Learned (2025-01-29)

### Deployment Synchronization
- **Problem**: Streamlit Cloud can cache old deployments even after git push
- **Solution**: Force reboot through dashboard or add deployment markers to commits
- **Prevention**: Include version tracking in footer, monitor deployment logs

### Dependency Management
- **Problem**: PyMuPDF updates break backward compatibility silently
- **Solution**: Always pin exact versions for critical dependencies
- **Prevention**: Test dependency updates in staging before production

### Authentication Credentials
- **Cloud vs Local**: Different passwords may be used on cloud deployments
- **Documentation**: Always document both sets of credentials clearly
- **Testing**: Verify logins work after each deployment