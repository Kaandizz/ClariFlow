"use client";

import { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import Dashboard from '@/components/layout/Dashboard';
import ChatWithSearch from '@/components/chat/ChatWithSearch';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { type SearchResult } from '@/lib/api';

export default function Home() {
  const [searchResult, setSearchResult] = useState<SearchResult | null>(null);
  const [currentView, setCurrentView] = useState<'dashboard' | 'chat'>('dashboard');

  const handleSearchResultSelect = (result: SearchResult) => {
    setSearchResult(result);
    setCurrentView('chat');
  };

  const handleNavigateFromDashboard = (section: string) => {
    if (section === 'chat') {
      setCurrentView('chat');
    }
    // Add more navigation logic here for other sections
  };

  const handleMainNavigation = (section: string) => {
    if (section === 'dashboard') {
      setCurrentView('dashboard');
    } else if (section === 'chat') {
      setCurrentView('chat');
    }
    // Add more navigation logic here for other sections
  };

  return (
    <ProtectedRoute>
      <MainLayout 
        onSearchResultSelect={handleSearchResultSelect}
        onNavigate={handleMainNavigation}
      >
        {currentView === 'dashboard' ? (
          <Dashboard onNavigate={handleNavigateFromDashboard} />
        ) : (
          <ChatWithSearch onSearchResultSelect={handleSearchResultSelect} />
        )}
      </MainLayout>
    </ProtectedRoute>
  );
}
