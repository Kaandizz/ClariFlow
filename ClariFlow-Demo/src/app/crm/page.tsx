import CRMSyncStatus from '@/components/crm/CRMSyncStatus';
import Head from 'next/head';

export default function CRMPage() {
  return (
    <>
      <Head>
        <title>CRM Integration | ClariFlow</title>
        <meta name="description" content="Manage your CRM connections and sync data across platforms." />
      </Head>
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="w-full max-w-2xl p-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
          <h1 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">CRM Integration</h1>
          <CRMSyncStatus />
        </div>
      </div>
    </>
  );
} 