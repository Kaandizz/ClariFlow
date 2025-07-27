# ClariFlow Frontend Multi-File Upload Feature

## Overview

The ClariFlow frontend has been upgraded to support **multi-file uploads** with drag-and-drop functionality, real-time validation, and comprehensive status tracking. This enhancement provides a seamless user experience for uploading multiple documents simultaneously.

## 🚀 Features

### Core Functionality
- **Multi-file selection**: Select multiple files via the upload button
- **Drag-and-drop support**: Drop multiple files anywhere on the chat interface
- **Real-time validation**: Instant feedback on file type and size validation
- **File previews**: Visual list of selected files with status indicators
- **Batch processing**: Upload all valid files in a single request
- **Progress tracking**: Real-time status updates for each file
- **Error handling**: Detailed error messages for failed uploads
- **Backward compatibility**: Single file upload still supported

### File Support
- **PDF** (`.pdf`) - Using PyPDFLoader
- **DOCX** (`.docx`) - Using Docx2txtLoader  
- **TXT** (`.txt`) - Using TextLoader

### Validation Rules
- **File size**: Maximum 10MB per file
- **File types**: Only PDF, DOCX, and TXT allowed
- **Duplicate prevention**: Automatic duplicate file detection

## 📁 Component Architecture

### Updated Components

#### 1. `FileDropZone.tsx`
**Purpose**: File selection and validation interface

**Key Features**:
- Multiple file selection via button click
- File validation with error display
- File preview integration
- Backward compatibility with single file upload

**Props**:
```typescript
interface FileDropZoneProps {
  onFilesSelect: (files: File[]) => void;
  onFileSelect?: (file: File) => void; // Legacy support
  isUploading: boolean;
  className?: string;
  showPreviews?: boolean;
  filePreviews?: FilePreview[];
  onRemoveFile?: (id: string) => void;
}
```

#### 2. `DragAndDropWrapper.tsx`
**Purpose**: Global drag-and-drop zone wrapper

**Key Features**:
- Multiple file drop support
- Visual feedback during drag operations
- File validation on drop
- Error handling for invalid files

**Props**:
```typescript
interface DragAndDropWrapperProps {
  children: React.ReactNode;
  onFilesDrop: (files: File[]) => void;
  onFileDrop?: (file: File) => void; // Legacy support
  isUploading?: boolean;
  className?: string;
}
```

#### 3. `FilePreview.tsx` (New)
**Purpose**: Individual file status display

**Key Features**:
- File type icons
- Status indicators (pending, uploading, success, error)
- Progress bars for uploading files
- Error message display
- Remove file functionality

**Props**:
```typescript
interface FilePreviewProps {
  filePreview: FilePreview;
  onRemove: (id: string) => void;
}
```

#### 4. `ChatInput.tsx`
**Purpose**: Enhanced chat input with file upload integration

**Key Features**:
- Multi-file upload support
- File preview integration
- Upload status display
- Backward compatibility

#### 5. `Chat.tsx`
**Purpose**: Main chat interface with file upload handling

**Key Features**:
- Batch file upload processing
- Upload status messages in chat
- File preview section
- Error handling and user feedback

## 🔧 Hook: `useFileUpload`

### Enhanced State Management
```typescript
interface FileUploadState {
  isUploading: boolean;
  error: string | null;
  filePreviews: FilePreview[];
}

interface FilePreview {
  id: string;
  file: File;
  status: 'pending' | 'valid' | 'invalid' | 'uploading' | 'success' | 'error';
  error?: string;
  progress?: number;
}
```

### Key Methods
- `uploadFiles(files: File[])`: Batch upload multiple files
- `uploadFile(file: File)`: Single file upload (legacy)
- `addFilePreviews(files: File[])`: Add files to preview list
- `removeFilePreview(id: string)`: Remove file from preview
- `clearFilePreviews()`: Clear all file previews
- `validateFiles(files: File[])`: Validate multiple files

## 📡 API Integration

### Multi-File Upload Endpoint
```typescript
// POST /api/upload
const uploadFiles = async (files: File[]): Promise<MultiFileUploadResponse> => {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });
  
  const response = await api.post<MultiFileUploadResponse>('/api/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  
  return response.data;
};
```

### Response Format
```typescript
interface MultiFileUploadResponse {
  message: string;
  total_files: number;
  successful_uploads: number;
  failed_uploads: number;
  results: FileUploadResult[];
}

interface FileUploadResult {
  filename: string;
  status: 'success' | 'error';
  error_message?: string | null;
  chunk_count?: number | null;
  document_id?: string | null;
}
```

## 🎨 User Experience

### File Selection Flow
1. **Button Selection**: Click paperclip icon → Select multiple files
2. **Drag & Drop**: Drag files onto chat area → Automatic validation
3. **Preview Display**: Files appear in preview list with status
4. **Validation**: Invalid files marked with error messages
5. **Upload**: Valid files processed in batch
6. **Status Updates**: Real-time progress and results

### Visual Feedback
- **File Type Icons**: 📄 for PDF/TXT, 📝 for DOCX
- **Status Colors**: 
  - Green: Success
  - Red: Error/Invalid
  - Blue: Uploading
  - Gray: Pending
- **Progress Bars**: For uploading files
- **Error Messages**: Clear validation feedback

### Chat Integration
- Upload messages appear in chat history
- Success/failure summaries
- Document context for subsequent questions
- Toast notifications for quick feedback

## 🔄 Migration Guide

### For Existing Code

**Old Single File Upload**:
```typescript
// Old usage
<FileDropZone
  onFileSelect={handleFileSelect}
  isUploading={isUploading}
/>

<DragAndDropWrapper onFileDrop={handleFileDrop}>
  {/* content */}
</DragAndDropWrapper>
```

**New Multi-File Upload**:
```typescript
// New usage
<FileDropZone
  onFilesSelect={handleFilesSelect}
  onFileSelect={handleFileSelect} // Still supported
  isUploading={isUploading}
  filePreviews={filePreviews}
  onRemoveFile={handleRemoveFile}
/>

<DragAndDropWrapper 
  onFilesDrop={handleFilesDrop}
  onFileDrop={handleFileDrop} // Still supported
>
  {/* content */}
</DragAndDropWrapper>
```

### Hook Usage
```typescript
// Old
const { isUploading, uploadFile, error } = useFileUpload();

// New
const { 
  isUploading, 
  uploadFiles, 
  uploadFile, // Still available
  error, 
  filePreviews, 
  addFilePreviews, 
  removeFilePreview 
} = useFileUpload();
```

## 🧪 Testing

### Test Component
Use `MultiFileUploadTest.tsx` for comprehensive testing:

```typescript
import MultiFileUploadTest from '@/components/chat/MultiFileUploadTest';

// Add to your page
<MultiFileUploadTest />
```

### Test Scenarios
1. **Valid Files**: Upload multiple valid files
2. **Invalid Files**: Test with unsupported types/sizes
3. **Mixed Files**: Valid + invalid files
4. **Drag & Drop**: Test drag-and-drop functionality
5. **Error Handling**: Network errors, API failures
6. **Progress Tracking**: Monitor upload progress
7. **File Removal**: Remove files from preview

## 🎯 Usage Examples

### Basic Multi-File Upload
```typescript
import { useFileUpload } from '@/hooks/useFileUpload';

function MyComponent() {
  const { 
    isUploading, 
    uploadFiles, 
    filePreviews, 
    addFilePreviews 
  } = useFileUpload();

  const handleFilesSelect = (files: File[]) => {
    addFilePreviews(files);
  };

  const handleUpload = async () => {
    const files = filePreviews
      .filter(fp => fp.status === 'pending')
      .map(fp => fp.file);
    
    const result = await uploadFiles(files);
    console.log('Upload result:', result);
  };

  return (
    <div>
      <FileDropZone
        onFilesSelect={handleFilesSelect}
        isUploading={isUploading}
      />
      <button onClick={handleUpload} disabled={isUploading}>
        Upload Files
      </button>
    </div>
  );
}
```

### Drag & Drop Integration
```typescript
import DragAndDropWrapper from '@/components/chat/DragAndDropWrapper';

function MyApp() {
  const handleFilesDrop = (files: File[]) => {
    // Handle dropped files
    console.log('Dropped files:', files);
  };

  return (
    <DragAndDropWrapper onFilesDrop={handleFilesDrop}>
      <div>Your app content</div>
    </DragAndDropWrapper>
  );
}
```

## 🔒 Security & Validation

### Client-Side Validation
- File type checking (MIME types)
- File size limits (10MB per file)
- Duplicate file detection
- Real-time validation feedback

### Error Handling
- Network error recovery
- API error responses
- Validation error display
- Graceful degradation

## 📊 Performance Considerations

### Optimization Features
- **Lazy Loading**: File previews load on demand
- **Batch Processing**: Single API call for multiple files
- **Memory Management**: Automatic cleanup of file references
- **Progress Tracking**: Real-time status updates

### Best Practices
- Limit file selection to reasonable numbers
- Provide clear feedback for large uploads
- Handle network timeouts gracefully
- Implement retry mechanisms for failed uploads

## 🚀 Future Enhancements

### Potential Improvements
- **Progress Tracking**: Real-time upload progress per file
- **Resume Uploads**: Resume interrupted uploads
- **File Compression**: Client-side compression for large files
- **Preview Generation**: Thumbnail previews for documents
- **Bulk Operations**: Select/deselect all files
- **Upload Queue**: Queue management for large batches

### Advanced Features
- **OCR Integration**: Extract text from images
- **File Conversion**: Convert unsupported formats
- **Cloud Storage**: Direct cloud storage integration
- **Version Control**: File version management

---

## 📞 Support

For issues or questions about the multi-file upload feature:
1. Check the test component for usage examples
2. Review the API documentation
3. Verify file format and size requirements
4. Check browser console for error details
5. Ensure backend is running and accessible

## 🔗 Related Documentation
- [Backend Multi-File Upload README](../backend/MULTI_FILE_UPLOAD_README.md)
- [API Documentation](../backend/MULTI_FILE_UPLOAD_README.md#api-endpoints)
- [Testing Guide](./MULTI_FILE_UPLOAD_FRONTEND_README.md#testing) 