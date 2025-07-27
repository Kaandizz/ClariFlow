"use client";

import { useState } from 'react';
import { ArrowUpTrayIcon } from '@heroicons/react/24/outline';

interface DragHintProps {
  className?: string;
}

export default function DragHint({ className }: DragHintProps) {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div 
      className={`absolute bottom-20 right-4 transition-all duration-300 ${
        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
      } ${className}`}
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      <div className="flex items-center gap-2 bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-700 rounded-lg px-3 py-2 shadow-lg">
        <ArrowUpTrayIcon className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
        <span className="text-xs text-indigo-700 dark:text-indigo-300 font-medium">
          Drop files anywhere to upload
        </span>
      </div>
      {/* Arrow pointing down */}
      <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-indigo-200 dark:border-t-indigo-700"></div>
    </div>
  );
} 