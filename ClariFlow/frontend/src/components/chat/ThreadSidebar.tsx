"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  PlusIcon, 
  TrashIcon, 
  PencilIcon,
  ChatBubbleLeftRightIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { useChatStore } from '@/store/chatStore';
import { 
  getChatSessions, 
  createChatSession, 
  deleteChatSession,
  updateSessionTitle 
} from '@/lib/api';
import ChatThreadItem from './ChatThreadItem';

export default function ThreadSidebar() {
  const router = useRouter();
  const {
    sessions,
    activeSessionId,
    isLoadingSessions,
    isCreatingSession,
    isDeletingSession,
    setSessions,
    setActiveSession,
    setLoadingSessions,
    setCreatingSession,
    setDeletingSession,
    addSession,
    removeSession,
    updateSession,
  } = useChatStore();

  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setLoadingSessions(true);
      const sessionsData = await getChatSessions();
      setSessions(sessionsData);
      
      // If no active session and we have sessions, select the first one
      if (!activeSessionId && sessionsData.length > 0) {
        setActiveSession(sessionsData[0].id);
        router.push(`/chat/${sessionsData[0].id}`);
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
      // You could add a toast notification here for better UX
    } finally {
      setLoadingSessions(false);
    }
  };

  const handleCreateNewChat = async () => {
    try {
      setCreatingSession(true);
      const newSession = await createChatSession();
      addSession(newSession);
      setActiveSession(newSession.id);
      
      // Navigate to the new chat
      router.push(`/chat/${newSession.id}`);
      
      // Clear any existing messages when creating a new chat
      // This will be handled by the Chat component when activeSessionId changes
    } catch (error) {
      console.error('Error creating new session:', error);
      // You could add a toast notification here for better UX
    } finally {
      setCreatingSession(false);
    }
  };

  const handleSelectSession = (sessionId: string) => {
    setActiveSession(sessionId);
    router.push(`/chat/${sessionId}`);
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      setDeletingSession(true);
      await deleteChatSession(sessionId);
      removeSession(sessionId);
      
      // If we deleted the active session, select the first available one
      if (activeSessionId === sessionId) {
        const remainingSessions = sessions.filter(s => s.id !== sessionId);
        if (remainingSessions.length > 0) {
          setActiveSession(remainingSessions[0].id);
          router.push(`/chat/${remainingSessions[0].id}`);
        } else {
          setActiveSession(null);
          router.push('/');
        }
      }
    } catch (error) {
      console.error('Error deleting session:', error);
      // You could add a toast notification here for better UX
    } finally {
      setDeletingSession(false);
    }
  };

  const handleStartEdit = (session: any) => {
    setEditingSessionId(session.id);
    setEditTitle(session.title);
  };

  const handleSaveEdit = async () => {
    if (!editingSessionId || !editTitle.trim()) return;

    try {
      const updatedSession = await updateSessionTitle(editingSessionId, {
        title: editTitle.trim()
      });
      updateSession(editingSessionId, updatedSession);
      setEditingSessionId(null);
      setEditTitle('');
    } catch (error) {
      console.error('Error updating session title:', error);
    }
  };

  const handleCancelEdit = () => {
    setEditingSessionId(null);
    setEditTitle('');
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 24) {
      return date.toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } else if (diffInHours < 168) { // 7 days
      return date.toLocaleDateString([], { 
        weekday: 'short' 
      });
    } else {
      return date.toLocaleDateString([], { 
        month: 'short', 
        day: 'numeric' 
      });
    }
  };

  return (
    <div className="flex h-full flex-col bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Chat History
        </h2>
        <button
          onClick={handleCreateNewChat}
          disabled={isCreatingSession}
          className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <PlusIcon className="h-4 w-4" />
          New Chat
        </button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto">
        {isLoadingSessions ? (
          <div className="p-2 space-y-1">
            {[...Array(5)].map((_, index) => (
              <div key={index} className="flex items-center gap-3 p-3 rounded-lg animate-pulse">
                <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        ) : sessions.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-8 text-center">
            <ChatBubbleLeftRightIcon className="h-12 w-12 text-gray-400 mb-4" />
            <p className="text-gray-500 dark:text-gray-400 mb-2">
              No chat history yet
            </p>
            <p className="text-sm text-gray-400 dark:text-gray-500">
              Start a new conversation to see it here
            </p>
          </div>
        ) : (
          <div className="p-2 space-y-1">
            {sessions.map((session) => (
              <ChatThreadItem
                key={session.id}
                session={session}
                isActive={session.id === activeSessionId}
                isEditing={session.id === editingSessionId}
                editTitle={editTitle}
                onSelect={() => handleSelectSession(session.id)}
                onDelete={() => handleDeleteSession(session.id)}
                onStartEdit={() => handleStartEdit(session)}
                onSaveEdit={handleSaveEdit}
                onCancelEdit={handleCancelEdit}
                onEditTitleChange={setEditTitle}
                formatTimestamp={formatTimestamp}
                isDeleting={isDeletingSession}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
} 