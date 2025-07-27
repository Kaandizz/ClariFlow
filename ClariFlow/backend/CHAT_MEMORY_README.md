# ClariFlow Chat Memory & Session Management

## Overview

ClariFlow now supports persistent chat memory and session management, allowing users to maintain conversation history across multiple chat sessions, similar to ChatGPT. This feature enables users to:

- Create and manage multiple chat sessions
- Maintain conversation context across sessions
- Auto-generate session titles from first messages
- Retrieve and continue previous conversations
- Delete sessions and their associated messages

## Features

### 🧠 Chat Sessions
- **Unique Session IDs**: Each chat session has a unique UUID identifier
- **Session Titles**: Customizable titles with auto-generation from first user message
- **Timestamps**: Created and updated timestamps for session management
- **Message Counts**: Track number of messages in each session

### 💬 Message History
- **Persistent Storage**: All messages stored in SQLite database
- **Chronological Order**: Messages retrieved in timestamp order
- **Role Tracking**: Distinguish between user and assistant messages
- **Source Tracking**: Track if response came from documents or general chat
- **Document Context**: Associate messages with specific documents

### 🔄 Session Management
- **Create Sessions**: Start new conversations with optional titles
- **List Sessions**: View all available chat sessions
- **Load Sessions**: Retrieve complete conversation history
- **Update Titles**: Rename sessions for better organization
- **Delete Sessions**: Remove sessions and all associated messages

## Database Schema

### ChatSession Table
```sql
CREATE TABLE chat_sessions (
    id VARCHAR PRIMARY KEY,
    title VARCHAR DEFAULT 'New Chat',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### ChatMessage Table
```sql
CREATE TABLE chat_messages (
    id VARCHAR PRIMARY KEY,
    session_id VARCHAR NOT NULL,
    role VARCHAR NOT NULL,  -- 'user' or 'assistant'
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    document_id VARCHAR,
    source VARCHAR,  -- 'document' or 'openai'
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
);
```

## API Endpoints

### Chat Endpoint
**POST** `/api/chat`

Send a message and get AI response with session support.

**Request Body:**
```json
{
    "query": "Your message here",
    "session_id": "optional-session-id",
    "history": []  // Optional, will use session history if session_id provided
}
```

**Response:**
```json
{
    "response": "AI response",
    "source": "document|openai",
    "session_id": "session-uuid",
    "timestamp": "2024-01-01T12:00:00Z",
    "document_id": "optional-document-id",
    "sources": ["source1", "source2"],
    "used_context": true,
    "matched_chunks": ["chunk1", "chunk2"],
    "relevance_score": 0.95
}
```

### Session Management Endpoints

#### Get All Sessions
**GET** `/api/sessions`

Returns list of all chat sessions.

**Response:**
```json
[
    {
        "id": "session-uuid",
        "title": "Session Title",
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:30:00Z",
        "message_count": 6
    }
]
```

#### Get Session Messages
**GET** `/api/sessions/{session_id}`

Returns all messages from a specific session.

**Response:**
```json
[
    {
        "id": "message-uuid",
        "role": "user",
        "content": "User message",
        "timestamp": "2024-01-01T12:00:00Z",
        "document_id": "optional-document-id",
        "source": "document|openai"
    }
]
```

#### Create Session
**POST** `/api/sessions`

Create a new chat session.

**Request Body:**
```json
{
    "title": "Optional Session Title"
}
```

**Response:**
```json
{
    "id": "session-uuid",
    "title": "Session Title",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z",
    "message_count": 0
}
```

#### Update Session Title
**PUT** `/api/sessions/{session_id}`

Update the title of a chat session.

**Request Body:**
```json
{
    "title": "New Session Title"
}
```

#### Delete Session
**DELETE** `/api/sessions/{session_id}`

Delete a chat session and all its messages.

**Response:**
```json
{
    "message": "Chat session deleted successfully"
}
```

## Usage Examples

### Starting a New Conversation
```python
import requests

# Create a new session
response = requests.post("http://localhost:8000/api/sessions", json={
    "title": "Document Analysis Session"
})
session = response.json()
session_id = session['id']

# Send first message
response = requests.post("http://localhost:8000/api/chat", json={
    "query": "Hello, can you help me analyze this document?",
    "session_id": session_id
})
```

### Continuing an Existing Conversation
```python
# Send message to existing session
response = requests.post("http://localhost:8000/api/chat", json={
    "query": "What was our previous discussion about?",
    "session_id": "existing-session-id"
})
```

### Retrieving Conversation History
```python
# Get all sessions
sessions = requests.get("http://localhost:8000/api/sessions").json()

# Get messages from specific session
messages = requests.get(f"http://localhost:8000/api/sessions/{session_id}").json()
```

## Auto-Generated Titles

When a user sends their first message in a session with the default title "New Chat", the system automatically generates a title from the first 50 characters of the message:

- **Input**: "Can you help me analyze the quarterly financial report for Q3 2024?"
- **Generated Title**: "Can you help me analyze the quarterly financial report for Q3 2024?"

- **Input**: "What are the key performance indicators mentioned in the document?"
- **Generated Title**: "What are the key performance indicators mentioned in the document?"

## Testing

Run the comprehensive test script to verify all functionality:

```bash
cd backend
python test_chat_memory.py
```

The test script covers:
- Session creation and management
- Chat functionality with and without sessions
- Message history retrieval
- Session title updates
- Session deletion
- Error handling

## Database Setup

The database is automatically created when the application starts. The SQLite database file (`clariflow.db`) will be created in the backend directory.

To manually create tables:
```python
from app.core.database import engine, Base
Base.metadata.create_all(bind=engine)
```

## Configuration

Database configuration is handled in `app/core/config.py`:

```python
database_url: str = "sqlite:///./clariflow.db"
```

For production, consider using PostgreSQL:
```python
database_url: str = "postgresql://user:password@localhost/clariflow"
```

## Error Handling

The API includes comprehensive error handling:

- **404**: Session not found
- **400**: Invalid request data
- **500**: Internal server errors

All errors include descriptive messages for debugging.

## Performance Considerations

- **Indexing**: Consider adding database indexes for frequently queried fields
- **Pagination**: For large message histories, implement pagination
- **Cleanup**: Implement automatic cleanup of old sessions
- **Backup**: Regular database backups for production deployments

## Security Considerations

- **Input Validation**: All inputs are validated using Pydantic models
- **SQL Injection**: Protected through SQLAlchemy ORM
- **Session Isolation**: Each session is isolated with unique IDs
- **Data Privacy**: Consider implementing user authentication for multi-user environments

## Future Enhancements

- **User Authentication**: Multi-user support with session ownership
- **Message Search**: Full-text search across conversation history
- **Session Sharing**: Share sessions between users
- **Export/Import**: Export conversations to various formats
- **Message Reactions**: Add reactions to messages
- **File Attachments**: Support for file attachments in messages 