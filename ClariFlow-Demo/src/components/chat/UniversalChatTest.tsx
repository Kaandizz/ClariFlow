"use client";

import { useState } from 'react';
import { sendChatMessage } from '@/lib/api';
import type { ChatRequest } from '@/lib/api';

export default function UniversalChatTest() {
  const [query, setQuery] = useState('');
  const [history, setHistory] = useState<string[]>([]);
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleTest = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    setError('');

    try {
      const request: ChatRequest = {
        query: query.trim(),
        history: history,
      };

      const result = await sendChatMessage(request);
      setResponse(JSON.stringify(result, null, 2));
      
      // Update history for next test
      setHistory(prev => [...prev, query.trim(), result.response]);
      setQuery('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  const clearHistory = () => {
    setHistory([]);
    setResponse('');
    setError('');
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Universal Chat Test
        </h2>
        
        <div className="space-y-4">
          {/* History Display */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Conversation History ({history.length} messages)
            </h3>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 max-h-40 overflow-y-auto">
              {history.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400 text-sm">No conversation history yet</p>
              ) : (
                <div className="space-y-2">
                  {history.map((msg, index) => (
                    <div key={index} className="text-sm">
                      <span className="font-medium text-gray-700 dark:text-gray-300">
                        {index % 2 === 0 ? 'User' : 'AI'}:
                      </span>
                      <span className="text-gray-600 dark:text-gray-400 ml-2">
                        {msg.length > 100 ? `${msg.substring(0, 100)}...` : msg}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <button
              onClick={clearHistory}
              className="mt-2 text-sm text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
            >
              Clear History
            </button>
          </div>

          {/* Query Input */}
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Test Query
            </label>
            <textarea
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your test query here..."
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              rows={3}
              disabled={isLoading}
            />
          </div>

          {/* Test Button */}
          <button
            onClick={handleTest}
            disabled={!query.trim() || isLoading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors"
          >
            {isLoading ? 'Testing...' : 'Test Universal Chat'}
          </button>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
              <h3 className="text-sm font-medium text-red-800 dark:text-red-200">Error</h3>
              <p className="text-sm text-red-700 dark:text-red-300 mt-1">{error}</p>
            </div>
          )}

          {/* Response Display */}
          {response && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                API Response
              </h3>
              <pre className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 overflow-x-auto text-sm text-gray-800 dark:text-gray-200">
                {response}
              </pre>
            </div>
          )}
        </div>
      </div>

      {/* Test Examples */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Test Examples
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <h4 className="font-medium text-gray-700 dark:text-gray-300">General Questions</h4>
            <div className="space-y-1">
              <button
                onClick={() => setQuery("What is the capital of France?")}
                className="block w-full text-left text-sm text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300 p-2 rounded hover:bg-indigo-50 dark:hover:bg-indigo-900/20"
              >
                What is the capital of France?
              </button>
              <button
                onClick={() => setQuery("Explain quantum computing in simple terms")}
                className="block w-full text-left text-sm text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300 p-2 rounded hover:bg-indigo-50 dark:hover:bg-indigo-900/20"
              >
                Explain quantum computing in simple terms
              </button>
              <button
                onClick={() => setQuery("What are the benefits of exercise?")}
                className="block w-full text-left text-sm text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300 p-2 rounded hover:bg-indigo-50 dark:hover:bg-indigo-900/20"
              >
                What are the benefits of exercise?
              </button>
            </div>
          </div>
          
          <div className="space-y-2">
            <h4 className="font-medium text-gray-700 dark:text-gray-300">Conversation Flow</h4>
            <div className="space-y-1">
              <button
                onClick={() => setQuery("Tell me about machine learning")}
                className="block w-full text-left text-sm text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300 p-2 rounded hover:bg-indigo-50 dark:hover:bg-indigo-900/20"
              >
                Tell me about machine learning
              </button>
              <button
                onClick={() => setQuery("Can you elaborate on that?")}
                className="block w-full text-left text-sm text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300 p-2 rounded hover:bg-indigo-50 dark:hover:bg-indigo-900/20"
              >
                Can you elaborate on that?
              </button>
              <button
                onClick={() => setQuery("What are some practical applications?")}
                className="block w-full text-left text-sm text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300 p-2 rounded hover:bg-indigo-50 dark:hover:bg-indigo-900/20"
              >
                What are some practical applications?
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 