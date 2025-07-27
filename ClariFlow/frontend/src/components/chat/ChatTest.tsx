"use client";

import { useState } from 'react';
import { sendChatMessage } from '@/lib/api';
import type { ChatResponse } from '@/lib/api';

export default function ChatTest() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const testQueries = [
    "What is the capital of France?",
    "Explain quantum computing in simple terms",
    "Write a short poem about technology",
    "What is machine learning?",
    "Tell me a joke"
  ];

  const handleTest = async (testQuery: string) => {
    setQuery(testQuery);
    setResponse(null);
    setError(null);
    setIsLoading(true);

    try {
      const result = await sendChatMessage({ query: testQuery });
      setResponse(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCustomTest = async () => {
    if (!query.trim()) return;
    await handleTest(query);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          ClariFlow Chat Test
        </h2>
        
        {/* Custom query input */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Custom Query:
          </label>
          <div className="flex space-x-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your query..."
              className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button
              onClick={handleCustomTest}
              disabled={!query.trim() || isLoading}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Test
            </button>
          </div>
        </div>

        {/* Quick test buttons */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Quick Tests:
          </label>
          <div className="flex flex-wrap gap-2">
            {testQueries.map((testQuery, index) => (
              <button
                key={index}
                onClick={() => handleTest(testQuery)}
                disabled={isLoading}
                className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50"
              >
                {testQuery}
              </button>
            ))}
          </div>
        </div>

        {/* Loading state */}
        {isLoading && (
          <div className="flex items-center justify-center p-8">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
            <span className="ml-2 text-gray-600 dark:text-gray-400">Testing...</span>
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <h3 className="text-sm font-medium text-red-800 dark:text-red-200">Error</h3>
            <p className="text-sm text-red-700 dark:text-red-300 mt-1">{error}</p>
          </div>
        )}

        {/* Response */}
        {response && (
          <div className="space-y-4">
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-2">Query:</h3>
              <p className="text-gray-700 dark:text-gray-300">{query}</p>
            </div>
            
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-gray-900 dark:text-white">Response:</h3>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    response.source === 'document' 
                      ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                      : 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                  }`}>
                    {response.source === 'document' ? '📄 Document' : '🤖 OpenAI'}
                  </span>
                  {response.document_id && (
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      ID: {response.document_id}
                    </span>
                  )}
                </div>
              </div>
              <div className="prose prose-sm max-w-none">
                <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{response.response}</p>
              </div>
              
              {response.sources && response.sources.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <h4 className="text-xs font-medium text-gray-900 dark:text-white mb-2">Sources:</h4>
                  <div className="space-y-2">
                    {response.sources.map((source, index) => (
                      <div key={index} className="text-xs text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 p-2 rounded">
                        {source.substring(0, 200)}...
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Timestamp: {new Date(response.timestamp).toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 