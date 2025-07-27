"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  redirectTo?: string;
  requireEmailVerification?: boolean;
}

export default function ProtectedRoute({ 
  children, 
  fallback,
  redirectTo = '/login',
  requireEmailVerification = false
}: ProtectedRouteProps) {
  const router = useRouter();
  const { isAuthenticated, isLoading, user, initialize, fetchCurrentUser } = useAuthStore();
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    const initAuth = async () => {
      try {
        // Initialize auth state
        await initialize();
        
        // If we have a user, try to fetch current user to verify authentication
        if (isAuthenticated) {
          try {
            await fetchCurrentUser();
          } catch (error) {
            console.error('Failed to fetch current user:', error);
            // If fetch fails, user will be logged out automatically
          }
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
      } finally {
        setIsInitialized(true);
      }
    };

    initAuth();
  }, [initialize, fetchCurrentUser, isAuthenticated]);

  useEffect(() => {
    if (isInitialized && !isLoading) {
      if (!isAuthenticated) {
        router.push(redirectTo);
      } else if (requireEmailVerification && user && !user.is_email_verified) {
        router.push('/verify-email');
      }
    }
  }, [isInitialized, isLoading, isAuthenticated, user, requireEmailVerification, router, redirectTo]);

  // Show loading state while initializing
  if (!isInitialized || isLoading) {
    return fallback || (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  // Show children if authenticated and email verified (if required)
  if (isAuthenticated && (!requireEmailVerification || (user && user.is_email_verified))) {
    return <>{children}</>;
  }

  // Show loading while redirecting
  return fallback || (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600 dark:text-gray-400">Redirecting...</p>
      </div>
    </div>
  );
} 