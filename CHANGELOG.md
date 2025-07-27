# Changelog

All notable changes to the Certificate Generator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-01-27

### 🔒 Security Improvements

#### Critical Fixes
- **Session Persistence**: JWT_SECRET is now loaded from environment variables to ensure sessions persist across application restarts
- **Password Security**: User and admin passwords are now required environment variables, preventing deployment with default credentials
- **CSRF Protection**: Added CSRF token generation and validation using persistent JWT secrets
- **Configuration Validation**: Application now fails to start if critical security settings are missing

#### Implementation Details
- Modified `utils/auth.py` to use `os.getenv("JWT_SECRET")` with fallback warning
- Added password requirement validation in `config.py` AuthConfig
- Implemented proper JWT-based CSRF token generation with session validation
- Added security warnings when JWT_SECRET is not set in environment

### 📚 Documentation Updates

#### New Files
- `.env.production.example` - Production-ready environment template with secure defaults
- `docs/DEPLOYMENT_SECURITY_GUIDE.md` - Comprehensive security guide for production deployment
- `tests/test_security_fixes.py` - Test suite for security improvements

#### Updated Files
- `README.md` - Added critical JWT_SECRET requirement warning
- `.env.example` - Enhanced with JWT_SECRET configuration and generation instructions

### 🧪 Testing
- Added comprehensive test suite for security fixes
- Tests verify JWT_SECRET persistence
- Tests validate password requirements
- Tests confirm CSRF protection functionality

### ⚙️ Configuration Changes

#### Environment Variables
- `JWT_SECRET` - Now required for session persistence (minimum 32 characters)
- `USER_PASSWORD` - Required, no default value allowed
- `ADMIN_PASSWORD` - Required, no default value allowed

#### Security Requirements
- Passwords must be 8+ characters with uppercase, lowercase, and numbers
- JWT_SECRET must be explicitly set (not auto-generated) for production
- CSRF protection enabled by default for production environments

### 🚨 Breaking Changes
- Application will not start without USER_PASSWORD and ADMIN_PASSWORD environment variables
- Sessions will be lost on restart if JWT_SECRET is not set in environment

### 🔧 Technical Details
- JWT tokens use HS256 algorithm for CSRF protection
- Session validation includes session_id and username verification
- Warning logs generated when JWT_SECRET is auto-generated (not from env)

## [1.0.0] - Previous Release

### Features
- Certificate generation from templates
- Bulk processing from CSV/XLSX files
- User and admin authentication
- Template management system
- Google Cloud Storage integration
- Rate limiting implementation