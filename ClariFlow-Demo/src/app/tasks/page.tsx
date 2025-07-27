import MeetingSummaryModal from '@/components/tasks/MeetingSummaryModal';
import Head from 'next/head';
import { useState } from 'react';

export default function TasksPage() {
  const [showMeetingModal, setShowMeetingModal] = useState(false);
  return (
    <>
      <Head>
        <title>Tasks | ClariFlow</title>
        <meta name="description" content="Extract actionable tasks from meetings and manage your workflow." />
      </Head>
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="w-full max-w-2xl p-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
          <h1 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Task Management</h1>
          <button
            onClick={() => setShowMeetingModal(true)}
            className="w-full sm:w-auto px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors mb-4"
          >
            Extract Tasks from Meeting
          </button>
          <MeetingSummaryModal isOpen={showMeetingModal} onClose={() => setShowMeetingModal(false)} onTasksExtracted={() => setShowMeetingModal(false)} />
        </div>
      </div>
    </>
  );
} 