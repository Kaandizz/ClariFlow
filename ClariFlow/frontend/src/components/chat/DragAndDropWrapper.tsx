"use client";

import { useState, useCallback, useRef, useEffect } from 'react';
import { DocumentArrowUpIcon, ExclamationTriangleIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';
import { validateFiles } from '@/hooks/useFileUpload';

interface DragAndDropWrapperProps {
  children: React.ReactNode;
  onFilesDrop: (files: File[]) => void;
  onFileDrop?: (file: File) => void; // Legacy single file support
  isUploading?: boolean;
  className?: string;
}

export default function DragAndDropWrapper({ 
  children, 
  onFilesDrop,
  onFileDrop,
  isUploading = false,
  className 
}: DragAndDropWrapperProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [dragCounter, setDragCounter] = useState(0);
  const [dragError, setDragError] = useState<string | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);
  const [isDragActive, setIsDragActive] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Document-level drag event handlers for global detection
  const handleDocumentDragEnter = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Only handle file drops
    if (e.dataTransfer?.types.includes('Files')) {
      setDragCounter(prev => prev + 1);
      setDragError(null);
      setIsDragging(true);
      setIsDragActive(true);
    }
  }, []);

  const handleDocumentDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    setDragCounter(prev => {
      const newCount = prev - 1;
      if (newCount <= 0) {
        setIsDragging(false);
        setIsDragActive(false);
        setDragError(null);
      }
      return newCount;
    });
  }, []);

  const handleDocumentDragOver = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Add visual feedback based on drag position
    if (e.dataTransfer) {
      e.dataTransfer.dropEffect = 'copy';
    }
  }, []);

  const handleDocumentDrop = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    setIsDragActive(false);
    setDragCounter(0);
    setDragError(null);

    const files = Array.from(e.dataTransfer?.files || []);
    
    if (files.length === 0) {
      setDragError('No files were dropped.');
      setTimeout(() => setDragError(null), 3000);
      return;
    }

    if (isUploading) {
      setDragError('Upload already in progress. Please wait.');
      setTimeout(() => setDragError(null), 3000);
      return;
    }

    // Validate files
    const { validFiles, invalidFiles } = validateFiles(files);
    
    if (validFiles.length === 0) {
      const errorMessage = invalidFiles.length === 1 
        ? invalidFiles[0].error 
        : 'All dropped files are invalid.';
      setDragError(errorMessage);
      setTimeout(() => setDragError(null), 4000);
      return;
    }

    // Show success animation
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 2000);

    // Show warnings for invalid files
    if (invalidFiles.length > 0) {
      const warningMessage = `${invalidFiles.length} file(s) were skipped due to validation errors.`;
      setDragError(warningMessage);
      setTimeout(() => setDragError(null), 4000);
    }

    // Handle single file for backward compatibility
    if (validFiles.length === 1 && onFileDrop) {
      onFileDrop(validFiles[0]);
    } else {
      // Handle multiple files
      onFilesDrop(validFiles);
    }
  }, [onFilesDrop, onFileDrop, isUploading]);

  // Set up document-level event listeners for global drag detection
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
  }, [handleDocumentDragEnter, handleDocumentDragLeave, handleDocumentDragOver, handleDocumentDrop]);

  return (
    <div
      ref={wrapperRef}
      className={cn("relative h-full", className)}
    >
      {/* Main content */}
      {children}

      {/* Global drag overlay - full screen */}
      {isDragging && (
        <div className={cn(
          "fixed inset-0 z-[9999] flex items-center justify-center transition-all duration-300",
          "bg-gradient-to-br from-indigo-50/95 to-blue-50/95 backdrop-blur-sm",
          "dark:from-indigo-900/95 dark:to-blue-900/95"
        )}>
          <div className={cn(
            "flex flex-col items-center space-y-6 rounded-2xl p-12 max-w-md mx-4 transform transition-all duration-300",
            "bg-white/90 dark:bg-gray-800/90 shadow-2xl",
            isDragActive ? "scale-105 shadow-3xl" : "scale-100",
            dragError ? "border-4 border-dashed border-red-400" : "border-4 border-dashed border-indigo-400",
            showSuccess ? "border-green-400" : ""
          )}>
            {dragError ? (
              <>
                <ExclamationTriangleIcon className="h-16 w-16 text-red-500 animate-pulse" />
                <div className="text-center">
                  <p className="text-xl font-semibold text-red-900 dark:text-red-100 mb-2">
                    Upload Error
                  </p>
                  <p className="text-sm text-red-600 dark:text-red-400 max-w-sm">
                    {dragError}
                  </p>
                </div>
              </>
            ) : showSuccess ? (
              <>
                <CheckCircleIcon className="h-16 w-16 text-green-500 animate-pulse" />
                <div className="text-center">
                  <p className="text-xl font-semibold text-green-900 dark:text-green-100 mb-2">
                    Files Accepted!
                  </p>
                  <p className="text-sm text-green-600 dark:text-green-400 max-w-sm">
                    Your files are being processed...
                  </p>
                </div>
              </>
            ) : (
              <>
                <DocumentArrowUpIcon className={cn(
                  "h-16 w-16 text-indigo-500 transition-transform duration-300",
                  isDragActive ? "animate-bounce scale-110" : "animate-pulse"
                )} />
                <div className="text-center">
                  <p className="text-xl font-semibold text-indigo-900 dark:text-indigo-100 mb-2">
                    Drop files to upload
                  </p>
                  <p className="text-sm text-indigo-600 dark:text-indigo-400 max-w-sm">
                    Supported formats: PDF, TXT, DOCX (max 10MB each)
                  </p>
                  <p className="text-xs text-indigo-500 dark:text-indigo-300 mt-3">
                    You can drop files anywhere on this window
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Upload progress indicator */}
      {isUploading && (
        <div className="fixed bottom-4 right-4 z-50">
          <div className="bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
            <span className="text-sm">Uploading files...</span>
          </div>
        </div>
      )}
    </div>
  );
} 