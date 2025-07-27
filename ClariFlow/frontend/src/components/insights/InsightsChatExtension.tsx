"use client";

interface InsightsChatExtensionProps {
  onSendInsight?: (insight: any) => void;
}

export default function InsightsChatExtension({ onSendInsight }: InsightsChatExtensionProps) {
  return (
    <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
      <h3 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
        Business Insights
      </h3>
      <p className="text-xs text-blue-700 dark:text-blue-300">
        Ask me to analyze your data and generate business insights.
      </p>
    </div>
  );
} 