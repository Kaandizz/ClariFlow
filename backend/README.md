# ClariFlow Backend

A FastAPI-based backend for the ClariFlow AI chatbot that supports both document-based and general-purpose conversations.

## Features

### 🤖 Hybrid Chat Intelligence
- **Document-Based Chat**: Ask questions about uploaded documents using vector similarity search
- **General Chat**: Have open-ended conversations like ChatGPT
- **Intelligent Routing**: Automatically detects when to use document context vs general AI
- **Seamless Experience**: Single endpoint handles both modes

### 📄 Document Processing
- Support for PDF, TXT, and DOCX files
- Automatic text extraction and chunking
- Vector embeddings using OpenAI
- ChromaDB for efficient similarity search

### 🔧 Technical Stack
- **Python 3.11**
- **FastAPI** - Modern, fast web framework
- **LangChain** - AI/ML framework for document processing
- **ChromaDB** - Vector database for embeddings
- **OpenAI GPT-4** - Advanced language model
- **Pydantic** - Data validation and serialization

## Quick Start

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the backend directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
CHROMA_PERSIST_DIRECTORY=chroma_db
LOG_LEVEL=INFO
```

### 3. Start the Server
```bash
python main.py
```

The server will start on `http://localhost:8000`

## API Endpoints

### Chat Endpoint
**POST** `/api/chat`

Send any question or message to the AI assistant.

**Request:**
```json
{
  "query": "What is the capital of France?"
}
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

### Upload Endpoint
**POST** `/api/upload`

Upload documents for context-aware chat.

**Request:** Multipart form data with file

**Response:**
```json
{
  "filename": "document.pdf",
  "status": "success",
  "message": "Document processed successfully",
  "document_id": "doc_123",
  "chunk_count": 15
}
```

### Health Check
**GET** `/health`

Check if the service is running.

**Response:**
```json
{
  "status": "healthy"
}
```

### Documents List
**GET** `/api/documents`

Get list of available documents.

**Response:**
```json
{
  "documents": ["doc_123", "doc_456"]
}
```

## How It Works

### Intelligent Chat Routing

1. **Document Detection**: System checks if documents are available in ChromaDB
2. **Query Analysis**: For each query, searches through available documents
3. **Relevance Scoring**: Calculates similarity scores using vector embeddings
4. **Smart Routing**: 
   - If relevance score > 0.3: Uses document context
   - If relevance score ≤ 0.3: Falls back to general AI chat
5. **Response Generation**: Provides contextual or general responses accordingly

### Document Processing Pipeline

1. **File Upload**: Accepts PDF, TXT, DOCX files
2. **Text Extraction**: Extracts text content from files
3. **Chunking**: Splits text into manageable chunks
4. **Embedding**: Generates vector embeddings using OpenAI
5. **Storage**: Stores embeddings in ChromaDB for similarity search

## Testing

Run the comprehensive test suite:

```bash
python test_chat.py
```

This will test:
- Health endpoint functionality
- General chat responses
- Document endpoint availability
- Invalid request handling

## Development

### Project Structure
```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Configuration
│   ├── models/        # Pydantic models
│   ├── services/      # Business logic
│   └── utils/         # Utilities
├── chroma_db/         # Vector database storage
├── uploads/           # Uploaded files
├── main.py           # Application entry point
├── requirements.txt  # Dependencies
└── test_chat.py      # Test suite
```

### Key Components

#### ChatService (`app/services/chat_service.py`)
- Main chat logic with hybrid intelligence
- Document search and relevance scoring
- OpenAI integration for responses

#### Document Processing (`app/services/document_processing.py`)
- File processing and text extraction
- Chunking and embedding generation
- ChromaDB integration

#### API Endpoints (`app/api/`)
- Chat endpoint for conversations
- Upload endpoint for documents
- Health and utility endpoints

## Configuration Options

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `CHROMA_PERSIST_DIRECTORY`: ChromaDB storage directory
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)

### Model Settings
- **General Chat**: GPT-4, 1500 max tokens, temperature 0.7
- **Document Chat**: GPT-4, 1000 max tokens, temperature 0.3
- **Relevance Threshold**: 0.3 (configurable)

## Error Handling

The system includes comprehensive error handling for:
- Invalid API requests
- OpenAI API errors
- File upload issues
- Database connection problems
- Document processing errors

All errors return appropriate HTTP status codes and user-friendly messages.

## Performance Considerations

- **Async Processing**: All I/O operations are asynchronous
- **Connection Pooling**: Efficient database connections
- **Caching**: ChromaDB provides fast similarity search
- **Chunking**: Documents are processed in manageable chunks

## Security

- **Input Validation**: All inputs validated with Pydantic
- **File Type Restrictions**: Only allowed file types accepted
- **Size Limits**: File size restrictions enforced
- **API Key Security**: Environment variable protection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the documentation
2. Run the test suite
3. Review error logs
4. Create an issue with detailed information 