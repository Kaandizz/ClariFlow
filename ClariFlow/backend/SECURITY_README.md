# ClariFlow Backend Security Implementation

## Overview

This document describes the comprehensive security implementation for the ClariFlow chatbot backend, built with FastAPI. The security layer includes JWT authentication, API key support, rate limiting, request validation, and proper CORS configuration.

## 🔐 Security Features Implemented

### 1. JWT Authentication & Authorization
- **JWT Token Management**: Access and refresh tokens with configurable expiration
- **Password Hashing**: Secure bcrypt password hashing
- **User Management**: User registration, login, and profile management
- **Role-Based Access**: Superuser and regular user roles
- **Token Refresh**: Automatic token refresh mechanism

### 2. API Key Authentication
- **API Key Support**: Alternative authentication for internal tools
- **Key Generation**: Secure API key generation utility
- **Key Validation**: API key verification middleware
- **Optional Authentication**: Support for both JWT and API key auth

### 3. Rate Limiting & Request Validation
- **Rate Limiting**: Per-minute, per-hour, and per-day limits
- **Request Size Validation**: Maximum file upload size (10MB)
- **Content Type Validation**: Allowed content types for requests
- **File Extension Validation**: Whitelist of allowed file types

### 4. Security Headers & CORS
- **Security Headers**: XSS protection, content type options, frame options
- **CORS Configuration**: Proper CORS setup with configurable origins
- **Content Security Policy**: CSP headers for XSS protection
- **HSTS**: HTTP Strict Transport Security (production only)

### 5. File Upload Security
- **File Size Limits**: 10MB maximum file size
- **File Type Validation**: PDF, DOCX, TXT only
- **User Isolation**: Files saved with user ID prefix
- **Temporary File Cleanup**: Automatic cleanup of temporary files

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Security
```bash
python setup_security.py
```

This will:
- Create database tables
- Create admin user (admin@clariflow.com / admin123)
- Generate API keys
- Setup initial security configuration

### 3. Configure Environment
Create/update your `.env` file:

```env
# Security Configuration
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Keys (add the generated keys here)
API_KEYS=["key1","key2","key3"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# CORS Settings
CORS_ORIGINS=["http://localhost:3000","https://yourdomain.com"]
CORS_ALLOW_CREDENTIALS=true

# Environment
ENVIRONMENT=development
```

### 4. Run the Application
```bash
python main.py
```

## 📚 API Endpoints

### Authentication Endpoints

#### POST `/auth/register`
Register a new user
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

#### POST `/auth/login`
Login and get JWT tokens
```json
{
  "username": "user@example.com",
  "password": "securepassword"
}
```

#### POST `/auth/refresh`
Refresh access token
```json
{
  "refresh_token": "your-refresh-token"
}
```

#### GET `/auth/me`
Get current user information (requires JWT)

#### PUT `/auth/me`
Update current user information (requires JWT)

#### POST `/auth/change-password`
Change user password (requires JWT)

### Protected API Endpoints

All API endpoints now require authentication:

#### Chat Endpoints
- `POST /api/chat` - Send chat message (30 req/min)
- `GET /api/sessions` - Get chat sessions (60 req/min)
- `POST /api/sessions` - Create new session (30 req/min)
- `GET /api/sessions/{id}` - Get session messages (60 req/min)
- `PUT /api/sessions/{id}` - Update session (30 req/min)
- `DELETE /api/sessions/{id}` - Delete session (30 req/min)

#### Upload Endpoints
- `POST /api/upload` - Upload multiple files (10 req/min)
- `POST /api/upload/single` - Upload single file (20 req/min)
- `POST /api/upload/api-key` - Upload with API key (5 req/min)
- `GET /api/upload/status` - Get upload status (60 req/min)

## 🔑 Authentication Methods

### 1. JWT Authentication (Recommended)
```bash
# Login to get token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password"

# Use token in requests
curl -X POST "http://localhost:8000/api/chat" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello"}'
```

### 2. API Key Authentication
```bash
# Use API key in header
curl -X POST "http://localhost:8000/api/upload/api-key" \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "files=@document.pdf"
```

## 🛡️ Security Best Practices

### 1. Production Deployment
- Change default admin password immediately
- Use strong, unique secret keys
- Configure proper CORS origins
- Enable HTTPS only
- Set environment to "production"
- Disable API documentation in production

### 2. API Key Management
- Rotate API keys regularly
- Use different keys for different services
- Monitor API key usage
- Revoke compromised keys immediately

### 3. Rate Limiting
- Monitor rate limit violations
- Adjust limits based on usage patterns
- Implement progressive rate limiting for abuse prevention

### 4. File Upload Security
- Validate file contents, not just extensions
- Scan uploaded files for malware
- Implement virus scanning
- Use cloud storage for large files

## 🔧 Configuration Options

### Security Settings
```python
# JWT Configuration
secret_key: str = "your-secret-key"
algorithm: str = "HS256"
access_token_expire_minutes: int = 30
refresh_token_expire_days: int = 7

# Rate Limiting
rate_limit_per_minute: int = 60
rate_limit_per_hour: int = 1000

# File Upload
max_file_size: int = 10 * 1024 * 1024  # 10MB
allowed_extensions: list = [".pdf", ".docx", ".txt"]

# CORS
cors_origins: List[str] = ["*"]
cors_allow_credentials: bool = True
```

## 🚨 Security Headers

The application automatically adds the following security headers:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- `Content-Security-Policy: default-src 'self'; ...`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (production only)

## 📊 Monitoring & Logging

### Security Events Logged
- User registration and login attempts
- Failed authentication attempts
- Rate limit violations
- File upload attempts
- API key usage
- Suspicious requests

### Log Format
```
2024-01-15 10:30:45 - app.core.security - INFO - User logged in successfully: user@example.com
2024-01-15 10:31:00 - app.middleware.security - WARNING - Rate limit exceeded for 192.168.1.100
```

## 🔍 Testing Security

### Test Authentication
```bash
# Test JWT authentication
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@clariflow.com&password=admin123"

# Test protected endpoint
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Rate Limiting
```bash
# Make multiple requests to test rate limiting
for i in {1..70}; do
  curl -X POST "http://localhost:8000/api/chat" \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"query": "test"}'
done
```

### Test File Upload Security
```bash
# Test file size limit
curl -X POST "http://localhost:8000/api/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@large_file.pdf"

# Test file type validation
curl -X POST "http://localhost:8000/api/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@script.js"
```

## 🚀 Deployment Checklist

- [ ] Change default admin password
- [ ] Generate strong secret key
- [ ] Configure API keys
- [ ] Set proper CORS origins
- [ ] Enable HTTPS
- [ ] Set environment to production
- [ ] Configure logging
- [ ] Setup monitoring
- [ ] Test all security features
- [ ] Document incident response procedures

## 📞 Support

For security issues or questions:
1. Check the logs for detailed error messages
2. Verify configuration settings
3. Test authentication flow
4. Review rate limiting settings
5. Check file upload permissions

## 🔄 Updates

This security implementation is designed to be:
- **Extensible**: Easy to add new security features
- **Configurable**: All settings via environment variables
- **Maintainable**: Clean, documented code
- **Compliant**: Follows security best practices
- **Testable**: Comprehensive test coverage

---

**Note**: This is a production-ready security implementation. Always review and customize security settings based on your specific requirements and compliance needs. 