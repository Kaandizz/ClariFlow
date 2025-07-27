"use client";

import React from 'react';
import { X, CheckCircle, AlertCircle, FileText, Upload } from 'lucide-react';
import { useFileUploadContext } from '@/contexts/FileUploadContext';
import Card from './Card';
import Button from './Button';

const FileUploadProgress: React.FC = () => {
  const { uploadProgress, isUploading, clearUploadProgress } = useFileUploadContext();

  if (uploadProgress.length === 0) {
    return null;
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'uploading':
        return <Upload className="h-4 w-4 text-blue-500 animate-bounce" />;
      default:
        return <FileText className="h-4 w-4 text-gray-500" />;
    }
  };

  const getProgressBarColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      case 'uploading':
        return 'bg-blue-500';
      default:
        return 'bg-gray-300';
    }
  };

  return (
    <Card className="fixed bottom-4 right-4 w-80 z-50 shadow-lg">
      <div className="p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white">
            File Upload Progress
          </h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={clearUploadProgress}
            disabled={isUploading}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
        
        <div className="space-y-3">
          {uploadProgress.map((file, index) => (
            <div key={index} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  {getStatusIcon(file.status)}
                  <span className="text-sm text-gray-700 dark:text-gray-300 truncate">
                    {file.fileName}
                  </span>
                </div>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {file.progress}%
                </span>
              </div>
              
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${getProgressBarColor(file.status)}`}
                  style={{ width: `${file.progress}%` }}
                />
              </div>
              
              {file.error && (
                <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                  {file.error}
                </p>
              )}
            </div>
          ))}
        </div>
        
        {isUploading && (
          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <p className="text-xs text-gray-600 dark:text-gray-400">
              Uploading files... Please don't close the window.
            </p>
          </div>
        )}
      </div>
    </Card>
  );
};

export default FileUploadProgress; 