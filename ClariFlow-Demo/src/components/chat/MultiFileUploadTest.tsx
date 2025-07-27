"use client";

import { useState } from 'react';
import { useFileUpload } from '@/hooks/useFileUpload';
import FileDropZone from './FileDropZone';
import FilePreview from './FilePreview';
import DragAndDropWrapper from './DragAndDropWrapper';

export default function MultiFileUploadTest() {
  const { 
    isUploading, 
    uploadFiles, 
    error, 
    filePreviews, 
    addFilePreviews, 
    removeFilePreview,
    clearFilePreviews 
  } = useFileUpload();

  const [uploadResults, setUploadResults] = useState<any>(null);

  const handleFilesSelect = async (files: File[]) => {
    console.log('Selected files:', files.map(f => f.name));
    addFilePreviews(files);
  };

  const handleFilesDrop = async (files: File[]) => {
    console.log('Dropped files:', files.map(f => f.name));
    addFilePreviews(files);
  };

  const handleUpload = async () => {
    const files = filePreviews
      .filter(fp => fp.status === 'pending' || fp.status === 'valid')
      .map(fp => fp.file);

    if (files.length === 0) {
      alert('No files to upload');
      return;
    }

    console.log('Uploading files:', files.map(f => f.name));
    const result = await uploadFiles(files);
    setUploadResults(result);
  };

  const pendingFiles = filePreviews.filter(fp => fp.status === 'pending' || fp.status === 'valid');
  const hasPendingFiles = pendingFiles.length > 0;

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Multi-File Upload Test
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Test the new multi-file upload functionality
        </p>
      </div>

      <DragAndDropWrapper onFilesDrop={handleFilesDrop}>
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              File Upload
            </h2>
            <div className="flex items-center space-x-2">
              <FileDropZone
                onFilesSelect={handleFilesSelect}
                isUploading={isUploading}
                showPreviews={false}
              />
              {hasPendingFiles && (
                <button
                  onClick={handleUpload}
                  disabled={isUploading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isUploading ? 'Uploading...' : 'Upload Files'}
                </button>
              )}
              {filePreviews.length > 0 && (
                <button
                  onClick={clearFilePreviews}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                >
                  Clear All
                </button>
              )}
            </div>
          </div>

          {/* File Previews */}
          {filePreviews.length > 0 && (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {filePreviews.map((filePreview) => (
                <FilePreview
                  key={filePreview.id}
                  filePreview={filePreview}
                  onRemove={removeFilePreview}
                />
              ))}
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="mt-4 p-3 bg-red-100 dark:bg-red-900/20 border border-red-300 dark:border-red-700 rounded-lg">
              <p className="text-red-700 dark:text-red-400 text-sm">{error}</p>
            </div>
          )}

          {/* Upload Results */}
          {uploadResults && (
            <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                Upload Results
              </h3>
              <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <p><strong>Message:</strong> {uploadResults.message}</p>
                <p><strong>Total Files:</strong> {uploadResults.total_files}</p>
                <p><strong>Successful:</strong> {uploadResults.successful_uploads}</p>
                <p><strong>Failed:</strong> {uploadResults.failed_uploads}</p>
              </div>
              
              <div className="mt-3 space-y-2">
                {uploadResults.results.map((result: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-white dark:bg-gray-800 rounded border">
                    <span className="text-sm font-medium">{result.filename}</span>
                    <span className={`text-xs px-2 py-1 rounded ${
                      result.status === 'success' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                        : 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
                    }`}>
                      {result.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </DragAndDropWrapper>

      {/* Instructions */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
          How to Test
        </h3>
        <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
          <li>• Click the paperclip icon to select multiple files</li>
          <li>• Drag and drop multiple files onto the upload area</li>
          <li>• Files will be validated for type (PDF, TXT, DOCX) and size (≤10MB)</li>
          <li>• Invalid files will be marked with errors</li>
          <li>• Click "Upload Files" to process valid files</li>
          <li>• View real-time status updates for each file</li>
        </ul>
      </div>
    </div>
  );
} 