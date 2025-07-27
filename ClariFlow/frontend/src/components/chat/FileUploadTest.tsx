"use client";

import { useState } from 'react';
import { useFileUpload, validateFile, formatFileSize } from '@/hooks/useFileUpload';

export default function FileUploadTest() {
  const [testFile, setTestFile] = useState<File | null>(null);
  const { isUploading, uploadFile, error, clearError } = useFileUpload();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setTestFile(file);
      clearError();
    }
  };

  const handleTestUpload = async () => {
    if (testFile) {
      const result = await uploadFile(testFile);
      console.log('Upload result:', result);
    }
  };

  const handleTestValidation = () => {
    if (testFile) {
      const validation = validateFile(testFile);
      console.log('Validation result:', validation);
      alert(validation.isValid ? 'File is valid!' : `Error: ${validation.error}`);
    }
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">File Upload Test</h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select a file to test:
          </label>
          <input
            type="file"
            onChange={handleFileChange}
            accept=".pdf,.txt,.docx"
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
          />
        </div>

        {testFile && (
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-sm">
              <strong>File:</strong> {testFile.name}
            </p>
            <p className="text-sm">
              <strong>Size:</strong> {formatFileSize(testFile.size)}
            </p>
            <p className="text-sm">
              <strong>Type:</strong> {testFile.type}
            </p>
          </div>
        )}

        <div className="flex space-x-2">
          <button
            onClick={handleTestValidation}
            disabled={!testFile}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            Test Validation
          </button>
          
          <button
            onClick={handleTestUpload}
            disabled={!testFile || isUploading}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
          >
            {isUploading ? 'Uploading...' : 'Test Upload'}
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}
      </div>
    </div>
  );
} 