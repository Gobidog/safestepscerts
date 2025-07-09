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
- Verify Docker build works

### 8. Code Organization
```
utils/
├── auth.py         # Authentication only
├── pdf_generator.py # PDF operations only
├── validators.py   # All validation logic
└── storage.py     # GCS and file operations

pages/
├── 1_login.py     # Authentication page
├── 2_generate.py  # Main generation UI
└── 3_admin.py    # Admin features only
```

### 9. Dependencies
Core dependencies (check versions with Context7):
- streamlit >= 1.31.0
- PyMuPDF >= 1.23.0
- pandas >= 2.0.0
- google-cloud-storage >= 2.10.0

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
- If builds fail: Verify requirements.txt versions
- If GCS fails: Check local fallback works
- If rate limit hit: Implement exponential backoff