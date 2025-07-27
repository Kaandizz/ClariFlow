"use client";

interface CompositionPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CompositionPanel({ isOpen, onClose }: CompositionPanelProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 shadow-xl">
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">AI Composer</h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
        >
          ✕
        </button>
      </div>
      <div className="p-4">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Email and proposal composition features coming soon.
        </p>
      </div>
    </div>
  );
} 