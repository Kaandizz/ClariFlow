"use client";

import { useState, useRef } from 'react';
import { type SearchResult } from '@/lib/api';
import Chat, { type ChatRef } from './Chat';
import { type ChatInputRef } from './ChatInput';

interface ChatWithSearchProps {
  onSearchResultSelect?: (result: SearchResult) => void;
}

export default function ChatWithSearch({ onSearchResultSelect }: ChatWithSearchProps) {
  const chatRef = useRef<ChatRef>(null);

  const handleSearchResultSelect = (result: SearchResult) => {
    // Create a context message with the search result
    const contextMessage = `Based on this information from ${result.source_file}${result.page_number ? ` (Page ${result.page_number})` : ''}:\n\n"${result.text}"\n\nPlease help me understand this better.`;
    
    // Set the input value and focus the chat input
    if (chatRef.current) {
      chatRef.current.setInputValue(contextMessage);
      chatRef.current.focusInput();
    }
    
    // Call the parent handler if provided
    onSearchResultSelect?.(result);
  };

  return (
    <div className="h-full">
      <Chat 
        ref={chatRef}
        onSearchResultSelect={handleSearchResultSelect}
      />
    </div>
  );
} 