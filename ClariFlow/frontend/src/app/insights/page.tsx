import InsightsChatExtension from '@/components/insights/InsightsChatExtension';
import Head from 'next/head';

export default function InsightsPage() {
  return (
    <>
      <Head>
        <title>Business Insights | ClariFlow</title>
        <meta name="description" content="Analyze your data and generate actionable business insights using AI." />
      </Head>
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="w-full max-w-2xl p-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
          <h1 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Business Insights</h1>
          <InsightsChatExtension />
        </div>
      </div>
    </>
  );
} 