# JWT Authentication Implementation - Frontend

This document describes the JWT authentication system implemented in the ClariFlow Next.js frontend.

## Overview

The frontend implements a complete JWT authentication system that:
- Provides a clean login interface
- Stores JWT tokens securely in localStorage
- Automatically includes JWT tokens in API requests
- Handles token refresh and expiration
- Protects routes and components

## Architecture

### Core Components

1. **AuthService** (`src/lib/auth.ts`)
   - Singleton service managing authentication state
   - Handles login, logout, token management
   - Provides JWT validation and refresh logic

2. **AuthContext** (`src/contexts/AuthContext.tsx`)
   - React Context for global auth state
   - Provides auth methods to components
   - Manages loading states and user info

3. **LoginForm** (`src/components/auth/LoginForm.tsx`)
   - Clean, responsive login interface
   - Form validation and error handling
   - Demo credentials display

4. **Axios Interceptors** (`src/lib/auth.ts`)
   - Automatically adds `Authorization: Bearer <token>` headers
   - Handles 401 responses with token refresh
   - Redirects to login on auth failure

## Features

### ✅ Login System
- Email and password authentication
- Form validation with real-time feedback
- Error handling for invalid credentials
- Loading states during authentication

### ✅ JWT Token Management
- Secure token storage in localStorage
- Automatic token validation and expiration checking
- Token refresh mechanism
- Clean token cleanup on logout

### ✅ Protected API Calls
- Automatic JWT inclusion in all API requests
- 401 error handling with automatic refresh
- Seamless integration with existing endpoints

### ✅ User Experience
- Responsive design with Tailwind CSS
- Loading indicators and error messages
- Automatic redirects based on auth state
- Demo credentials for easy testing

## API Integration

### Backend Endpoints Used

1. **Login** (`POST /auth/login`)
   ```json
   {
     "email": "demo@example.com",
     "password": "demopass"
   }
   ```
   Response:
   ```json
   {
     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
     "token_type": "bearer",
     "expires_in": 3600
   }
   ```

2. **Protected Endpoints**
   - All API calls automatically include: `Authorization: Bearer <token>`
   - Upload endpoints: `/api/upload`
   - Chat endpoints: `/api/chat`
   - Other protected routes

### Demo Credentials
- **Email**: `demo@example.com`
- **Password**: `demopass`

## Implementation Details

### Token Storage
```typescript
// Keys used in localStorage
const ACCESS_TOKEN_KEY = 'clariflow_access_token';
const REFRESH_TOKEN_KEY = 'clariflow_refresh_token';
const USER_KEY = 'clariflow_user';
```

### Automatic Token Inclusion
```typescript
// Axios request interceptor
axiosInstance.interceptors.request.use((config) => {
  const token = authService.getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Token Validation
```typescript
isTokenExpired(token: string): boolean {
  try {
    const decoded = jwtDecode(token);
    const currentTime = Date.now() / 1000;
    return decoded.exp ? decoded.exp < currentTime : true;
  } catch {
    return true;
  }
}
```

## Usage

### Basic Login Flow
```typescript
import { useAuth } from '@/contexts/AuthContext';

const { login, isAuthenticated, user } = useAuth();

const handleLogin = async () => {
  const result = await login(email, password);
  if (result.success) {
    // Redirect to main app
    router.push('/');
  } else {
    // Handle error
    setError(result.error);
  }
};
```

### Protected Components
```typescript
import { useAuth } from '@/contexts/AuthContext';

const ProtectedComponent = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return <div>Loading...</div>;
  if (!isAuthenticated) return <div>Please log in</div>;

  return <div>Protected content</div>;
};
```

### API Calls
```typescript
import { api } from '@/lib/api';

// Token is automatically included
const response = await api.post('/api/upload', formData);
const chatResponse = await api.post('/api/chat', { query: 'Hello' });
```

## Testing

### Demo Page
Visit `/demo-auth` to test the authentication system:
- Login with demo credentials
- View authentication status
- Test logout functionality
- See JWT token management in action

### Manual Testing
1. Open browser dev tools
2. Go to Application > Local Storage
3. Check for `clariflow_access_token`
4. Monitor Network tab for Authorization headers

## Security Considerations

### ✅ Implemented
- JWT tokens stored in localStorage (for demo purposes)
- Token expiration validation
- Automatic token refresh
- Secure logout with token cleanup
- HTTPS-only in production

### 🔒 Production Recommendations
- Consider using httpOnly cookies for token storage
- Implement CSRF protection
- Add rate limiting on login attempts
- Use secure session management
- Regular token rotation

## File Structure

```
frontend/src/
├── lib/
│   ├── auth.ts              # Core authentication service
│   └── api.ts               # API client with auth interceptors
├── contexts/
│   └── AuthContext.tsx      # React context for auth state
├── components/auth/
│   ├── LoginForm.tsx        # Login form component
│   ├── AuthTest.tsx         # Test component
│   └── ProtectedRoute.tsx   # Route protection wrapper
└── app/
    ├── login/
    │   └── page.tsx         # Login page
    └── demo-auth/
        └── page.tsx         # Demo page
```

## Configuration

### Environment Variables
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Token Expiration
- Access token: 1 hour (configurable in backend)
- Refresh token: 7 days (configurable in backend)

## Troubleshooting

### Common Issues

1. **Login fails with 401**
   - Verify backend is running on correct port
   - Check demo credentials are correct
   - Ensure backend JWT endpoints are working

2. **API calls fail with 401**
   - Check token is stored in localStorage
   - Verify token hasn't expired
   - Ensure Authorization header is being sent

3. **Token not persisting**
   - Check localStorage is available
   - Verify no browser privacy settings blocking storage
   - Check for JavaScript errors in console

### Debug Mode
Enable debug logging by checking browser console for:
- Token validation messages
- API request/response logs
- Authentication state changes

## Future Enhancements

- [ ] Remember me functionality
- [ ] Multi-factor authentication
- [ ] Social login integration
- [ ] Password reset flow
- [ ] Account management interface
- [ ] Session timeout warnings
- [ ] Offline authentication support 