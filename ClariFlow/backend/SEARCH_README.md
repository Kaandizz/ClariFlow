# ClariFlow Search Functionality

This document describes the file-based semantic search functionality added to ClariFlow's backend.

## Overview

The search functionality allows users to perform semantic search across previously uploaded documents using vector embeddings stored in ChromaDB. The system uses the same embedding model (OpenAI text-embedding-3-small) that was used during document processing to ensure consistency.

## Features

- **Semantic Search**: Search using natural language queries
- **File-specific Search**: Option to search within a specific uploaded document
- **Configurable Results**: Adjustable number of top results (default: 5)
- **Rich Metadata**: Results include source file, page numbers, and similarity scores
- **Cross-document Search**: Search across all uploaded documents or within specific files

## API Endpoints

### 1. Search Documents

**Endpoint**: `POST /api/search`

**Description**: Perform semantic search across uploaded documents.

**Request Body**:
```json
{
  "query": "What is the main topic of the document?",
  "file_id": "optional-document-id",
  "top_k": 5
}
```

**Parameters**:
- `query` (required): The search query text
- `file_id` (optional): Document ID to search within a specific document
- `top_k` (optional): Number of top results to return (default: 5)

**Response**:
```json
{
  "results": [
    {
      "text": "Relevant chunk text...",
      "score": 0.87,
      "source_file": "example.pdf",
      "page_number": 4,
      "chunk_index": 12
    }
  ],
  "total_results": 1,
  "query": "What is the main topic of the document?"
}
```

**Response Fields**:
- `results`: Array of search results
  - `text`: The relevant text chunk
  - `score`: Similarity score (0-1, higher is better)
  - `source_file`: Name of the source file
  - `page_number`: Page number (if available)
  - `chunk_index`: Index of the chunk in the document
- `total_results`: Total number of results found
- `query`: The original search query

### 2. Get Available Documents

**Endpoint**: `GET /api/documents`

**Description**: Get a list of all available documents for search.

**Response**:
```json
{
  "documents": [
    {
      "document_id": "uuid-string",
      "source_file": "example.pdf",
      "chunk_count": 25
    }
  ],
  "total_documents": 1
}
```

## Implementation Details

### Architecture

The search functionality is implemented using a layered architecture:

1. **API Layer** (`app/api/search.py`): Handles HTTP requests and responses
2. **Service Layer** (`app/services/search_service.py`): Contains business logic for search operations
3. **Model Layer** (`app/models/search.py`): Defines data models for requests and responses
4. **Embedding Layer** (`app/services/embedding.py`): Reuses existing embedding service

### Search Process

1. **Query Embedding**: The search query is embedded using the same model as document chunks
2. **Vector Search**: ChromaDB performs similarity search using the query embedding
3. **Result Processing**: Raw results are processed to extract metadata and calculate scores
4. **Score Conversion**: L2 distances are converted to similarity scores (0-1 scale)
5. **Result Sorting**: Results are sorted by similarity score in descending order

### File Organization

```
backend/
├── app/
│   ├── api/
│   │   └── search.py              # Search API endpoints
│   ├── models/
│   │   └── search.py              # Search data models
│   └── services/
│       └── search_service.py      # Search business logic
├── main.py                        # Updated to include search router
└── test_search.py                 # Test script for search functionality
```

## Usage Examples

### Basic Search

```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key features?",
    "top_k": 3
  }'
```

### Search Within Specific Document

```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic?",
    "file_id": "3094660a-9445-4e80-b62f-0fa725d87e98",
    "top_k": 5
  }'
```

### Get Available Documents

```bash
curl -X GET "http://localhost:8000/api/documents"
```

## Testing

Run the test script to verify the search functionality:

```bash
cd backend
python test_search.py
```

The test script will:
1. Test the documents endpoint
2. Test basic search functionality
3. Test search with file ID filtering

## Error Handling

The search functionality includes comprehensive error handling:

- **Empty Query**: Returns 400 error for empty search queries
- **Invalid File ID**: Gracefully handles non-existent document collections
- **Connection Errors**: Proper error messages for ChromaDB connection issues
- **Embedding Errors**: Handles OpenAI API errors during embedding creation

## Performance Considerations

- **Chunk Size**: Documents are split into 1000-character chunks with 200-character overlap
- **Vector Search**: Uses ChromaDB's efficient vector similarity search
- **Result Limiting**: Configurable result count to control response size
- **Caching**: ChromaDB provides persistent storage for embeddings

## Dependencies

The search functionality relies on the existing ClariFlow dependencies:
- `chromadb`: Vector database for similarity search
- `langchain_openai`: OpenAI embeddings
- `fastapi`: Web framework for API endpoints
- `pydantic`: Data validation and serialization

## Future Enhancements

Potential improvements for the search functionality:

1. **Advanced Filtering**: Add filters for date ranges, file types, etc.
2. **Search Analytics**: Track popular searches and improve relevance
3. **Fuzzy Matching**: Add support for typo-tolerant search
4. **Search Suggestions**: Provide query suggestions based on document content
5. **Batch Search**: Support for multiple queries in a single request
6. **Search History**: Store and retrieve previous search queries 