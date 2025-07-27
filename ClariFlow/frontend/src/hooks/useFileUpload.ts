import { useState, useCallback } from 'react';
import { uploadFiles, uploadFile, type MultiFileUploadResponse, type FileUploadResult } from '@/lib/api';

export interface FileUploadState {
  isUploading: boolean;
  error: string | null;
}

export interface FileUploadResponse {
  filename: string;
  status: string;
  message: string;
  document_id: string;
}

export interface FilePreview {
  id: string;
  file: File;
  status: 'pending' | 'valid' | 'invalid' | 'uploading' | 'success' | 'error';
  error?: string;
  progress?: number;
}

const ACCEPTED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'text/plain': ['.txt'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
};

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export interface FileValidationResult {
  isValid: boolean;
  error?: string;
}

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const validateFile = (file: File): FileValidationResult => {
  // Check file type
  if (!Object.keys(ACCEPTED_FILE_TYPES).includes(file.type)) {
    return { 
      isValid: false, 
      error: `File type not supported. Please use PDF, TXT, or DOCX files.` 
    };
  }

  // Check file size
  if (file.size > MAX_FILE_SIZE) {
    return { 
      isValid: false, 
      error: `File too large. Maximum size is 10MB (your file is ${formatFileSize(file.size)}).` 
    };
  }

  return { isValid: true };
};

export const validateFiles = (files: File[]): { validFiles: File[]; invalidFiles: { file: File; error: string }[] } => {
  const validFiles: File[] = [];
  const invalidFiles: { file: File; error: string }[] = [];

  files.forEach(file => {
    const validation = validateFile(file);
    if (validation.isValid) {
      validFiles.push(file);
    } else {
      invalidFiles.push({ file, error: validation.error || 'Invalid file' });
    }
  });

  return { validFiles, invalidFiles };
};

export const useFileUpload = () => {
  const [state, setState] = useState<FileUploadState>({
    isUploading: false,
    error: null,
  });

  const [filePreviews, setFilePreviews] = useState<FilePreview[]>([]);

  const uploadFilesHandler = useCallback(async (files: File[]): Promise<MultiFileUploadResponse | null> => {
    // Validate all files first
    const { validFiles, invalidFiles } = validateFiles(files);
    
    if (validFiles.length === 0) {
      const errorMessage = invalidFiles.length === 1 
        ? invalidFiles[0].error 
        : 'All selected files are invalid.';
      setState(prev => ({ ...prev, error: errorMessage }));
      return null;
    }

    // Update file previews to show validation results
    setFilePreviews(prev => {
      const updated = [...prev];
      
      // Mark invalid files
      invalidFiles.forEach(({ file }) => {
        const index = updated.findIndex(fp => fp.file === file);
        if (index !== -1) {
          updated[index] = { ...updated[index], status: 'invalid', error: invalidFiles.find(f => f.file === file)?.error };
        }
      });

      // Mark valid files as uploading
      validFiles.forEach(file => {
        const index = updated.findIndex(fp => fp.file === file);
        if (index !== -1) {
          updated[index] = { ...updated[index], status: 'uploading', progress: 0 };
        }
      });

      return updated;
    });

    try {
      setState({ isUploading: true, error: null });
      const response = await uploadFiles(validFiles);
      
      // Update file previews with results
      setFilePreviews(prev => {
        const updated = [...prev];
        
        response.results.forEach(result => {
          const index = updated.findIndex(fp => fp.file.name === result.filename);
          if (index !== -1) {
            updated[index] = {
              ...updated[index],
              status: result.status,
              error: result.error_message || undefined,
              progress: result.status === 'success' ? 100 : 0,
            };
          }
        });

        return updated;
      });

      setState({ isUploading: false, error: null });
      return response;
    } catch (error) {
      let errorMessage = 'Failed to upload files. Please try again.';
      
      if (error instanceof Error) {
        if (error.message.includes('Network Error')) {
          errorMessage = 'Network error. Please check your connection and try again.';
        } else if (error.message.includes('timeout')) {
          errorMessage = 'Upload timed out. Please try again with smaller files.';
        } else {
          errorMessage = error.message;
        }
      }
      
      // Mark all uploading files as error
      setFilePreviews(prev => 
        prev.map(fp => 
          fp.status === 'uploading' 
            ? { ...fp, status: 'error', error: errorMessage }
            : fp
        )
      );
      
      setState({ isUploading: false, error: errorMessage });
      return null;
    }
  }, []);

  const uploadFileHandler = useCallback(async (file: File): Promise<FileUploadResponse | null> => {
    // Validate file first
    const validation = validateFile(file);
    if (!validation.isValid) {
      setState(prev => ({ ...prev, error: validation.error || 'Invalid file' }));
      return null;
    }

    try {
      setState({ isUploading: true, error: null });
      const response = await uploadFile(file);
      setState({ isUploading: false, error: null });
      return response;
    } catch (error) {
      let errorMessage = 'Failed to upload file. Please try again.';
      
      if (error instanceof Error) {
        if (error.message.includes('Network Error')) {
          errorMessage = 'Network error. Please check your connection and try again.';
        } else if (error.message.includes('timeout')) {
          errorMessage = 'Upload timed out. Please try again with a smaller file.';
        } else {
          errorMessage = error.message;
        }
      }
      
      setState({ isUploading: false, error: errorMessage });
      return null;
    }
  }, []);

  const addFilePreviews = useCallback((files: File[]) => {
    const newPreviews: FilePreview[] = files.map(file => ({
      id: `${file.name}-${file.size}-${file.lastModified}`,
      file,
      status: 'pending',
    }));
    
    setFilePreviews(prev => {
      // Filter out duplicates
      const existingIds = new Set(prev.map(fp => fp.id));
      const uniqueNewPreviews = newPreviews.filter(fp => !existingIds.has(fp.id));
      return [...prev, ...uniqueNewPreviews];
    });
  }, []);

  const removeFilePreview = useCallback((id: string) => {
    setFilePreviews(prev => prev.filter(fp => fp.id !== id));
  }, []);

  const clearFilePreviews = useCallback(() => {
    setFilePreviews([]);
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    filePreviews,
    uploadFiles: uploadFilesHandler,
    uploadFile: uploadFileHandler,
    addFilePreviews,
    removeFilePreview,
    clearFilePreviews,
    clearError,
  };
}; 