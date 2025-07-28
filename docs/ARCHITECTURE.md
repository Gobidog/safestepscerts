# SafeSteps Certificate Generator - Architecture Documentation

## System Overview

SafeSteps Certificate Generator is a Streamlit-based web application designed for bulk PDF certificate generation with comprehensive user authentication and management capabilities.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Browser                           │
│                   (Streamlit Frontend)                       │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTPS
┌───────────────────────┴─────────────────────────────────────┐
│                    Streamlit Server                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                  Application Layer                   │    │
│  │  ┌──────────┐  ┌──────────┐  ┌────────────────┐   │    │
│  │  │  Login   │  │Certificate│  │     Admin      │   │    │
│  │  │  Page    │  │Generation │  │   Dashboard    │   │    │
│  │  └─────┬────┘  └─────┬────┘  └────────┬───────┘   │    │
│  │        │             │                 │            │    │
│  │  ┌─────┴─────────────┴─────────────────┴────────┐  │    │
│  │  │            Session Management                 │  │    │
│  │  │         (JWT-based with CSRF)                │  │    │
│  │  └───────────────────┬───────────────────────────┘  │    │
│  └────────────────────────┬─────────────────────────────┘    │
│                          │                                   │
│  ┌──────────────────────┴────────────────────────────────┐  │
│  │                   Service Layer                        │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────┐ │  │
│  │  │    Auth    │  │    PDF     │  │     User       │ │  │
│  │  │  Service   │  │ Generator  │  │  Management    │ │  │
│  │  └──────┬─────┘  └─────┬──────┘  └───────┬────────┘ │  │
│  │         │              │                  │           │  │
│  │  ┌──────┴──────────────┴──────────────────┴────────┐ │  │
│  │  │              Data Access Layer                   │ │  │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │ │  │
│  │  │  │   User   │  │ Template │  │   Session    │  │ │  │
│  │  │  │  Store   │  │  Storage │  │   Storage    │  │ │  │
│  │  │  └────┬─────┘  └─────┬────┘  └──────┬───────┘  │ │  │
│  │  └───────┼──────────────┼───────────────┼──────────┘ │  │
│  └──────────┼──────────────┼───────────────┼────────────┘  │
└─────────────┼──────────────┼───────────────┼────────────────┘
              │              │               │
┌─────────────┴──────┐ ┌─────┴───────┐ ┌────┴──────────────┐
│   Local Storage    │ │Google Cloud │ │   In-Memory       │
│ • users.json       │ │  Storage    │ │ • Sessions        │
│ • temp files       │ │ • Templates │ │ • Rate limits     │
│ • logs             │ │ • PDFs      │ │ • Failed logins   │
└────────────────────┘ └─────────────┘ └───────────────────┘
```

## Core Components

### 1. Frontend Layer (Streamlit)

**Login Page** (`app.py`)
- Username/email and password input form
- Session initialization on successful authentication
- Error handling and user feedback
- Help documentation access

**Certificate Generation** (`pages/2_generate.py`)
- CSV/XLSX file upload interface
- Template selection dropdown
- Preview functionality
- Bulk generation with progress tracking
- ZIP download of generated certificates

**Admin Dashboard** (`pages/3_admin.py`)
- User management interface
- Template upload and management
- System statistics and monitoring
- Password reset functionality

### 2. Authentication & Session Management

**Authentication Service** (`utils/auth.py`)
- `login_with_credentials()`: Username/email + password authentication
- `create_session()`: JWT-based session creation
- `validate_session()`: Session validation and timeout management
- Password hashing using bcrypt
- Rate limiting for failed login attempts

**User Store** (`utils/user_store.py`)
- JSON-based user persistence with file locking
- Thread-safe operations for concurrent access
- User CRUD operations
- Password hash storage and verification
- Unique constraint enforcement (username, email)

**Session Features**
- JWT tokens for stateless session management
- 30-minute timeout with activity tracking
- CSRF protection using JWT tokens
- Secure session storage in Streamlit state

### 3. PDF Generation Engine

**PDF Generator** (`utils/pdf_generator.py`)
- PyMuPDF (fitz) for PDF manipulation
- **Robust constructor with required template_path parameter** ✅ **FIXED**
- **Template path validation and error handling** ✅ **ADDED**
- Form field population and flattening
- Multi-threaded parallel processing
- Auto-sizing text to fit fields
- Support for various PDF form types
- **Session state integration for template path extraction** ✅ **IMPROVED**

**Processing Pipeline**
1. **Validate template path from session state** ✅ **NEW**
2. **Initialize PDFGenerator with template_path** ✅ **FIXED**
3. Load template PDF
4. Extract form fields
5. Populate with spreadsheet data
6. Flatten form (remove blue backgrounds)
7. Save to temporary storage
8. Package into ZIP for download

### 4. Storage Layer

**Local Storage**
- User data: `data/storage/users.json`
- Temporary files: `temp/` directory
- Local template cache: `templates/`
- Auto-cleanup of files older than 2 hours

**Google Cloud Storage** (Optional)
- Template persistence across deployments
- Scalable PDF storage
- Configurable via environment variables
- Fallback to local storage if unavailable

**Storage Abstraction** (`utils/storage.py`)
- Unified interface for local/cloud storage
- Automatic fallback mechanism
- **Template metadata robustness with graceful fallback** ✅ **IMPROVED**
- Template caching for performance
- Thread-safe file operations
- **Handles incomplete template metadata without crashes** ✅ **FIXED**

### 5. Security Components

**Environment Security** ✅ **ENHANCED**
- **Standardized environment loading across all contexts**
- **Graceful fallback when dotenv unavailable**
- **JWT_SECRET consistency validation**
- **Error handling prevents environment-related crashes**

**Password Security**
- Bcrypt hashing with salt rounds
- Password strength validation
- No plaintext storage
- Admin-controlled resets

**Access Control**
- Role-based permissions (user/admin)
- Protected admin functions
- Last admin protection
- Account activation/deactivation

**Rate Limiting**
- Per-username login attempt tracking
- Configurable limits via environment
- Automatic lockout on threshold
- Time-based reset

**Data Protection**
- File locking for concurrent access
- Input validation and sanitization
- Path traversal prevention
- Content-type validation

## Data Flow

### Authentication Flow
```
1. User enters credentials
2. System validates username/email exists
3. Password hash comparison
4. Rate limit check
5. Create JWT session
6. Store session in Streamlit state
7. Redirect to appropriate page
```

### Certificate Generation Flow
```
1. User uploads spreadsheet
2. System validates file format
3. User selects template
4. System loads template from storage
5. Preview generated (first row)
6. User confirms generation
7. Parallel processing of all rows
8. Package certificates into ZIP
9. Provide download link
10. Cleanup temporary files
```

### User Management Flow
```
1. Admin accesses user management
2. System loads current user list
3. Admin performs action (create/edit/delete)
4. System validates permissions
5. Update user store with locking
6. Log action for audit
7. Refresh UI with changes
```

## Security Architecture

### Defense in Depth
1. **Network Layer**: HTTPS enforcement (Cloud Run)
2. **Application Layer**: Authentication and authorization
3. **Session Layer**: JWT tokens with expiration
4. **Data Layer**: Encryption at rest, hashed passwords
5. **Audit Layer**: Comprehensive logging

### Security Controls
- Environment variable validation on startup
- Mandatory JWT_SECRET for production
- CSRF protection on state-changing operations
- Input validation on all user inputs
- File type and content validation
- Rate limiting on sensitive operations

## Scalability Considerations

### Current Limitations
- Single-instance Streamlit (no horizontal scaling)
- File-based user storage (not distributed)
- In-memory session storage
- Local file processing

### Scaling Strategies
1. **Session Storage**: Move to Redis/Memorystore
2. **User Database**: Migrate to Cloud SQL/Firestore
3. **File Processing**: Use Cloud Functions for PDF generation
4. **Load Balancing**: Cloud Run with multiple instances
5. **Caching**: CDN for static assets and templates

## Deployment Architecture

### Development
```
Local Machine
├── Streamlit Development Server
├── Local File Storage
└── Environment Variables (.env)
```

### Production (Cloud Run)
```
Google Cloud Project
├── Cloud Run Service
│   ├── Container Instance(s)
│   ├── Environment Variables
│   └── Service Account
├── Cloud Storage Bucket
│   ├── Templates
│   └── Generated PDFs
└── Cloud Logging
    ├── Application Logs
    └── Audit Logs
```

## Monitoring and Observability

### Metrics
- Active sessions count
- Login success/failure rates
- Certificate generation performance
- Template usage statistics
- Storage utilization

### Logging
- Authentication events
- User management actions
- Certificate generation requests
- Error conditions
- Performance metrics

### Health Checks
- Application startup validation
- Storage connectivity
- Session store availability
- Rate limit functionality

## Disaster Recovery

### Backup Strategy
- Daily backup of user data
- Template versioning in GCS
- Session state is ephemeral (no backup needed)
- Configuration in version control

### Recovery Procedures
1. **User Data Loss**: Restore from backup JSON
2. **Template Loss**: Re-upload from local copies
3. **Session Loss**: Users must re-authenticate
4. **Complete Failure**: Redeploy from container image

## Future Architecture Improvements

### Phase 1: Enhanced Security
- Two-factor authentication
- OAuth integration
- Advanced audit logging
- Security event monitoring

### Phase 2: Scalability
- Distributed session storage
- Database for user management
- Horizontal scaling support
- Caching layer

### Phase 3: Features
- API endpoints for automation
- Bulk user import/export
- Template versioning
- Advanced analytics

## Technology Stack Summary

- **Framework**: Streamlit 1.31.0+
- **Language**: Python 3.10+
- **PDF Library**: PyMuPDF (fitz)
- **Authentication**: JWT + bcrypt
- **Storage**: Local filesystem / Google Cloud Storage
- **Deployment**: Docker / Cloud Run
- **Monitoring**: Cloud Logging / Custom metrics