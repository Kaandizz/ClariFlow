# Google OAuth Backend Implementation

## Overview

The ClariFlow FastAPI backend has been upgraded to use Google OAuth authentication instead of traditional email/password authentication. This implementation provides secure, token-based authentication using Google's OAuth 2.0 service.

## Architecture

### Core Components

1. **Google OAuth Authentication Module** (`app/core/google_auth.py`)
   - `GoogleAuthManager`: Handles Google token verification
   - `GoogleUserInfo`: Pydantic model for user information
   - `get_current_user_from_google_token()`: FastAPI dependency for protected routes

2. **Updated API Endpoints**
   - All protected endpoints now use Google OAuth authentication
   - Removed old JWT-based authentication endpoints
   - Added Google OAuth verification endpoints

3. **Environment Configuration**
   - Google OAuth credentials management
   - Secure token verification

## Setup Instructions

### 1. Install Dependencies

The required Google OAuth dependencies have been added to `requirements.txt`:

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2
```

### 2. Configure Environment Variables

Update your `.env` file with Google OAuth credentials:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
```

### 3. Get Google OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Configure the OAuth consent screen
6. Add authorized redirect URIs for your frontend
7. Copy the Client ID and Client Secret to your `.env` file

## Implementation Details

### Google OAuth Authentication Flow

1. **Frontend Authentication**: User signs in with Google via NextAuth.js
2. **Token Extraction**: Frontend extracts Google access token from session
3. **API Requests**: Frontend includes token in Authorization header
4. **Backend Verification**: Backend verifies token with Google's servers
5. **User Information**: Backend extracts user info (email, name, picture) from verified token

### Token Verification Process

```python
async def verify_google_token(self, token: str) -> GoogleUserInfo:
    # Verify token with Google's servers
    idinfo = id_token.verify_oauth2_token(
        token, 
        requests.Request(), 
        self.google_client_id
    )
    
    # Extract user information
    return GoogleUserInfo(
        email=idinfo.get('email', ''),
        name=idinfo.get('name', ''),
        picture=idinfo.get('picture'),
        sub=idinfo.get('sub', ''),
        email_verified=idinfo.get('email_verified', False)
    )
```

### Protected Route Implementation

All protected endpoints now use the Google OAuth dependency:

```python
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: GoogleUserInfo = Depends(get_current_user_from_google_token)
):
    # Endpoint logic here
    pass
```

## API Endpoints

### Authentication Endpoints

- `GET /auth/me` - Get current user information
- `GET /auth/verify` - Verify Google OAuth token
- `GET /auth/protected` - Protected route example

### Protected API Endpoints

All the following endpoints now require Google OAuth authentication:

- **Chat API** (`/api/chat/*`)
  - `POST /api/chat` - Send chat messages
  - `GET /api/sessions` - Get chat sessions
  - `GET /api/sessions/{session_id}` - Get session messages
  - `POST /api/sessions` - Create new session
  - `PUT /api/sessions/{session_id}` - Update session
  - `DELETE /api/sessions/{session_id}` - Delete session
  - `GET /api/documents` - Get available documents

- **Upload API** (`/api/upload/*`)
  - `POST /api/upload` - Upload multiple files
  - `POST /api/upload/single` - Upload single file
  - `GET /api/upload/status` - Get upload status

- **Other Protected APIs**
  - Search API
  - Leads API
  - Insights API
  - Tasks API
  - Composition API
  - CRM API

## Security Features

### Token Validation

- **Google Verification**: All tokens are verified with Google's servers
- **Automatic Expiration**: Google handles token expiration
- **Secure Headers**: Proper WWW-Authenticate headers for failed auth

### Error Handling

- **Missing Token**: 401 with "Missing Authorization header"
- **Invalid Token**: 401 with "Invalid Google token"
- **Expired Token**: 401 with "Invalid Google token"
- **Configuration Error**: 500 with "Google OAuth not configured"

### Logging

- **Successful Auth**: Logs user email and action
- **Failed Auth**: Logs error details for debugging
- **Token Verification**: Logs verification attempts and results

## Migration from JWT Authentication

### Removed Components

- JWT token generation and validation
- User registration and login endpoints
- Password-based authentication
- JWT refresh token system
- User database models (optional)

### Updated Components

- All API endpoints now use `get_current_user_from_google_token()`
- User identification uses Google email instead of database ID
- File uploads use email-based naming for better identification

### Benefits

- **Enhanced Security**: Google handles password security
- **Simplified Auth**: No need to manage user passwords
- **Better UX**: Seamless Google Sign-In experience
- **Reduced Complexity**: No JWT token management needed

## Testing

### Manual Testing

1. **Start the backend server**:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. **Test authentication**:
   ```bash
   # This will fail without a valid Google token
   curl -H "Authorization: Bearer invalid-token" http://localhost:8000/auth/me
   ```

3. **Test with frontend**: Use the frontend Google Sign-In to get valid tokens

### Integration Testing

The backend is designed to work seamlessly with the NextAuth.js frontend implementation. The frontend automatically includes Google access tokens in API requests.

## Troubleshooting

### Common Issues

1. **"Google OAuth not configured"**
   - Ensure `GOOGLE_CLIENT_ID` is set in `.env`
   - Verify Google Cloud Console configuration

2. **"Invalid Google token"**
   - Check if token is expired
   - Verify token format (should be Google access token)
   - Ensure Google+ API is enabled

3. **CORS Issues**
   - Verify frontend domain is in Google OAuth authorized origins
   - Check backend CORS configuration

### Debug Logging

Enable debug logging by setting `LOG_LEVEL=DEBUG` in your `.env` file to see detailed authentication logs.

## Security Considerations

1. **Token Storage**: Never store Google tokens in database
2. **HTTPS**: Always use HTTPS in production
3. **Client ID**: Keep Google Client ID secure but it can be public
4. **Token Validation**: Always verify tokens with Google servers
5. **Error Messages**: Don't expose sensitive information in error responses

## Future Enhancements

1. **User Database Integration**: Optionally store verified user info in database
2. **Role-Based Access**: Implement role-based permissions using Google user info
3. **Token Caching**: Cache verified user info for performance
4. **Multi-Provider Support**: Add support for other OAuth providers

## Support

For issues or questions about the Google OAuth implementation:

1. Check the logs for detailed error messages
2. Verify Google Cloud Console configuration
3. Test with the frontend integration
4. Review this documentation for setup instructions 