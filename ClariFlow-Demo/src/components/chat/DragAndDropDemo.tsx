"use client";

import { useState } from 'react';
import { DocumentArrowUpIcon, InformationCircleIcon } from '@heroicons/react/24/outline';

interface DragAndDropDemoProps {
  onClose: () => void;
}

export default function DragAndDropDemo({ onClose }: DragAndDropDemoProps) {
  const [isVisible, setIsVisible] = useState(true);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(onClose, 300);
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center">
            <DocumentArrowUpIcon className="h-5 w-5 mr-2 text-indigo-500" />
            Drag & Drop File Upload
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="space-y-4">
          <div className="bg-indigo-50 rounded-lg p-4">
            <div className="flex items-start">
              <InformationCircleIcon className="h-5 w-5 text-indigo-500 mt-0.5 mr-2 flex-shrink-0" />
              <div className="text-sm text-indigo-700">
                <p className="font-medium mb-1">How to use:</p>
                <ul className="space-y-1">
                  <li>• Drag any file from your computer onto the chat area</li>
                  <li>• Drop the file anywhere on the chat window</li>
                  <li>• The file will be automatically uploaded and processed</li>
                </ul>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-medium text-gray-900 mb-2">Supported File Types:</h3>
            <div className="grid grid-cols-1 gap-2 text-sm text-gray-600">
              <div className="flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                PDF files (.pdf)
              </div>
              <div className="flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                Text files (.txt)
              </div>
              <div className="flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                Word documents (.docx)
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-medium text-gray-900 mb-2">Limitations:</h3>
            <div className="text-sm text-gray-600 space-y-1">
              <p>• Maximum file size: 10MB</p>
              <p>• One file at a time</p>
              <p>• Files are processed for embeddings</p>
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500">
              💡 <strong>Tip:</strong> You can also use the file upload button in the chat input area for the same functionality.
            </p>
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={handleClose}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            Got it!
          </button>
        </div>
      </div>
    </div>
  );
} 