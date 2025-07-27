"use client";

import { 
  HomeIcon,
  ChatBubbleLeftRightIcon, 
  ChartBarIcon, 
  ClipboardDocumentListIcon, 
  UserGroupIcon,
  Cog6ToothIcon,
  DocumentTextIcon,
  PencilSquareIcon
} from '@heroicons/react/24/outline';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navigation = [
  { name: 'Dashboard', href: 'dashboard', icon: HomeIcon },
  { name: 'Chat', href: 'chat', icon: ChatBubbleLeftRightIcon },
  { name: 'Documents', href: 'documents', icon: DocumentTextIcon },
  { name: 'Insights', href: 'insights', icon: ChartBarIcon },
  { name: 'Tasks', href: 'tasks', icon: ClipboardDocumentListIcon },
  { name: 'Composition', href: 'composition', icon: PencilSquareIcon },
  { name: 'CRM', href: 'crm', icon: UserGroupIcon },
  { name: 'Settings', href: 'settings', icon: Cog6ToothIcon },
];

export default function Sidebar() {
  const pathname = usePathname();
  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
      {/* Logo */}
      <div className="flex items-center justify-center h-16 px-4 border-b border-gray-200 dark:border-gray-700">
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">ClariFlow</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`group w-full flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 ${
                isActive
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/25'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700/50 hover:shadow-sm hover:scale-[1.02]'
              }`}
            >
              <item.icon className={`mr-3 h-5 w-5 transition-colors ${
                isActive ? 'text-white' : 'text-gray-500 group-hover:text-gray-700 dark:group-hover:text-gray-300'
              }`} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
          ClariFlow v2.0.0
        </div>
      </div>
    </div>
  );
} 