# Google Sign-In Implementation - ClariFlow Frontend

This document describes the Google Sign-In authentication system implemented in the ClariFlow Next.js frontend using NextAuth.js.

## Overview

The frontend has been upgraded from email/password authentication to Google Sign-In using NextAuth.js, providing:
- Secure OAuth 2.0 authentication with Google
- Automatic session management
- Protected routes and components
- Seamless integration with the FastAPI backend
- Modern, responsive UI matching ClariFlow's branding

## Architecture

### Core Components

1. **NextAuth Configuration** (`src/lib/auth.ts`)
   - Google OAuth provider setup
   - JWT session strategy
   - Custom callbacks for token management

2. **API Route Handler** (`src/app/api/auth/[...nextauth]/route.ts`)
   - NextAuth API endpoints
   - Handles authentication flows

3. **Session Provider** (`src/app/layout.tsx`)
   - Global session management
   - Wraps the entire application

4. **Login Page** (`src/app/login/page.tsx`)
   - Modern Google Sign-In interface
   - Responsive design with ClariFlow branding

5. **Protected Route Component** (`src/components/auth/ProtectedRoute.tsx`)
   - Route protection wrapper
   - Automatic redirects for unauthenticated users

6. **User Menu** (`src/components/auth/UserMenu.tsx`)
   - User profile display
   - Sign out functionality
   - Google profile picture integration

## Features

### ✅ Google OAuth Authentication
- One-click Google Sign-In
- Secure OAuth 2.0 flow
- Automatic token management
- Session persistence

### ✅ Session Management
- JWT-based sessions
- Automatic session validation
- Secure token storage
- Session refresh handling

### ✅ Protected Routes
- Automatic route protection
- Loading states during auth checks
- Redirect to login for unauthenticated users
- Seamless user experience

### ✅ API Integration
- Automatic Google access token inclusion in API requests
- Bearer token authentication with FastAPI backend
- 401 error handling with automatic redirects

### ✅ User Experience
- Modern, responsive design
- Google profile picture display
- Clean user menu interface
- Smooth authentication flows

## Setup Instructions

### 1. Environment Variables

Create or update your `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000

# NextAuth Configuration
NEXTAUTH_SECRET=your-nextauth-secret-key-change-in-production
NEXTAUTH_URL=http://localhost:3000

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 2. Google OAuth Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API
4. Go to "Credentials" and create an OAuth 2.0 Client ID
5. Set the authorized redirect URI to: `http://localhost:3000/api/auth/callback/google`
6. Copy the Client ID and Client Secret to your `.env.local` file

### 3. Generate NextAuth Secret

Generate a secure secret for NextAuth:

```bash
openssl rand -base64 32
```

## Implementation Details

### NextAuth Configuration

```typescript
export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    async jwt({ token, account }) {
      if (account) {
        token.accessToken = account.access_token;
      }
      return token;
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken;
      return session;
    },
  },
  pages: {
    signIn: '/login',
  },
  session: {
    strategy: "jwt",
  },
});
```

### API Integration

```typescript
// Automatic token inclusion in API requests
api.interceptors.request.use(
  async (config) => {
    const session = await getSession();
    if (session?.accessToken) {
      config.headers.Authorization = `Bearer ${session.accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);
```

### Protected Routes

```typescript
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'loading') return;
    if (!session) {
      router.push('/login');
    }
  }, [session, status, router]);

  if (status === 'loading') {
    return <LoadingSpinner />;
  }

  if (!session) {
    return null;
  }

  return <>{children}</>;
};
```

## Usage

### Basic Authentication Flow

```typescript
import { useSession, signIn, signOut } from 'next-auth/react';

const MyComponent = () => {
  const { data: session, status } = useSession();

  if (status === 'loading') return <div>Loading...</div>;
  if (status === 'unauthenticated') return <div>Please sign in</div>;

  return (
    <div>
      <p>Welcome, {session?.user?.name}!</p>
      <button onClick={() => signOut()}>Sign Out</button>
    </div>
  );
};
```

### Protected Components

```typescript
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

const App = () => {
  return (
    <ProtectedRoute>
      <div>Protected content here</div>
    </ProtectedRoute>
  );
};
```

### API Calls

```typescript
import { api } from '@/lib/api';

// Token is automatically included
const response = await api.post('/api/upload', formData);
const chatResponse = await api.post('/api/chat', { query: 'Hello' });
```

## File Structure

```
frontend/src/
├── app/
│   ├── api/auth/
│   │   └── [...nextauth]/
│   │       └── route.ts          # NextAuth API routes
│   ├── login/
│   │   └── page.tsx              # Google Sign-In page
│   └── layout.tsx                # Session provider setup
├── components/auth/
│   ├── ProtectedRoute.tsx        # Route protection wrapper
│   └── UserMenu.tsx              # User menu with Google profile
├── lib/
│   ├── auth.ts                   # NextAuth configuration
│   └── api.ts                    # API client with auth
└── types/
    └── next-auth.d.ts            # TypeScript declarations
```

## Security Considerations

### ✅ Implemented
- OAuth 2.0 secure authentication flow
- JWT session tokens
- HTTPS-only in production
- Secure token storage
- Automatic session validation

### 🔒 Production Recommendations
- Use strong NEXTAUTH_SECRET
- Configure proper CORS settings
- Set up proper Google OAuth redirect URIs
- Use environment-specific configurations
- Implement rate limiting
- Regular security audits

## Migration from JWT Auth

### Removed Components
- `AuthContext.tsx` - Replaced with NextAuth SessionProvider
- `LoginForm.tsx` - Replaced with Google Sign-In
- `RegisterForm.tsx` - No longer needed
- `AuthTest.tsx` - Replaced with NextAuth testing
- Old JWT token management

### Updated Components
- `layout.tsx` - Now uses SessionProvider
- `api.ts` - Uses NextAuth session instead of JWT
- `ProtectedRoute.tsx` - Uses useSession hook
- `UserMenu.tsx` - Displays Google profile info

## Testing

### Local Development
1. Start the development server: `npm run dev`
2. Visit `http://localhost:3000/login`
3. Click "Continue with Google"
4. Complete Google OAuth flow
5. Verify protected routes work
6. Test API calls with authentication

### Manual Testing
1. Check browser dev tools for session cookies
2. Monitor Network tab for Authorization headers
3. Test logout functionality
4. Verify redirects work correctly

## Troubleshooting

### Common Issues

1. **Google OAuth Error**
   - Verify Google Client ID and Secret
   - Check redirect URI configuration
   - Ensure Google+ API is enabled

2. **Session Not Persisting**
   - Check NEXTAUTH_SECRET is set
   - Verify NEXTAUTH_URL configuration
   - Check browser cookie settings

3. **API Calls Failing**
   - Verify access token is being sent
   - Check backend authentication setup
   - Monitor Network tab for 401 errors

4. **Redirect Loops**
   - Check protected route logic
   - Verify login page configuration
   - Ensure session state is correct

### Debug Mode
Enable debug logging by checking browser console for:
- NextAuth session state
- API request/response logs
- Authentication flow messages

## Future Enhancements

- [ ] Multi-provider authentication (GitHub, Microsoft)
- [ ] Role-based access control
- [ ] Session timeout warnings
- [ ] Offline authentication support
- [ ] Two-factor authentication
- [ ] Account linking
- [ ] Social login analytics
- [ ] Custom OAuth providers 