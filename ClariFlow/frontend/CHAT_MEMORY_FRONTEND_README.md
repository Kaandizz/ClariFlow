# ClariFlow Frontend - Chat Memory & Thread View

## Overview

This document describes the implementation of chat memory and thread view functionality in the ClariFlow frontend. The feature allows users to manage multiple chat sessions, view conversation history, and switch between different threads seamlessly.

## Features Implemented

### 🧵 Thread Management
- **Thread Sidebar**: Displays all chat sessions in a scrollable sidebar
- **Session Creation**: Create new chat sessions with the "New Chat" button
- **Session Selection**: Click on any thread to load its conversation history
- **Active Session Highlighting**: Visual indication of the currently active session

### 📝 Session Operations
- **Rename Sessions**: Inline editing of session titles with hover actions
- **Delete Sessions**: Remove sessions with confirmation dialog
- **Auto-title Generation**: Session titles are automatically generated from the first user message

### 💬 Message History
- **Persistent Storage**: All messages are stored and retrieved from the backend
- **Chronological Display**: Messages are shown in the correct order
- **Loading States**: Smooth loading indicators while fetching session data
- **Real-time Updates**: New messages are immediately added to the current session

### 🎨 UI/UX Features
- **Responsive Design**: Works on desktop and tablet devices
- **Dark Mode Support**: Full dark mode compatibility
- **Smooth Animations**: Loading spinners and transitions
- **Error Handling**: Toast notifications for errors and success states

## Architecture

### State Management
We use **Zustand** for state management with the following store structure:

```typescript
interface ChatState {
  // Sessions
  sessions: ChatSession[];
  activeSessionId: string | null;
  isLoadingSessions: boolean;
  
  // Messages
  messages: ChatMessage[];
  isLoadingMessages: boolean;
  
  // UI State
  isCreatingSession: boolean;
  isDeletingSession: boolean;
  isUpdatingTitle: boolean;
  
  // Actions
  setSessions: (sessions: ChatSession[]) => void;
  setActiveSession: (sessionId: string | null) => void;
  setMessages: (messages: ChatMessage[]) => void;
  addMessage: (message: ChatMessage) => void;
  // ... more actions
}
```

### Component Structure

```
src/
├── components/
│   ├── chat/
│   │   ├── ThreadSidebar.tsx      # Main sidebar component
│   │   ├── ChatThreadItem.tsx     # Individual thread item
│   │   └── Chat.tsx               # Updated chat component
│   └── layout/
│       └── MainLayout.tsx         # Updated layout with sidebar
├── store/
│   └── chatStore.ts               # Zustand store
└── lib/
    └── api.ts                     # Updated API functions
```

## Key Components

### ThreadSidebar
The main sidebar component that manages the list of chat sessions.

**Features:**
- Loads and displays all chat sessions
- Handles session creation, deletion, and selection
- Manages loading states and error handling
- Provides timestamp formatting

**Props:** None (uses Zustand store)

**Key Methods:**
- `loadSessions()`: Fetches all sessions from the backend
- `handleCreateNewChat()`: Creates a new session
- `handleSelectSession()`: Switches to a different session
- `handleDeleteSession()`: Removes a session with confirmation

### ChatThreadItem
Individual thread item component with edit and delete functionality.

**Features:**
- Displays session title, timestamp, and message count
- Hover actions for edit and delete
- Inline editing with keyboard shortcuts (Enter/Escape)
- Visual feedback for active state

**Props:**
```typescript
interface ChatThreadItemProps {
  session: ChatSession;
  isActive: boolean;
  isEditing: boolean;
  editTitle: string;
  onSelect: () => void;
  onDelete: () => void;
  onStartEdit: () => void;
  onSaveEdit: () => void;
  onCancelEdit: () => void;
  onEditTitleChange: (title: string) => void;
  formatTimestamp: (timestamp: string) => string;
  isDeleting: boolean;
}
```

### Updated Chat Component
Enhanced chat component that integrates with session management.

**Key Changes:**
- Uses Zustand store for state management
- Loads messages when active session changes
- Sends session_id with chat requests
- Handles loading states for message history

## API Integration

### Backend Endpoints Used
- `GET /api/sessions` - Get all chat sessions
- `POST /api/sessions` - Create new session
- `GET /api/sessions/{session_id}` - Get session messages
- `PUT /api/sessions/{session_id}` - Update session title
- `DELETE /api/sessions/{session_id}` - Delete session
- `POST /api/chat` - Send message (updated with session_id)

### API Functions
```typescript
// Session management
export const getChatSessions = async (): Promise<ChatSession[]>
export const createChatSession = async (request?: CreateSessionRequest): Promise<ChatSession>
export const getSessionMessages = async (sessionId: string): Promise<ChatMessageResponse[]>
export const updateSessionTitle = async (sessionId: string, request: UpdateSessionRequest): Promise<ChatSession>
export const deleteChatSession = async (sessionId: string): Promise<{ message: string }>

// Updated chat function
export const sendChatMessage = async (request: ChatRequest): Promise<ChatResponse>
```

## User Experience Flow

### 1. First Visit
1. User opens the application
2. Thread sidebar loads existing sessions (if any)
3. If no sessions exist, shows empty state with "New Chat" button
4. User can start typing to create their first session

### 2. Creating a New Chat
1. User clicks "New Chat" button
2. New session is created in the backend
3. Session appears at the top of the sidebar
4. Chat area is cleared and ready for new conversation
5. First message automatically sets the session title

### 3. Switching Between Sessions
1. User clicks on any session in the sidebar
2. Loading indicator appears
3. Session messages are fetched from backend
4. Chat area updates with conversation history
5. Active session is highlighted in sidebar

### 4. Managing Sessions
1. **Renaming**: Hover over session → click edit icon → type new title → press Enter
2. **Deleting**: Hover over session → click delete icon → confirm deletion
3. **Auto-title**: First user message automatically becomes session title

## Styling and Design

### Color Scheme
- **Primary**: Blue (#3B82F6) for active states and buttons
- **Secondary**: Gray tones for inactive states
- **Success**: Green for save actions
- **Error**: Red for delete actions

### Responsive Breakpoints
- **Desktop (lg+)**: Thread sidebar visible (320px width)
- **Tablet (md+)**: Main sidebar visible (256px width)
- **Mobile**: Sidebars hidden, full-width chat

### Dark Mode Support
All components include dark mode variants using Tailwind's dark: prefix:
- Background colors: `bg-white dark:bg-gray-800`
- Text colors: `text-gray-900 dark:text-white`
- Border colors: `border-gray-200 dark:border-gray-700`

## Error Handling

### Network Errors
- Toast notifications for API failures
- Graceful fallbacks for missing data
- Retry mechanisms for failed requests

### User Input Validation
- Confirmation dialogs for destructive actions
- Input validation for session titles
- Keyboard shortcuts for better UX

### Loading States
- Skeleton loaders for session list
- Spinner for message loading
- Disabled states during operations

## Performance Considerations

### Optimizations
- **Lazy Loading**: Messages loaded only when session is selected
- **Debounced Updates**: Session title updates are debounced
- **Memoization**: Components use React.memo where appropriate
- **Efficient Re-renders**: Zustand store prevents unnecessary re-renders

### Memory Management
- **Message Limits**: Only recent messages are kept in history
- **Session Cleanup**: Deleted sessions are properly removed from state
- **Garbage Collection**: Unused references are cleaned up

## Testing

### Manual Testing Checklist
- [ ] Create new chat session
- [ ] Send messages and verify they're saved
- [ ] Switch between sessions
- [ ] Rename session titles
- [ ] Delete sessions
- [ ] Test responsive design
- [ ] Verify dark mode functionality
- [ ] Test error scenarios (network failures)

### Component Testing
```bash
# Run tests
npm test

# Test specific components
npm test ThreadSidebar
npm test ChatThreadItem
npm test chatStore
```

## Future Enhancements

### Planned Features
- **Session Search**: Search through chat history
- **Session Export**: Export conversations to various formats
- **Session Sharing**: Share sessions between users
- **Message Reactions**: Add reactions to messages
- **File Attachments**: Support for file attachments in messages

### Technical Improvements
- **Virtual Scrolling**: For large message histories
- **Real-time Updates**: WebSocket integration for live updates
- **Offline Support**: Service worker for offline functionality
- **Advanced Search**: Full-text search across all sessions

## Troubleshooting

### Common Issues

**Session not loading:**
- Check backend API health
- Verify session_id is being sent correctly
- Check browser console for errors

**Messages not saving:**
- Ensure session_id is included in chat requests
- Verify backend database is accessible
- Check API response format

**UI not updating:**
- Verify Zustand store is properly connected
- Check component re-render triggers
- Ensure state updates are synchronous

### Debug Mode
Enable debug logging by setting:
```javascript
localStorage.setItem('debug', 'chat:*');
```

## Conclusion

The chat memory and thread view implementation provides a robust, user-friendly interface for managing multiple chat sessions. The architecture is scalable, maintainable, and follows React best practices. The integration with the backend ensures data persistence and real-time updates across sessions. 