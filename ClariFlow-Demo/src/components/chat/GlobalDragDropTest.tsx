"use client";

import { useState } from 'react';
import { useFileUpload } from '@/hooks/useFileUpload';
import DragAndDropWrapper from './DragAndDropWrapper';
import FilePreview from './FilePreview';
import DragHint from './DragHint';

export default function GlobalDragDropTest() {
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

  const handleFilesDrop = async (files: File[]) => {
    console.log('Files dropped globally:', files.map(f => f.name));
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
    <DragAndDropWrapper onFilesDrop={handleFilesDrop}>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-4xl mx-auto p-6 space-y-6">
          {/* Header */}
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Global Drag & Drop Test
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Try dragging files anywhere on this page - the entire window is a drop zone!
            </p>
          </div>

          {/* Test Areas */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left Column */}
            <div className="space-y-4">
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Test Area 1
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  This is a test area. You can drop files anywhere on this page, including this area.
                </p>
                <div className="h-32 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Drop zone area
                  </p>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Test Area 2
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Another test area. The entire page is a drop zone, so you can drop files here too.
                </p>
              </div>
            </div>

            {/* Right Column */}
            <div className="space-y-4">
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Upload Controls
                </h2>
                <div className="space-y-3">
                  {hasPendingFiles && (
                    <button
                      onClick={handleUpload}
                      disabled={isUploading}
                      className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isUploading ? 'Uploading...' : 'Upload Files'}
                    </button>
                  )}
                  {filePreviews.length > 0 && (
                    <button
                      onClick={clearFilePreviews}
                      className="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                    >
                      Clear All Files
                    </button>
                  )}
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Instructions
                </h2>
                <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-2">
                  <li>• Drag files from your computer anywhere on this page</li>
                  <li>• The entire window is a drop zone</li>
                  <li>• Supported: PDF, TXT, DOCX (max 10MB each)</li>
                  <li>• Invalid files will show error messages</li>
                  <li>• Hover near the bottom to see the drag hint</li>
                </ul>
              </div>
            </div>
          </div>

          {/* File Previews */}
          {filePreviews.length > 0 && (
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Selected Files ({filePreviews.length})
              </h2>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {filePreviews.map((filePreview) => (
                  <FilePreview
                    key={filePreview.id}
                    filePreview={filePreview}
                    onRemove={removeFilePreview}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg p-4">
              <p className="text-red-700 dark:text-red-400 text-sm">{error}</p>
            </div>
          )}

          {/* Upload Results */}
          {uploadResults && (
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Upload Results
              </h2>
              <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <p><strong>Message:</strong> {uploadResults.message}</p>
                <p><strong>Total Files:</strong> {uploadResults.total_files}</p>
                <p><strong>Successful:</strong> {uploadResults.successful_uploads}</p>
                <p><strong>Failed:</strong> {uploadResults.failed_uploads}</p>
              </div>
              
              <div className="mt-4 space-y-2">
                {uploadResults.results.map((result: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded border">
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

          {/* Drag Hint */}
          <div className="relative h-20">
            <DragHint />
          </div>
        </div>
      </div>
    </DragAndDropWrapper>
  );
} 