"use client";

import { useState, useRef, useEffect, forwardRef, useImperativeHandle } from 'react';
import { QuestionMarkCircleIcon, DocumentTextIcon, SparklesIcon, UserIcon, MicrophoneIcon, StopIcon } from '@heroicons/react/24/outline';
import type { ChatMessage, ChatRequest, SearchResult, ChatMessageResponse } from '@/lib/api';
import { sendChatMessage, getSessionMessages, createChatSession, getChatSessions } from '@/lib/api';
import { useChatStore, convertMessageResponse } from '@/store/chatStore';
import ChatInput, { type ChatInputRef } from './ChatInput';
import DragAndDropWrapper from './DragAndDropWrapper';
import DragAndDropDemo from './DragAndDropDemo';
import Toast, { ToastType } from '../ui/Toast';
import { useFileUpload } from '@/hooks/useFileUpload';
import { useFileUploadContext } from '@/contexts/FileUploadContext';
import FilePreview from './FilePreview';
import DragHint from './DragHint';

interface ToastState {
  message: string;
  type: ToastType;
}

interface ChatProps {
  onSearchResultSelect?: (result: SearchResult) => void;
  chatInputRef?: React.RefObject<ChatInputRef>;
}

export interface ChatRef {
  focusInput: () => void;
  setInputValue: (value: string) => void;
}

const Chat = forwardRef<ChatRef, ChatProps>(({ onSearchResultSelect, chatInputRef: externalChatInputRef }, ref) => {
  const [toast, setToast] = useState<ToastState | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recognition, setRecognition] = useState<any>(null);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const { 
    isUploading, 
    uploadFiles, 
    uploadFile, 
    error, 
    filePreviews, 
    addFilePreviews, 
    removeFilePreview 
  } = useFileUpload();
  const { showDemo, setShowDemo, currentDocumentId, setCurrentDocumentId } = useFileUploadContext();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const internalChatInputRef = useRef<ChatInputRef>(null);
  
  // Chat store
  const {
    messages,
    activeSessionId,
    isLoadingMessages,
    setMessages,
    addMessage,
    setLoadingMessages,
  } = useChatStore();
  
  // Use external ref if provided, otherwise use internal ref
  const chatInputRef = externalChatInputRef || internalChatInputRef;

  // Expose methods to parent component
  useImperativeHandle(ref, () => ({
    focusInput: () => {
      chatInputRef.current?.focus();
    },
    setInputValue: (value: string) => {
      chatInputRef.current?.setValue(value);
    }
  }));

  // Auto-scroll to bottom when new messages are added
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Load messages when active session changes
  useEffect(() => {
    if (activeSessionId) {
      loadSessionMessages(activeSessionId);
    } else {
      setMessages([]);
    }
  }, [activeSessionId]);

  const loadSessionMessages = async (sessionId: string) => {
    try {
      setLoadingMessages(true);
      const sessionMessages = await getSessionMessages(sessionId);
      const convertedMessages = sessionMessages.map(convertMessageResponse);
      setMessages(convertedMessages);
    } catch (error) {
      console.error('Error loading session messages:', error);
      setToast({
        message: 'Failed to load chat history. Please try again.',
        type: 'error',
      });
    } finally {
      setLoadingMessages(false);
    }
  };

  // Convert messages to history format for API
  const getMessageHistory = (): string[] => {
    // Get last 5 conversation turns (10 messages max)
    const recentMessages = messages.slice(-10);
    return recentMessages.map(msg => msg.content);
  };

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
      document_id: currentDocumentId || undefined,
    };

    addMessage(userMessage);
    setIsLoading(true);

    try {
      // Prepare chat request with session_id and history
      const chatRequest: ChatRequest = {
        query: content,
        session_id: activeSessionId || undefined,
        history: getMessageHistory(),
      };

      // Send to backend
      const response = await sendChatMessage(chatRequest);

      // Add assistant response with enhanced metadata
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
        document_id: response.document_id || undefined,
        source: response.source,
      };

      addMessage(assistantMessage);

    } catch (error) {
      console.error('Error sending chat message:', error);
      
      // Add error message
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your request. Please try again.',
        timestamp: new Date().toISOString(),
        source: 'openai',
      };

      addMessage(errorMessage);

      setToast({
        message: 'Failed to send message. Please try again.',
        type: 'error',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilesUpload = async (files: File[]) => {
    console.log('handleFilesUpload called with files:', files.map(f => f.name));
    
    // Add file previews
    addFilePreviews(files);
    
    // Add a user message showing the files being uploaded
    const fileNames = files.map(f => f.name).join(', ');
    const userMessage: ChatMessage = {
      role: 'user',
      content: `📎 Uploading ${files.length} file(s): ${fileNames}`,
      timestamp: new Date().toISOString(),
    };
    
    addMessage(userMessage);
    
    console.log('Calling uploadFiles from hook...');
    const response = await uploadFiles(files);
    console.log('Upload response:', response);
    
    if (response) {
      const successfulFiles = response.results.filter(r => r.status === 'success');
      const failedFiles = response.results.filter(r => r.status === 'error');
      
      // Store the first successful document ID (for backward compatibility)
      const firstSuccess = successfulFiles[0];
      if (firstSuccess?.document_id) {
        setCurrentDocumentId(firstSuccess.document_id);
      }
      
      // Create summary message
      let summaryMessage = '';
      if (successfulFiles.length > 0) {
        summaryMessage += `✅ Successfully uploaded ${successfulFiles.length} file(s): ${successfulFiles.map(r => r.filename).join(', ')}. `;
      }
      if (failedFiles.length > 0) {
        summaryMessage += `❌ Failed to upload ${failedFiles.length} file(s): ${failedFiles.map(r => r.filename).join(', ')}. `;
      }
      summaryMessage += 'You can now ask questions about the uploaded documents!';
      
      // Add a system message to show the upload results
      const fileMessage: ChatMessage = {
        role: 'assistant',
        content: summaryMessage,
        timestamp: new Date().toISOString(),
        document_id: firstSuccess?.document_id || undefined,
        source: 'document',
      };
      
      addMessage(fileMessage);
      
      // Show toast with summary
      const toastMessage = successfulFiles.length > 0 
        ? `Successfully uploaded ${successfulFiles.length} file(s)`
        : 'Upload completed with errors';
      const toastType: ToastType = successfulFiles.length > 0 ? 'success' : 'error';
      
      setToast({
        message: toastMessage,
        type: toastType,
      });
    } else {
      // Add error message to chat
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `❌ Failed to upload files. ${error ?? 'Please try again.'}`,
        timestamp: new Date().toISOString(),
        source: 'openai',
      };
      
      addMessage(errorMessage);
      
      setToast({
        message: error ?? 'Failed to upload files. Please try again.',
        type: 'error',
      });
    }
  };

  const handleFileDrop = async (file: File) => {
    // Legacy single file support
    console.log('handleFileDrop called with file:', file.name);
    
    // Add a user message showing the file being uploaded
    const userMessage: ChatMessage = {
      role: 'user',
      content: `📎 Uploading file: ${file.name}`,
      timestamp: new Date().toISOString(),
    };
    
    addMessage(userMessage);
    
    console.log('Calling uploadFile from hook...');
    const response = await uploadFile(file);
    console.log('Upload response:', response);
    
    if (response) {
      // Store the document ID
      setCurrentDocumentId(response.document_id);
      
      // Add a system message to show the uploaded file
      const fileMessage: ChatMessage = {
        role: 'assistant',
        content: `✅ File "${response.filename}" uploaded successfully and is being processed for embeddings. You can now ask questions about this document!`,
        timestamp: new Date().toISOString(),
        document_id: response.document_id,
        source: 'document',
      };
      
      addMessage(fileMessage);
      
      setToast({
        message: `File "${response.filename}" uploaded successfully`,
        type: 'success',
      });
    } else {
      // Add error message to chat
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `❌ Failed to upload file "${file.name}". ${error ?? 'Please try again.'}`,
        timestamp: new Date().toISOString(),
        source: 'openai',
      };
      
      addMessage(errorMessage);
      
      setToast({
        message: error ?? 'Failed to upload file. Please try again.',
        type: 'error',
      });
    }
  };

  const SourceBadge = ({ source }: { source?: 'document' | 'openai' }) => {
    if (!source) return null;
    
    return (
      <div className="flex items-center gap-1 text-xs text-gray-500 mt-2">
        {source === 'document' ? (
          <>
            <DocumentTextIcon className="h-3 w-3" />
            <span>From Document</span>
          </>
        ) : (
          <>
            <SparklesIcon className="h-3 w-3" />
            <span>From OpenAI</span>
          </>
        )}
      </div>
    );
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  useEffect(() => {
    // Initialize Web Speech API
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      
      recognitionInstance.continuous = true;
      recognitionInstance.interimResults = true;
      recognitionInstance.lang = 'en-US';
      
      recognitionInstance.onresult = (event: any) => {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }
        
        setTranscript(finalTranscript);
        setInterimTranscript(interimTranscript);
      };
      
      recognitionInstance.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
        setToast({
          message: `Speech recognition error: ${event.error}`,
          type: 'error',
        });
      };
      
      recognitionInstance.onend = () => {
        setIsRecording(false);
      };
      
      setRecognition(recognitionInstance);
    }
  }, []);

  const handleVoiceInput = () => {
    if (!recognition) {
      setToast({
        message: 'Speech recognition is not supported in this browser',
        type: 'error',
      });
      return;
    }
    
    if (isRecording) {
      recognition.stop();
      setIsRecording(false);
      // Send the transcript as a message
      if (transcript.trim()) {
        handleSendMessage(transcript);
        setTranscript('');
        setInterimTranscript('');
      }
    } else {
      recognition.start();
      setIsRecording(true);
      setTranscript('');
      setInterimTranscript('');
    }
  };

  // Show loading state while messages are being loaded
  if (isLoadingMessages) {
    return (
      <div className="flex flex-col h-full">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {[...Array(3)].map((_, index) => (
            <div key={index} className={`flex gap-3 ${index % 2 === 0 ? 'justify-end' : 'justify-start'}`}>
              {index % 2 === 0 ? (
                <>
                  <div className="max-w-[80%] rounded-lg px-4 py-3 bg-blue-600 animate-pulse">
                    <div className="h-4 bg-blue-500 rounded w-32 mb-2"></div>
                    <div className="h-3 bg-blue-500 rounded w-16"></div>
                  </div>
                  <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full flex-shrink-0"></div>
                </>
              ) : (
                <>
                  <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full flex-shrink-0"></div>
                  <div className="max-w-[80%] rounded-lg px-4 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 animate-pulse">
                    <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-48 mb-2"></div>
                    <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-40 mb-2"></div>
                    <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-20"></div>
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
        <div className="border-t border-gray-200 dark:border-gray-700 p-4">
          <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse"></div>
        </div>
      </div>
    );
  }

  return (
    <DragAndDropWrapper 
      onFilesDrop={handleFilesUpload} 
      onFileDrop={handleFileDrop} 
      isUploading={isUploading}
    >
      <div className="flex flex-col h-full">
        {/* Voice Transcript Display */}
        {isRecording && (transcript || interimTranscript) && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border-b border-blue-200 dark:border-blue-800 p-3">
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
                  Listening...
                </span>
              </div>
              <div className="text-sm text-blue-600 dark:text-blue-400">
                {transcript}
                <span className="text-blue-400 dark:text-blue-500">{interimTranscript}</span>
              </div>
            </div>
          </div>
        )}

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-center">
              <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/20 rounded-full flex items-center justify-center mb-4">
                <QuestionMarkCircleIcon className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Welcome to ClariFlow
              </h3>
              <p className="text-gray-600 dark:text-gray-400 max-w-md">
                Start a conversation by typing a message below. You can ask questions about uploaded documents or have a general chat.
              </p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-3 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/20 rounded-full flex items-center justify-center flex-shrink-0">
                    <SparklesIcon className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                  </div>
                )}
                
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  <div className={`text-xs mt-2 ${
                    message.role === 'user' ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'
                  }`}>
                    {formatTimestamp(message.timestamp)}
                  </div>
                  <SourceBadge source={message.source} />
                </div>
                
                {message.role === 'user' && (
                  <div className="w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center flex-shrink-0">
                    <UserIcon className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                  </div>
                )}
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/20 rounded-full flex items-center justify-center flex-shrink-0">
                <SparklesIcon className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  <span className="text-gray-600 dark:text-gray-400">Thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* File Previews */}
        {filePreviews.length > 0 && (
          <div className="border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 p-4">
            <div className="max-w-4xl mx-auto">
              <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">
                Files ({filePreviews.length})
              </h4>
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {filePreviews.map((filePreview) => (
                  <FilePreview
                    key={filePreview.id}
                    filePreview={filePreview}
                    onRemove={removeFilePreview}
                  />
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Chat Input */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-4 relative">
          {showDemo ? (
            <DragAndDropDemo onClose={() => setShowDemo(false)} />
          ) : (
            <div className="flex items-end gap-2">
              <div className="flex-1">
                <ChatInput
                  ref={chatInputRef}
                  onSend={handleSendMessage}
                  isLoading={isLoading || isUploading}
                  onFilesUpload={handleFilesUpload}
                  onFileUpload={handleFileDrop}
                  filePreviews={filePreviews}
                  onRemoveFile={removeFilePreview}
                />
              </div>
              {/* Voice Input Button */}
              <button
                onClick={handleVoiceInput}
                disabled={isLoading || isUploading}
                className={`p-2 rounded-md transition-colors mb-2 ${
                  isRecording 
                    ? 'bg-red-500 hover:bg-red-600 text-white' 
                    : 'bg-gray-200 hover:bg-gray-300 text-gray-700 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-gray-300'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
                title={isRecording ? 'Stop recording' : 'Voice input'}
              >
                {isRecording ? (
                  <StopIcon className="h-5 w-5" />
                ) : (
                  <MicrophoneIcon className="h-5 w-5" />
                )}
              </button>
            </div>
          )}
          <DragHint />
        </div>

        {/* Toast Notifications */}
        {toast && (
          <Toast
            message={toast.message}
            type={toast.type}
            onClose={() => setToast(null)}
          />
        )}
      </div>
    </DragAndDropWrapper>
  );
});

Chat.displayName = 'Chat';

export default Chat; 