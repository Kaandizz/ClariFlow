# ClariFlow Multi-File Upload Feature

## Overview

The ClariFlow backend has been upgraded to support **multi-file uploads** and **batch document processing**. This enhancement allows users to upload multiple documents simultaneously, with comprehensive validation, processing, and detailed status reporting.

## 🚀 Features

### Core Functionality
- **Multi-file upload**: Upload multiple files in a single request
- **Batch processing**: Process all files efficiently with parallel validation
- **Comprehensive validation**: File type, size, and content validation
- **Detailed reporting**: Individual status for each uploaded file
- **Backward compatibility**: Single file upload still supported
- **Async processing**: Non-blocking file handling with `aiofiles`

### File Support
- **PDF** (`.pdf`) - Using PyPDFLoader
- **DOCX** (`.docx`) - Using Docx2txtLoader  
- **TXT** (`.txt`) - Using TextLoader

### Validation Rules
- **File size**: Maximum 10MB per file
- **File types**: Only PDF, DOCX, and TXT allowed
- **Content validation**: Automatic content extraction and validation

## 📡 API Endpoints

### 1. Multi-File Upload
```http
POST /api/upload
Content-Type: multipart/form-data
```

**Request:**
- `files`: List of files to upload (multiple files with same field name)

**Response:**
```json
{
  "message": "2 out of 3 files processed successfully",
  "total_files": 3,
  "successful_uploads": 2,
  "failed_uploads": 1,
  "results": [
    {
      "filename": "document1.pdf",
      "status": "success",
      "error_message": null,
      "chunk_count": 15,
      "document_id": "uuid-1234-5678-9abc-def0"
    },
    {
      "filename": "document2.txt",
      "status": "success", 
      "error_message": null,
      "chunk_count": 8,
      "document_id": "uuid-8765-4321-fedc-ba98"
    },
    {
      "filename": "invalid.jpg",
      "status": "error",
      "error_message": "Unsupported file type '.jpg'. Allowed types: .pdf, .docx, .txt",
      "chunk_count": null,
      "document_id": null
    }
  ]
}
```

### 2. Single File Upload (Backward Compatible)
```http
POST /api/upload/single
Content-Type: multipart/form-data
```

**Request:**
- `file`: Single file to upload

**Response:** Same format as multi-file upload with `total_files: 1`

## 🔧 Implementation Details

### File Processing Pipeline

1. **File Reception**: Files are received via FastAPI's `UploadFile`
2. **Temporary Storage**: Files are saved to temporary location using `aiofiles`
3. **Validation**: Each file is validated for type and size
4. **Content Extraction**: Document content is extracted based on file type
5. **Chunking**: Content is split using `RecursiveCharacterTextSplitter`
6. **Embedding Generation**: OpenAI embeddings are created for each chunk
7. **Storage**: Chunks and embeddings are stored in ChromaDB
8. **Cleanup**: Temporary files are removed

### Error Handling

The system provides granular error handling:

- **File-level errors**: Individual file failures don't affect other files
- **Validation errors**: Clear error messages for size/type violations
- **Processing errors**: Detailed error reporting for content extraction issues
- **Graceful degradation**: Partial success scenarios are handled properly

### Logging

Comprehensive logging is implemented:
- File upload events
- Processing status per file
- Chunk generation counts
- Error details for debugging

## 📝 Usage Examples

### Python Requests Example

```python
import requests

# Multi-file upload
files = [
    ('files', ('document1.pdf', open('document1.pdf', 'rb'), 'application/pdf')),
    ('files', ('document2.txt', open('document2.txt', 'rb'), 'text/plain')),
    ('files', ('document3.docx', open('document3.docx', 'rb'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'))
]

response = requests.post('http://localhost:8000/api/upload', files=files)
result = response.json()

print(f"Processed {result['successful_uploads']} out of {result['total_files']} files")
for file_result in result['results']:
    print(f"{file_result['filename']}: {file_result['status']}")
```

### JavaScript/Fetch Example

```javascript
const formData = new FormData();
formData.append('files', file1);
formData.append('files', file2);
formData.append('files', file3);

const response = await fetch('/api/upload', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(`Processed ${result.successful_uploads} out of ${result.total_files} files`);
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "files=@document1.pdf" \
  -F "files=@document2.txt" \
  -F "files=@document3.docx"
```

## 🧪 Testing

A comprehensive test suite is included:

```bash
cd backend
python test_multi_upload.py
```

The test suite covers:
- Single file uploads
- Multi-file uploads
- Mixed valid/invalid files
- Empty uploads
- Server health checks

## 🔄 Migration Guide

### For Existing Frontend Code

If you're updating from the old single-file upload:

**Old endpoint:**
```javascript
// Old single file upload
const formData = new FormData();
formData.append('file', file);
const response = await fetch('/api/upload', { method: 'POST', body: formData });
```

**New multi-file upload:**
```javascript
// New multi-file upload
const formData = new FormData();
files.forEach(file => formData.append('files', file));
const response = await fetch('/api/upload', { method: 'POST', body: formData });
```

**Backward compatibility:**
```javascript
// Still works for single files
const formData = new FormData();
formData.append('file', file);
const response = await fetch('/api/upload/single', { method: 'POST', body: formData });
```

## 📊 Performance Considerations

### Batch Processing Benefits
- **Reduced overhead**: Single HTTP request for multiple files
- **Parallel validation**: Files are validated concurrently
- **Efficient storage**: Temporary files are cleaned up automatically
- **Memory optimization**: Files are processed one at a time to manage memory

### Scalability
- **Configurable limits**: File size and count limits can be adjusted
- **Async processing**: Non-blocking file operations
- **Resource management**: Automatic cleanup prevents disk space issues

## 🔒 Security Features

- **File type validation**: Prevents malicious file uploads
- **Size limits**: Prevents DoS attacks via large files
- **Content validation**: Ensures files contain valid document content
- **Temporary file cleanup**: Automatic removal of uploaded files

## 🛠️ Configuration

Key configuration options in `app/core/config.py`:

```python
# File Upload Configuration
upload_dir: str = "uploads"
max_file_size: int = 10 * 1024 * 1024  # 10MB
allowed_extensions: list = [".pdf", ".docx", ".txt"]
```

## 📈 Monitoring

The system provides detailed metrics:
- Files processed per request
- Success/failure rates
- Chunk generation statistics
- Processing time per file

## 🚀 Future Enhancements

Potential future improvements:
- **Duplicate detection**: File hash-based duplicate prevention
- **Progress tracking**: Real-time upload progress
- **Resume capability**: Resume interrupted uploads
- **Compression support**: Handle compressed archives
- **OCR integration**: Extract text from images

---

## 📞 Support

For issues or questions about the multi-file upload feature:
1. Check the test suite for usage examples
2. Review the API documentation
3. Check server logs for detailed error information
4. Verify file format and size requirements 