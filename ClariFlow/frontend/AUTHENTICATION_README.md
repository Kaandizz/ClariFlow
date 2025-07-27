# 🔐 ClariFlow Frontend Authentication System

This document outlines the comprehensive authentication system implemented for the ClariFlow frontend, built with Next.js 14+ and TypeScript.

## 🏗️ Architecture Overview

The authentication system is built with a modular, secure approach using:

- **JWT Tokens**: Secure token-based authentication with refresh mechanism
- **Zustand Store**: Global state management for authentication
- **Protected Routes**: Route-level authentication guards
- **Axios Interceptors**: Automatic token management for API requests
- **Local Storage**: Secure token persistence

## 📁 File Structure

```
src/
├── lib/
│   └── auth.ts                 # Core authentication logic
├── store/
│   └── authStore.ts           # Zustand authentication store
├── components/
│   └── auth/
│       ├── AuthProvider.tsx   # Authentication context provider
│       ├── LoginForm.tsx      # Login form component
│       ├── RegisterForm.tsx   # Registration form component
│       └── ProtectedRoute.tsx # Route protection component
└── app/
    ├── layout.tsx             # Root layout with auth provider
    ├── page.tsx              # Protected main page
    └── login/
        └── page.tsx          # Login/register page
```

## 🔧 Core Components

### 1. Authentication Service (`lib/auth.ts`)

**Features:**
- JWT token management (access & refresh tokens)
- Token validation and expiration checking
- Axios interceptors for automatic token handling
- User data persistence
- API authentication functions

**Key Functions:**
```typescript
// Token Management
getToken(): string | null
setToken(token: string): void
removeToken(): void
isTokenValid(token: string): boolean

// Authentication
login(credentials: LoginRequest): Promise<LoginResponse>
register(userData: RegisterRequest): Promise<LoginResponse>
logout(): void
refreshToken(): Promise<{ access_token: string; refresh_token: string }>

// User Management
getCurrentUser(): Promise<User>
updateProfile(updates: Partial<User>): Promise<User>
changePassword(currentPassword: string, newPassword: string): Promise<{ message: string }>
```

### 2. Authentication Store (`store/authStore.ts`)

**Features:**
- Global authentication state management
- Loading and error state handling
- Automatic token refresh
- Persistent state with localStorage

**State Interface:**
```typescript
interface AuthStore {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login(credentials: LoginRequest): Promise<void>;
  register(userData: RegisterRequest): Promise<void>;
  logout(): void;
  fetchCurrentUser(): Promise<void>;
  updateUserProfile(updates: Partial<User>): Promise<void>;
  changeUserPassword(currentPassword: string, newPassword: string): Promise<void>;
}
```

### 3. Authentication Components

#### LoginForm Component
- Email/password validation
- Error handling and display
- Loading states
- Demo account login
- Password visibility toggle

#### RegisterForm Component
- Email/password/confirm password validation
- Password strength requirements
- Form validation with real-time feedback
- Password visibility toggles

#### ProtectedRoute Component
- Route-level authentication guards
- Automatic redirect to login
- Loading states during authentication checks
- Token validation on route access

#### AuthProvider Component
- Initializes authentication state on app load
- Provides authentication context to the app

## 🚀 Usage Examples

### 1. Protecting Routes

```typescript
import ProtectedRoute from '@/components/auth/ProtectedRoute';

export default function MyPage() {
  return (
    <ProtectedRoute>
      <div>This content is only visible to authenticated users</div>
    </ProtectedRoute>
  );
}
```

### 2. Using Authentication in Components

```typescript
import { useAuthStore } from '@/store/authStore';

export default function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuthStore();

  const handleLogin = async () => {
    try {
      await login({ email: 'user@example.com', password: 'password' });
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <div>
      {isAuthenticated ? (
        <div>
          <p>Welcome, {user?.email}!</p>
          <button onClick={logout}>Logout</button>
        </div>
      ) : (
        <button onClick={handleLogin}>Login</button>
      )}
    </div>
  );
}
```

### 3. Making Authenticated API Calls

```typescript
import { api } from '@/lib/api';

// The api instance automatically includes the auth token
const response = await api.get('/api/protected-endpoint');
```

## 🔒 Security Features

### 1. Token Management
- **Access Tokens**: Short-lived tokens for API requests
- **Refresh Tokens**: Long-lived tokens for token renewal
- **Automatic Refresh**: Transparent token refresh on 401 responses
- **Token Validation**: JWT expiration checking

### 2. Route Protection
- **Client-side Guards**: ProtectedRoute component
- **Automatic Redirects**: Unauthenticated users redirected to login
- **Loading States**: Smooth UX during authentication checks

### 3. Form Security
- **Input Validation**: Client-side validation with real-time feedback
- **Password Requirements**: Strong password enforcement
- **Error Handling**: Comprehensive error display and handling

### 4. API Security
- **Automatic Headers**: Auth tokens automatically included in requests
- **Error Interception**: 401 responses trigger automatic logout
- **Request Retry**: Failed requests retried with fresh tokens

## 🎨 UI/UX Features

### 1. Modern Design
- Clean, responsive design with Tailwind CSS
- Dark mode support
- Loading animations and transitions
- Error states with clear messaging

### 2. User Experience
- Smooth authentication flow
- Persistent login state
- Automatic redirects
- Loading indicators
- Form validation feedback

### 3. Accessibility
- Proper ARIA labels
- Keyboard navigation support
- Screen reader compatibility
- Focus management

## 🔧 Configuration

### Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Dependencies

```json
{
  "dependencies": {
    "axios": "^1.10.0",
    "jwt-decode": "^4.0.0",
    "zustand": "^5.0.5",
    "@heroicons/react": "^2.2.0"
  }
}
```

## 🧪 Testing

### Manual Testing Checklist

1. **Login Flow**
   - [ ] Valid credentials work
   - [ ] Invalid credentials show error
   - [ ] Demo account login works
   - [ ] Form validation works

2. **Registration Flow**
   - [ ] Valid registration works
   - [ ] Password validation works
   - [ ] Email validation works
   - [ ] Password confirmation works

3. **Route Protection**
   - [ ] Unauthenticated users redirected to login
   - [ ] Authenticated users can access protected routes
   - [ ] Loading states display correctly

4. **Token Management**
   - [ ] Tokens persist across page reloads
   - [ ] Token refresh works automatically
   - [ ] Logout clears all tokens

5. **API Integration**
   - [ ] Authenticated API calls work
   - [ ] 401 responses trigger logout
   - [ ] Token refresh retries failed requests

## 🚀 Deployment Considerations

### 1. Production Security
- Use HTTPS in production
- Set secure cookie flags
- Implement CSRF protection
- Configure proper CORS settings

### 2. Environment Configuration
- Set production API URLs
- Configure proper error handling
- Set up monitoring and logging

### 3. Performance
- Token validation is optimized
- Minimal re-renders with Zustand
- Efficient localStorage usage

## 🔄 Integration with Backend

The frontend authentication system is designed to work seamlessly with the ClariFlow backend authentication endpoints:

- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/refresh` - Token refresh
- `GET /auth/me` - Get current user
- `PUT /auth/me` - Update user profile
- `POST /auth/change-password` - Change password

## 📝 Future Enhancements

### Planned Features
- [ ] Remember me functionality
- [ ] Multi-factor authentication
- [ ] Social login integration
- [ ] Password reset flow
- [ ] Account deletion
- [ ] Session management
- [ ] Audit logging

### Security Improvements
- [ ] HttpOnly cookies for token storage
- [ ] CSRF token implementation
- [ ] Rate limiting on auth endpoints
- [ ] Account lockout after failed attempts

## 🐛 Troubleshooting

### Common Issues

1. **Token Not Persisting**
   - Check localStorage permissions
   - Verify token storage functions

2. **API Calls Failing**
   - Check token validity
   - Verify API URL configuration
   - Check CORS settings

3. **Redirect Loops**
   - Check authentication state initialization
   - Verify route protection logic

4. **Form Validation Issues**
   - Check validation functions
   - Verify error state management

### Debug Mode

Enable debug logging by adding to browser console:
```javascript
localStorage.setItem('debug', 'auth:*');
```

## 📚 Additional Resources

- [Next.js Authentication](https://nextjs.org/docs/authentication)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [JWT.io](https://jwt.io/)
- [Axios Interceptors](https://axios-http.com/docs/interceptors)

---

This authentication system provides a robust, secure, and user-friendly foundation for the ClariFlow application. It follows modern best practices and is designed to scale with the application's growth. 