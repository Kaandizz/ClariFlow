"use client";

import { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useChatStore } from '@/store/chatStore';
import { getChatSessions } from '@/lib/api';
import MainLayout from '@/components/layout/MainLayout';
import ChatWithSearch from '@/components/chat/ChatWithSearch';
import { type SearchResult } from '@/lib/api';

export default function ChatPage() {
  const params = useParams();
  const router = useRouter();
  const chatId = params.chatId as string;
  
  const {
    sessions,
    activeSessionId,
    setActiveSession,
    setSessions,
    setLoadingSessions,
  } = useChatStore();

  // Load sessions and validate chatId
  useEffect(() => {
    const loadSessionsAndValidate = async () => {
      try {
        setLoadingSessions(true);
        const sessionsData = await getChatSessions();
        setSessions(sessionsData);
        
        // Check if the chatId from URL exists in sessions
        const sessionExists = sessionsData.some(session => session.id === chatId);
        
        if (sessionExists) {
          setActiveSession(chatId);
        } else {
          // If session doesn't exist, redirect to home
          console.warn(`Chat session ${chatId} not found, redirecting to home`);
          router.push('/');
        }
      } catch (error) {
        console.error('Error loading sessions:', error);
        router.push('/');
      } finally {
        setLoadingSessions(false);
      }
    };

    if (chatId) {
      loadSessionsAndValidate();
    }
  }, [chatId, setActiveSession, setSessions, setLoadingSessions, router]);

  const handleSearchResultSelect = (result: SearchResult) => {
    // Handle search result selection if needed
  };

  return (
    <MainLayout onSearchResultSelect={handleSearchResultSelect}>
      <ChatWithSearch onSearchResultSelect={handleSearchResultSelect} />
    </MainLayout>
  );
} 