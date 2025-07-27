# Global Drag & Drop Feature - ClariFlow Frontend

## Overview

The global drag-and-drop feature allows users to drop files anywhere on the chat window, not just in specific upload areas. This provides a more intuitive and user-friendly experience for file uploads.

## Features

### 🎯 Core Functionality
- **Global Drop Zone**: Entire chat window acts as a drop zone
- **Document-Level Detection**: Uses document event listeners for seamless detection
- **Full-Screen Overlay**: Beautiful overlay appears when dragging files
- **Multi-File Support**: Accepts multiple files simultaneously
- **Real-Time Validation**: Validates file types and sizes on drop
- **Error Handling**: Shows clear error messages for invalid files

### 🎨 User Experience
- **Visual Feedback**: Animated drop overlay with clear messaging
- **Drag Hint**: Subtle tooltip that appears on hover near chat input
- **Progress Indication**: Shows upload progress and status
- **Responsive Design**: Works across all screen sizes
- **Dark Mode Support**: Fully compatible with dark/light themes

## Component Architecture

### 1. DragAndDropWrapper
**Location**: `src/components/chat/DragAndDropWrapper.tsx`

**Purpose**: Main wrapper component that provides global drag-and-drop functionality.

**Key Features**:
- Document-level event listeners for global detection
- Full-screen overlay with animated styling
- File validation and error handling
- Support for both single and multiple file drops

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

**Usage**:
```tsx
<DragAndDropWrapper onFilesDrop={handleFilesUpload} onFileDrop={handleFileDrop}>
  <div className="chat-window">
    {/* Entire chat interface */}
  </div>
</DragAndDropWrapper>
```

### 2. DragHint
**Location**: `src/components/chat/DragHint.tsx`

**Purpose**: Subtle tooltip that hints users about the global drag-and-drop functionality.

**Features**:
- Appears on hover near chat input
- Smooth fade-in/out animations
- Responsive positioning
- Dark mode support

### 3. GlobalDragDropTest
**Location**: `src/components/chat/GlobalDragDropTest.tsx`

**Purpose**: Test component to demonstrate and validate the global drag-and-drop functionality.

**Features**:
- Multiple test areas across the page
- Real-time file preview
- Upload controls and results display
- Comprehensive error handling

## Implementation Details

### Document-Level Event Listeners

The component uses document-level event listeners to capture drag events anywhere on the page:

```typescript
useEffect(() => {
  document.addEventListener('dragenter', handleDocumentDragEnter);
  document.addEventListener('dragleave', handleDocumentDragLeave);
  document.addEventListener('dragover', handleDocumentDragOver);
  document.addEventListener('drop', handleDocumentDrop);

  return () => {
    document.removeEventListener('dragenter', handleDocumentDragEnter);
    document.removeEventListener('dragleave', handleDocumentDragLeave);
    document.removeEventListener('dragover', handleDocumentDragOver);
    document.removeEventListener('drop', handleDocumentDrop);
  };
}, []);
```

### Drag Counter Logic

Uses a counter to handle nested drag events properly:

```typescript
const [dragCounter, setDragCounter] = useState(0);

const handleDocumentDragEnter = useCallback((e: DragEvent) => {
  setDragCounter(prev => prev + 1);
  setIsDragging(true);
}, []);

const handleDocumentDragLeave = useCallback((e: DragEvent) => {
  setDragCounter(prev => {
    const newCount = prev - 1;
    if (newCount <= 0) {
      setIsDragging(false);
    }
    return newCount;
  });
}, []);
```

### Full-Screen Overlay

The overlay uses fixed positioning to cover the entire viewport:

```tsx
{isDragging && (
  <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-indigo-50/95 backdrop-blur-sm">
    <div className="flex flex-col items-center space-y-6 rounded-xl border-4 border-dashed border-indigo-400 bg-white/90 p-12 shadow-2xl">
      {/* Drop content */}
    </div>
  </div>
)}
```

## File Validation

### Supported Formats
- **PDF** (`.pdf`)
- **Text** (`.txt`)
- **Word Documents** (`.docx`)

### Size Limits
- **Maximum**: 10MB per file
- **Validation**: Real-time during drag and drop

### Error Messages
- File type not supported
- File size exceeds limit
- Upload already in progress
- No files dropped

## Integration with Existing Components

### Chat Component Integration

The Chat component now wraps the entire interface with DragAndDropWrapper:

```tsx
return (
  <DragAndDropWrapper onFilesDrop={handleFilesUpload} onFileDrop={handleFileDrop}>
    <div className="flex flex-col h-full">
      {/* Messages Container */}
      {/* File Previews */}
      {/* Chat Input with DragHint */}
    </div>
  </DragAndDropWrapper>
);
```

### File Upload Hook Integration

Uses the existing `useFileUpload` hook for:
- File validation
- Upload processing
- Progress tracking
- Error handling

## Styling and Theming

### Color Scheme
- **Primary**: Indigo (`indigo-400`, `indigo-500`, `indigo-600`)
- **Success**: Green (`green-100`, `green-800`)
- **Error**: Red (`red-100`, `red-800`)
- **Background**: Gray scale with dark mode support

### Animations
- **Fade In/Out**: Smooth opacity transitions
- **Bounce**: Animated icon during drag
- **Slide**: Tooltip entrance animations

### Responsive Design
- **Mobile**: Optimized touch interactions
- **Tablet**: Adaptive overlay sizing
- **Desktop**: Full feature set

## Testing

### Manual Testing
1. **Basic Functionality**:
   - Drag files from desktop to any area of chat window
   - Verify overlay appears and disappears correctly
   - Test file validation and error messages

2. **Edge Cases**:
   - Drag multiple files simultaneously
   - Try invalid file types
   - Test with files exceeding size limit
   - Drag during active upload

3. **User Experience**:
   - Verify drag hint appears on hover
   - Test responsive behavior
   - Check dark mode compatibility

### Test Component
Use `GlobalDragDropTest` component for comprehensive testing:

```tsx
import GlobalDragDropTest from '@/components/chat/GlobalDragDropTest';

// In your test page
<GlobalDragDropTest />
```

## Browser Compatibility

### Supported Browsers
- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

### Feature Detection
- **Drag and Drop API**: Native browser support
- **File API**: Modern browser support
- **CSS Grid/Flexbox**: Layout compatibility

## Performance Considerations

### Event Listener Management
- Proper cleanup of document event listeners
- Debounced drag counter updates
- Efficient re-renders with useCallback

### Memory Management
- File object cleanup after upload
- Preview component unmounting
- Error state reset

## Future Enhancements

### Planned Features
- **Drag Preview**: Show file thumbnails during drag
- **Batch Operations**: Select multiple files for batch actions
- **Keyboard Shortcuts**: Ctrl+V for paste upload
- **Drag Zones**: Configurable drop zones

### Accessibility Improvements
- **Screen Reader Support**: ARIA labels and descriptions
- **Keyboard Navigation**: Tab through upload areas
- **High Contrast Mode**: Enhanced visibility options

## Troubleshooting

### Common Issues

1. **Overlay Not Appearing**:
   - Check z-index values
   - Verify event listener attachment
   - Ensure drag events are not being blocked

2. **File Validation Errors**:
   - Check file type extensions
   - Verify file size calculations
   - Review validation logic

3. **Performance Issues**:
   - Monitor event listener cleanup
   - Check for memory leaks
   - Optimize re-render cycles

### Debug Mode
Enable console logging for debugging:

```typescript
const DEBUG = process.env.NODE_ENV === 'development';

if (DEBUG) {
  console.log('Drag event:', event);
}
```

## Migration Guide

### From Local Drag-and-Drop
1. Remove local drag event handlers
2. Wrap entire component with DragAndDropWrapper
3. Update file handling callbacks
4. Test global functionality

### Breaking Changes
- Drag events now handled at document level
- Overlay positioning changed to fixed
- Z-index values updated for global overlay

## Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `npm install`
3. Start development server: `npm run dev`
4. Test global drag-and-drop functionality

### Code Style
- Use TypeScript for type safety
- Follow React hooks best practices
- Maintain consistent naming conventions
- Add comprehensive JSDoc comments

---

**Last Updated**: December 2024
**Version**: 1.0.0
**Author**: ClariFlow Development Team 