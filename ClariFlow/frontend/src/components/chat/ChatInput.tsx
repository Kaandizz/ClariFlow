"use client";

import { useState, useRef, useImperativeHandle, forwardRef, useEffect } from 'react';
import { PaperAirplaneIcon } from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';
import FileDropZone from './FileDropZone';
import { type FilePreview } from '@/hooks/useFileUpload';

export interface ChatInputRef {
  focus: () => void;
  setValue: (value: string) => void;
  getValue: () => string;
  clear: () => void;
}

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
  placeholder?: string;
  onFilesUpload?: (files: File[]) => void;
  onFileUpload?: (file: File) => void;
  className?: string;
  filePreviews?: FilePreview[];
  onRemoveFile?: (id: string) => void;
}

const ChatInput = forwardRef<ChatInputRef, ChatInputProps>(({
  onSend,
  isLoading = false,
  placeholder = "Type your message...",
  onFilesUpload,
  onFileUpload,
  className,
  filePreviews = [],
  onRemoveFile,
}, ref) => {
  const [input, setInput] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useImperativeHandle(ref, () => ({
    focus: () => {
      textareaRef.current?.focus();
    },
    setValue: (value: string) => {
      setInput(value);
      adjustTextareaHeight();
    },
    getValue: () => input,
    clear: () => {
      setInput('');
      adjustTextareaHeight();
    },
  }));

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSend(input.trim());
      setInput('');
      adjustTextareaHeight();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      if (e.shiftKey) {
        // Allow new line with Shift+Enter
        return;
      } else {
        // Send message with Enter
        e.preventDefault();
        handleSubmit(e);
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
  };

  return (
    <div className={cn("relative", className)}>
      <form onSubmit={handleSubmit} className="flex flex-col">
        <div
          className={cn(
            "flex items-end gap-2 p-3 sm:p-4 border rounded-lg transition-colors",
            isFocused
              ? "border-blue-500 bg-white dark:bg-gray-800"
              : "border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800",
            "focus-within:border-blue-500 focus-within:bg-white dark:focus-within:bg-gray-800"
          )}
        >
          {/* File Upload Button */}
          <div className="flex-shrink-0">
            <FileDropZone
              onFilesSelect={onFilesUpload || (() => {})}
              onFileSelect={onFileUpload}
              isUploading={isLoading}
              showPreviews={false}
              className="flex items-center"
            />
          </div>

          {/* Text Input */}
          <div className="flex-1 min-w-0">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={handleChange}
              onKeyDown={handleKeyDown}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder={placeholder}
              disabled={isLoading}
              rows={1}
              className={cn(
                "w-full resize-none border-none outline-none bg-transparent",
                "text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400",
                "text-sm sm:text-base leading-relaxed",
                "disabled:cursor-not-allowed disabled:opacity-50",
                "min-h-[1.5rem] max-h-[120px] overflow-y-auto"
              )}
              style={{
                scrollbarWidth: 'thin',
                scrollbarColor: 'rgb(156 163 175) transparent',
              }}
            />
          </div>

          {/* Send Button */}
          <div className="flex-shrink-0">
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className={cn(
                "flex items-center justify-center p-2 sm:p-2.5 rounded-md transition-all",
                "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
                "dark:focus:ring-offset-gray-800",
                "touch-manipulation", // Better touch handling
                input.trim() && !isLoading
                  ? "bg-blue-600 hover:bg-blue-700 text-white shadow-sm hover:shadow-md"
                  : "bg-gray-200 dark:bg-gray-600 text-gray-400 dark:text-gray-500 cursor-not-allowed",
                "disabled:opacity-50 disabled:cursor-not-allowed"
              )}
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
              ) : (
                <PaperAirplaneIcon className="h-4 w-4 sm:h-5 sm:w-5" />
              )}
              <span className="sr-only">Send message</span>
            </button>
          </div>
        </div>

        {/* Mobile Instructions */}
        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 sm:hidden">
          <p>Tap to type • Hold shift + enter for new line</p>
        </div>

        {/* Desktop Instructions */}
        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 hidden sm:block">
          <p>Press Enter to send, Shift+Enter for new line</p>
        </div>
      </form>
    </div>
  );
});

ChatInput.displayName = 'ChatInput';

export default ChatInput; 