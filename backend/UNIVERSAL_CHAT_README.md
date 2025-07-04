# Universal Chatbot Upgrade for ClariFlow

## Overview

The ClariFlow backend has been upgraded to support **universal chatbot queries** — combining general AI chat capabilities with document-based question answering. This creates a seamless experience where users can have natural conversations that intelligently reference uploaded documents when relevant.

## Features

### 🎯 Universal Chat Endpoint
- **Endpoint**: `POST /api/chat`
- **Request Body**:
  ```json
  {
    "query": "string",
    "history": ["string", ...]  // Optional: Previous conversation turns
  }
  ```
- **Response**:
  ```json
  {
    "response": "AI reply",
    "source": "document" | "openai",
    "sources": ["chunk1", "chunk2", ...],  // Document chunks if used
    "document_id": "uuid",  // Document ID if used
    "timestamp": "2024-01-01T12:00:00",
    "used_context": true | false,
    "matched_chunks": ["chunk1", "chunk2", ...],  // Debug info
    "relevance_score": 0.85  // Debug info
  }
  ```

### 🧠 Intelligent Behavior

1. **Document-Aware**: If files are uploaded, the system searches for relevant content
2. **Context-Aware**: Uses conversation history to maintain context
3. **Fallback Support**: Gracefully falls back to general chat if no relevant documents found
4. **Smart Thresholding**: Only uses document context when relevance score > 0.3

### 🔧 Technical Implementation

#### ChatService Class
- **Location**: `app/services/chat_service.py`
- **Key Methods**:
  - `chat(query, history)`: Main universal chat handler
  - `_handle_general_chat(query, history)`: OpenAI-based general chat
  - `_try_document_search(query, documents, history)`: Document search with RAG

#### Configuration
- **Similarity Threshold**: 0.3 (minimum relevance to use document context)
- **Max History Length**: 5 turns (to save tokens)
- **Search Results**: Top 3 most relevant chunks per document

## Usage Examples

### General Chat (No Documents)
```python
# Request
{
  "query": "What is the capital of France?",
  "history": ["Hello!", "Hi there! How can I help you today?"]
}

# Response
{
  "response": "The capital of France is Paris...",
  "source": "openai",
  "used_context": false,
  "relevance_score": null
}
```

### Document-Based Chat
```python
# Request
{
  "query": "What are the main topics in this document?",
  "history": ["Can you help me understand this document?"]
}

# Response
{
  "response": "Based on the document content, the main topics are...",
  "source": "document",
  "used_context": true,
  "document_id": "uuid-123",
  "relevance_score": 0.85,
  "matched_chunks": ["chunk1", "chunk2"]
}
```

### Conversation Flow
```python
# Request with conversation history
{
  "query": "Can you elaborate on that?",
  "history": [
    "What is machine learning?",
    "Machine learning is a subset of AI...",
    "How does it work?",
    "It works by training algorithms on data..."
  ]
}
```

## API Endpoints

### POST /api/chat
Universal chatbot endpoint that handles both document-based and general queries.

**Request**:
- `query` (string, required): User's question/message
- `history` (array of strings, optional): Previous conversation turns

**Response**:
- `response` (string): AI's reply
- `source` (string): "document" or "openai"
- `sources` (array, optional): Document chunks used
- `document_id` (string, optional): ID of document used
- `timestamp` (datetime): Response timestamp
- `used_context` (boolean): Whether document context was used
- `matched_chunks` (array, optional): Debug info - matched chunks
- `relevance_score` (float, optional): Debug info - relevance score

### GET /api/documents
Get list of available documents for chat.

**Response**:
```json
{
  "documents": ["uuid-1", "uuid-2", ...]
}
```

## Testing

Run the test script to verify functionality:

```bash
cd backend
python test_universal_chat.py
```

The test script covers:
- ✅ General chat without documents
- ✅ Document-based chat (if documents exist)
- ✅ Conversation flow with history
- ✅ Edge cases (empty queries, long history)

## Best Practices

### 1. History Management
- Keep history short (last 3-5 turns) to save tokens
- History is automatically truncated to `max_history_length`

### 2. Error Handling
- Graceful fallback if document search fails
- Comprehensive logging for debugging
- Proper error responses with meaningful messages

### 3. Performance
- Efficient document search with ChromaDB
- Token optimization with history truncation
- Caching of document collections

### 4. Security
- Input validation for queries
- Safe handling of file paths
- Environment variable configuration for API keys

## Debug Features

The system includes debug metadata to help understand its behavior:

- `used_context`: Whether document context was used
- `matched_chunks`: Which document chunks were found relevant
- `relevance_score`: How relevant the found chunks were (0-1)

## Dependencies

- **LangChain**: Document processing and embeddings
- **OpenAI**: GPT-4 for chat completions
- **ChromaDB**: Vector database for document search
- **FastAPI**: Web framework
- **Pydantic**: Data validation
- **Python-dotenv**: Environment variable management

## Configuration

Environment variables required:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Future Enhancements

1. **Streaming Responses**: Real-time response streaming
2. **Multi-Modal Support**: Image and audio processing
3. **Advanced RAG**: More sophisticated retrieval methods
4. **Conversation Memory**: Persistent conversation storage
5. **Custom Models**: Support for other LLM providers

## Troubleshooting

### Common Issues

1. **No documents found**: Check if files have been uploaded and processed
2. **Low relevance scores**: Adjust `similarity_threshold` in ChatService
3. **API key errors**: Verify `OPENAI_API_KEY` environment variable
4. **ChromaDB errors**: Check database path and permissions

### Logging

The system provides comprehensive logging:
- Request/response logging
- Document search details
- Error tracking
- Performance metrics

Check logs for detailed debugging information. 