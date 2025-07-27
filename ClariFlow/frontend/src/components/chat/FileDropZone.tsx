"use client";

import { useState, useRef, useCallback } from 'react';
import { PaperClipIcon } from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';
import { validateFiles } from '@/hooks/useFileUpload';
import FilePreview from './FilePreview';
import { type FilePreview as FilePreviewType } from '@/hooks/useFileUpload';

interface FileDropZoneProps {
  onFilesSelect: (files: File[]) => void;
  onFileSelect?: (file: File) => void; // Legacy single file support
  isUploading: boolean;
  className?: string;
  showPreviews?: boolean;
  filePreviews?: FilePreviewType[];
  onRemoveFile?: (id: string) => void;
}

export default function FileDropZone({ 
  onFilesSelect, 
  onFileSelect,
  isUploading, 
  className,
  showPreviews = true,
  filePreviews = [],
  onRemoveFile
}: FileDropZoneProps) {
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setError(null);
    
    if (files.length === 0) return;

    if (isUploading) {
      setError('Upload already in progress. Please wait.');
      setTimeout(() => setError(null), 2000);
      return;
    }

    // Validate files
    const { validFiles, invalidFiles } = validateFiles(files);
    
    if (validFiles.length === 0) {
      const errorMessage = invalidFiles.length === 1 
        ? invalidFiles[0].error 
        : 'All selected files are invalid.';
      setError(errorMessage);
      setTimeout(() => setError(null), 3000);
      return;
    }

    // Show warnings for invalid files
    if (invalidFiles.length > 0) {
      const warningMessage = `${invalidFiles.length} file(s) were skipped due to validation errors.`;
      setError(warningMessage);
      setTimeout(() => setError(null), 3000);
    }

    // Handle single file for backward compatibility
    if (validFiles.length === 1 && onFileSelect) {
      onFileSelect(validFiles[0]);
    } else {
      // Handle multiple files
      onFilesSelect(validFiles);
    }

    // Reset input value to allow selecting the same files again
    e.target.value = '';
  }, [onFilesSelect, onFileSelect, isUploading]);

  const handleButtonClick = useCallback(() => {
    if (!isUploading && fileInputRef.current) {
      fileInputRef.current.click();
    }
  }, [isUploading]);

  return (
    <div className={cn("relative", className)}>
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        accept=".pdf,.txt,.docx"
        multiple
        onChange={handleFileInput}
        disabled={isUploading}
      />

      {/* ChatGPT-style paperclip button */}
      <button
        type="button"
        onClick={handleButtonClick}
        disabled={isUploading}
        className={cn(
          "inline-flex items-center justify-center rounded-md p-2",
          "text-gray-500 hover:text-gray-700 hover:bg-gray-100",
          "dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700",
          "focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2",
          "dark:focus:ring-offset-gray-800",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          "transition-colors duration-200",
          "group"
        )}
        title="Attach files (PDF, TXT, DOCX, max 10MB each)"
      >
        <PaperClipIcon 
          className={cn(
            "h-5 w-5",
            "group-hover:scale-110 transition-transform duration-200"
          )} 
          aria-hidden="true" 
        />
        <span className="sr-only">Attach files</span>
      </button>

      {/* File previews */}
      {showPreviews && filePreviews.length > 0 && (
        <div className="absolute bottom-full left-0 mb-2 w-80 max-h-64 overflow-y-auto bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-2 z-20">
          <div className="space-y-2">
            {filePreviews.map((filePreview) => (
              <FilePreview
                key={filePreview.id}
                filePreview={filePreview}
                onRemove={onRemoveFile || (() => {})}
              />
            ))}
          </div>
        </div>
      )}

      {/* Error tooltip */}
      {error && (
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-red-100 dark:bg-red-900/90 border border-red-300 dark:border-red-700 text-red-700 dark:text-red-200 text-xs rounded-lg shadow-lg whitespace-nowrap z-10 max-w-xs">
          {error}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-red-300 dark:border-t-red-700"></div>
        </div>
      )}
    </div>
  );
} 