import CompositionPanel from '@/components/composition/CompositionPanel';
import Head from 'next/head';

export default function ComposePage() {
  return (
    <>
      <Head>
        <title>Compose | ClariFlow</title>
        <meta name="description" content="Generate and edit content with AI composition tools." />
      </Head>
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="w-full max-w-2xl p-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
          <h1 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">AI Composition</h1>
          <CompositionPanel isOpen={true} onClose={() => {}} />
        </div>
      </div>
    </>
  );
} 