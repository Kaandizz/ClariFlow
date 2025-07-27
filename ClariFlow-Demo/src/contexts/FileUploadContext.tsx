"use client";

import { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import { toast } from 'react-hot-toast';
import { uploadFiles, type FileUploadResult } from '@/lib/api';

interface UploadProgress {
  fileName: string;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
}

interface FileUploadContextType {
  showDemo: boolean;
  setShowDemo: (show: boolean) => void;
  currentDocumentId: string | null;
  setCurrentDocumentId: (documentId: string | null) => void;
  uploadProgress: UploadProgress[];
  isUploading: boolean;
  uploadFiles: (files: FileList) => Promise<void>;
  clearUploadProgress: () => void;
}

const FileUploadContext = createContext<FileUploadContextType | undefined>(undefined);

export function FileUploadProvider({ children }: { children: ReactNode }) {
  const [showDemo, setShowDemo] = useState(false);
  const [currentDocumentId, setCurrentDocumentId] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const handleUploadFiles = useCallback(async (files: FileList) => {
    const fileArray = Array.from(files);
    
    // Initialize progress tracking
    const initialProgress: UploadProgress[] = fileArray.map(file => ({
      fileName: file.name,
      progress: 0,
      status: 'pending'
    }));
    
    setUploadProgress(initialProgress);
    setIsUploading(true);

    try {
      // Update status to uploading
      setUploadProgress(prev => 
        prev.map(p => ({ ...p, status: 'uploading' as const, progress: 10 }))
      );

      // Simulate progress updates (in real implementation, this would come from upload progress)
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => 
          prev.map(p => 
            p.status === 'uploading' && p.progress < 90 
              ? { ...p, progress: p.progress + 10 }
              : p
          )
        );
      }, 200);

      // Perform the actual upload
      const response = await uploadFiles(fileArray);
      
      // Clear progress interval
      clearInterval(progressInterval);

      // Update final status based on results
      setUploadProgress(prev => 
        prev.map(p => {
          const result = response.results.find(r => r.filename === p.fileName);
          if (result) {
            return {
              ...p,
              progress: 100,
              status: result.status === 'success' ? 'success' : 'error',
              error: result.error_message || undefined
            };
          }
          return { ...p, progress: 100, status: 'success' };
        })
      );

      // Show success/error toasts
      if (response.successful_uploads > 0) {
        toast.success(
          `Successfully uploaded ${response.successful_uploads} of ${response.total_files} files`,
          {
            duration: 5000,
            icon: '✅'
          }
        );
      }

      if (response.failed_uploads > 0) {
        toast.error(
          `Failed to upload ${response.failed_uploads} files. Check the upload status for details.`,
          {
            duration: 7000,
            icon: '❌'
          }
        );
      }

      // Auto-clear progress after 5 seconds
      setTimeout(() => {
        setUploadProgress([]);
      }, 5000);

    } catch (error) {
      // Handle upload error
      setUploadProgress(prev => 
        prev.map(p => ({
          ...p,
          progress: 0,
          status: 'error' as const,
          error: error instanceof Error ? error.message : 'Upload failed'
        }))
      );

      toast.error('Upload failed. Please try again.', {
        duration: 5000,
        icon: '❌'
      });
    } finally {
      setIsUploading(false);
    }
  }, []);

  const clearUploadProgress = useCallback(() => {
    setUploadProgress([]);
  }, []);

  return (
    <FileUploadContext.Provider value={{
      showDemo,
      setShowDemo,
      currentDocumentId,
      setCurrentDocumentId,
      uploadProgress,
      isUploading,
      uploadFiles: handleUploadFiles,
      clearUploadProgress,
    }}>
      {children}
    </FileUploadContext.Provider>
  );
}

export function useFileUploadContext() {
  const context = useContext(FileUploadContext);
  if (context === undefined) {
    throw new Error('useFileUploadContext must be used within a FileUploadProvider');
  }
  return context;
} 