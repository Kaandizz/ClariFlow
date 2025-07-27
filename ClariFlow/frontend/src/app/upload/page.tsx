import { FileUploadProvider } from '@/contexts/FileUploadContext';
import FileUploadProgress from '@/components/ui/FileUploadProgress';
import Head from 'next/head';

export default function UploadPage() {
  return (
    <>
      <Head>
        <title>Upload Documents | ClariFlow</title>
        <meta name="description" content="Upload your documents to ClariFlow for AI-powered chat and search." />
      </Head>
      <FileUploadProvider>
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900">
          <div className="w-full max-w-2xl p-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
            <h1 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Upload Documents</h1>
            {/* Place your drag-and-drop or upload UI here */}
            <FileUploadProgress />
          </div>
        </div>
      </FileUploadProvider>
    </>
  );
} 