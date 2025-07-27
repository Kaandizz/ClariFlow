"use client";

import { ReactNode, useState, useEffect } from 'react';
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';
import Sidebar from './Sidebar';
import TopBar from './TopBar';
import ThreadSidebar from '../chat/ThreadSidebar';
import { FileUploadProvider } from '@/contexts/FileUploadContext';
import { type SearchResult } from '@/lib/api';
import InsightsChatExtension from '../insights/InsightsChatExtension';
import MeetingSummaryModal from '../tasks/MeetingSummaryModal';
import CompositionPanel from '../composition/CompositionPanel';
import CRMSyncStatus from '../crm/CRMSyncStatus';
import Chat from '../chat/Chat';
import FileUploadProgress from '../ui/FileUploadProgress';

interface MainLayoutProps {
  children: ReactNode;
  onSearchResultSelect?: (result: SearchResult) => void;
  onNavigate?: (section: string) => void;
}

export default function MainLayout({ children }: { children: React.ReactNode }) {
  return (
      <div className="flex h-screen bg-gray-50 dark:bg-gray-900 overflow-hidden">
        <div className="hidden md:flex md:w-64 md:flex-col border-r border-gray-200 dark:border-gray-700">
        <Sidebar />
        </div>
        <div className="flex flex-1 flex-col min-w-0">
          <div className="hidden md:block">
          <TopBar />
        </div>
        <main className="flex-1 overflow-hidden p-2 sm:p-4 relative">
          {children}
        </main>
      </div>
    </div>
  );
} 