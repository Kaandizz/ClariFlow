"use client";

import { useState } from 'react';
import { 
  XMarkIcon, 
  CheckCircleIcon, 
  ExclamationTriangleIcon,
  DocumentIcon,
  ArrowUpTrayIcon
} from '@heroicons/react/24/outline';
import { type FilePreview as FilePreviewType } from '@/hooks/useFileUpload';
import { formatFileSize } from '@/hooks/useFileUpload';

interface FilePreviewProps {
  filePreview: FilePreviewType;
  onRemove: (id: string) => void;
}

export default function FilePreview({ filePreview, onRemove }: FilePreviewProps) {
  const { id, file, status, error, progress } = filePreview;

  const getStatusIcon = () => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon className="h-4 w-4 text-green-500" />;
      case 'error':
      case 'invalid':
        return <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />;
      case 'uploading':
        return <ArrowUpTrayIcon className="h-4 w-4 text-blue-500 animate-pulse" />;
      default:
        return <DocumentIcon className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'valid':
        return 'Valid';
      case 'invalid':
        return 'Invalid';
      case 'uploading':
        return 'Uploading...';
      case 'success':
        return 'Uploaded';
      case 'error':
        return 'Failed';
      default:
        return 'Unknown';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'success':
        return 'text-green-600 dark:text-green-400';
      case 'error':
      case 'invalid':
        return 'text-red-600 dark:text-red-400';
      case 'uploading':
        return 'text-blue-600 dark:text-blue-400';
      default:
        return 'text-gray-500 dark:text-gray-400';
    }
  };

  const getFileTypeIcon = () => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'pdf':
        return '📄';
      case 'docx':
        return '📝';
      case 'txt':
        return '📄';
      default:
        return '📄';
    }
  };

  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="flex items-center space-x-3 flex-1 min-w-0">
        {/* File type icon */}
        <div className="flex-shrink-0 text-lg">
          {getFileTypeIcon()}
        </div>

        {/* File info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2">
            <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
              {file.name}
            </p>
            {getStatusIcon()}
          </div>
          
          <div className="flex items-center justify-between mt-1">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {formatFileSize(file.size)}
            </p>
            <p className={`text-xs font-medium ${getStatusColor()}`}>
              {getStatusText()}
            </p>
          </div>

          {/* Error message */}
          {error && (
            <p className="text-xs text-red-600 dark:text-red-400 mt-1 truncate">
              {error}
            </p>
          )}

          {/* Progress bar for uploading files */}
          {status === 'uploading' && (
            <div className="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1">
              <div 
                className="bg-blue-600 h-1 rounded-full transition-all duration-300"
                style={{ width: `${progress || 0}%` }}
              />
            </div>
          )}
        </div>
      </div>

      {/* Remove button */}
      <button
        onClick={() => onRemove(id)}
        className="flex-shrink-0 ml-2 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
        title="Remove file"
      >
        <XMarkIcon className="h-4 w-4" />
      </button>
    </div>
  );
} 