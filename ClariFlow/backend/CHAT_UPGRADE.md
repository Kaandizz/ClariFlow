# ClariFlow Chat Upgrade - General Purpose Chat Support

## Overview
The ClariFlow chatbot has been upgraded to support both document-based and general-purpose chat functionality. Users can now ask any question and the system will intelligently route between document context and general AI responses.

## Key Features Implemented

### 1. Enhanced Chat Endpoint (`/api/chat`)
- **Request Format**: `{"query": "user's message"}`
- **Response Format**: 
  ```json
  {
    "response": "AI reply",
    "source": "document" | "openai",
    "sources": ["document chunks if applicable"],
    "document_id": "document ID if applicable",
    "timestamp": "ISO timestamp"
  }
  ```

### 2. Intelligent Routing Logic
- **Document Detection**: Automatically checks if documents are available
- **Relevance Scoring**: Uses vector similarity search with relevance threshold (0.3)
- **Fallback Mechanism**: Falls back to general OpenAI chat when no relevant documents found
- **Hybrid Responses**: Can combine document context with general knowledge

### 3. Updated Models

#### ChatRequest (Updated)
```python
class ChatRequest(BaseModel):
    query: str  # Changed from 'question' to 'query'
```

#### ChatResponse (Enhanced)
```python
class ChatResponse(BaseModel):
    response: str  # Changed from 'answer' to 'response'
    source: str  # 'document' or 'openai'
    sources: Optional[List[str]] = None
    document_id: Optional[str] = None
    timestamp: datetime
```

### 4. Enhanced ChatService

#### Key Methods:
- `chat(query: str)`: Main entry point for all chat requests
- `_handle_general_chat(query: str)`: Handles general OpenAI conversations
- `_try_document_search(query: str, documents: List[str])`: Searches documents for relevance
- `get_available_documents()`: Lists available document collections

#### Routing Logic:
1. Check if documents exist in ChromaDB
2. If no documents: Use general OpenAI chat
3. If documents exist: Search for relevant information
4. If relevance score > 0.3: Use document-based response
5. If relevance score ≤ 0.3: Fall back to general OpenAI chat

### 5. Frontend Updates

#### API Client (`frontend/src/lib/api.ts`)
- Updated `ChatRequest` interface to use `query` instead of `question`
- Updated `ChatResponse` interface to include `source` field
- Enhanced `ChatMessage` interface with optional `source` tracking

#### Chat Component (`frontend/src/components/chat/Chat.tsx`)
- Updated to use new API interface
- Added source tracking in message display
- Enhanced UI to show response source (document vs general AI)

## Technical Implementation

### Backend Changes
1. **Models** (`app/models/chat.py`): Updated request/response schemas
2. **Service** (`app/services/chat_service.py`): Complete rewrite with hybrid logic
3. **API** (`app/api/chat.py`): Updated endpoint to use new interface

### Frontend Changes
1. **API Client**: Updated interfaces and request format
2. **Chat Component**: Enhanced to handle new response format
3. **UI Enhancements**: Added source indicators for responses

## Usage Examples

### General Chat (No Documents)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the capital of France?"}'
```

**Response:**
```json
{
  "response": "The capital of France is Paris...",
  "source": "openai",
  "sources": null,
  "document_id": null,
  "timestamp": "2024-01-15T10:30:00"
}
```

### Document-Based Chat (With Uploaded Documents)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What does the document say about AI?"}'
```

**Response:**
```json
{
  "response": "According to the document, AI is defined as...",
  "source": "document",
  "sources": ["document chunk 1", "document chunk 2"],
  "document_id": "doc_123",
  "timestamp": "2024-01-15T10:30:00"
}
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for both general and document-based chat
- `CHROMA_PERSIST_DIRECTORY`: Directory for ChromaDB storage

### Model Configuration
- **General Chat**: Uses GPT-4 with 1500 max tokens
- **Document Chat**: Uses GPT-4 with 1000 max tokens and lower temperature (0.3)
- **Relevance Threshold**: 0.3 (configurable in chat service)

## Error Handling

### Backend Error Handling
- Invalid requests (empty query, missing fields)
- OpenAI API errors
- ChromaDB connection issues
- Document processing errors

### Frontend Error Handling
- Network errors
- API response errors
- File upload errors
- User-friendly error messages

## Testing

### Test Script
A comprehensive test script (`test_chat.py`) is included to verify:
- Health endpoint functionality
- General chat responses
- Document endpoint availability
- Invalid request handling

### Manual Testing
1. Start the backend server: `python main.py`
2. Run tests: `python test_chat.py`
3. Test with frontend: Upload documents and chat

## Future Enhancements

### Potential Improvements
1. **Conversation Memory**: Maintain chat history across sessions
2. **Multi-Document Support**: Handle queries across multiple documents
3. **Advanced Relevance**: Implement more sophisticated relevance scoring
4. **Response Caching**: Cache common responses for performance
5. **User Preferences**: Allow users to prefer document vs general responses

### Performance Optimizations
1. **Async Processing**: Implement background document processing
2. **Response Streaming**: Stream responses for better UX
3. **Connection Pooling**: Optimize database connections
4. **Response Caching**: Cache frequently asked questions

## Migration Notes

### Breaking Changes
- API request format changed from `question` to `query`
- API response format changed from `answer` to `response`
- Added required `source` field in responses

### Backward Compatibility
- Frontend has been updated to handle new API format
- Old document-based functionality preserved
- Enhanced with general chat capabilities

## Conclusion

The ClariFlow chatbot now provides a seamless experience for both document-based and general-purpose conversations. Users can ask any question and receive intelligent responses that leverage available document context when relevant, while falling back to general AI knowledge when appropriate.

The implementation maintains the existing document upload and processing capabilities while adding powerful general chat functionality, making ClariFlow a versatile AI assistant for various use cases. 