import Head from 'next/head';

export default function LeadsPage() {
  return (
    <>
      <Head>
        <title>Leads | ClariFlow</title>
        <meta name="description" content="Manage your leads and track progress." />
      </Head>
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="w-full max-w-2xl p-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
          <h1 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Leads Management</h1>
          <p className="text-gray-600 dark:text-gray-400">Leads management UI coming soon.</p>
        </div>
      </div>
    </>
  );
} 