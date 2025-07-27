"use client";

import React, { useState, useEffect } from 'react';
import { FileText, MessageSquare, TrendingUp, CheckSquare, Plus, Search, Clock, Users, BarChart3, Calendar, Lightbulb } from 'lucide-react';
import Card, { CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import SkeletonLoader from '@/components/ui/SkeletonLoader';
import { toast } from 'react-hot-toast';
import Link from 'next/link';
import { getAvailableDocuments, getChatSessions, getTasks, getDataSources } from '@/lib/api';

const Dashboard: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');

  // Documents widget state
  const [documents, setDocuments] = useState<any[]>([]);
  const [documentsLoading, setDocumentsLoading] = useState(true);
  const [documentsError, setDocumentsError] = useState<string | null>(null);

  // Chat widget state
  const [chatSessions, setChatSessions] = useState<any[]>([]);
  const [chatsLoading, setChatsLoading] = useState(true);
  const [chatsError, setChatsError] = useState<string | null>(null);

  // Insights widget state
  const [insights, setInsights] = useState<any[]>([]);
  const [insightsLoading, setInsightsLoading] = useState(true);
  const [insightsError, setInsightsError] = useState<string | null>(null);

  // Tasks widget state
  const [tasks, setTasks] = useState<any[]>([]);
  const [tasksLoading, setTasksLoading] = useState(true);
  const [tasksError, setTasksError] = useState<string | null>(null);

  // Fetch Documents
  const fetchDocuments = () => {
    setDocumentsLoading(true);
    setDocumentsError(null);
    getAvailableDocuments()
      .then(res => setDocuments(res.documents))
      .catch(() => setDocumentsError('Failed to load documents.'))
      .finally(() => setDocumentsLoading(false));
  };
  useEffect(fetchDocuments, []);

  // Fetch Chat Sessions
  const fetchChats = () => {
    setChatsLoading(true);
    setChatsError(null);
    getChatSessions()
      .then(setChatSessions)
      .catch(() => setChatsError('Failed to load chat sessions.'))
      .finally(() => setChatsLoading(false));
  };
  useEffect(fetchChats, []);

  // Fetch Insights (placeholder)
  const fetchInsights = () => {
    setInsightsLoading(true);
    setInsightsError(null);
    setInsights([]); // No real insights yet
    setInsightsLoading(false);
  };
  useEffect(fetchInsights, []);

  // Fetch Tasks
  const fetchTasks = () => {
    setTasksLoading(true);
    setTasksError(null);
    getTasks(1, 4)
      .then(res => setTasks(res.tasks))
      .catch(() => setTasksError('Failed to load tasks.'))
      .finally(() => setTasksLoading(false));
  };
  useEffect(fetchTasks, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processed':
      case 'completed':
        return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/20';
      case 'processing':
      case 'in_progress':
        return 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/20';
      case 'pending':
        return 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/20';
      default:
        return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900/20';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/20';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/20';
      case 'low':
        return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/20';
      default:
        return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900/20';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Overview of your documents, chats, insights, and tasks
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Documents Card */}
        <Card hoverable>
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Documents</p>
              {documentsLoading ? (
                <SkeletonLoader variant="text" className="h-8 w-16" />
              ) : documentsError ? (
                <div className="flex flex-col items-start">
                  <span className="text-red-600 dark:text-red-400 text-xs mb-1">{documentsError}</span>
                  <Button size="sm" onClick={fetchDocuments}>Retry</Button>
                </div>
              ) : (
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{documents.length}</p>
              )}
            </div>
            <div className="p-3 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
              <FileText className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
          </CardContent>
        </Card>
        {/* Chat Sessions Card */}
        <Card hoverable>
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Chat Sessions</p>
              {chatsLoading ? (
                <SkeletonLoader variant="text" className="h-8 w-16" />
              ) : chatsError ? (
                <div className="flex flex-col items-start">
                  <span className="text-red-600 dark:text-red-400 text-xs mb-1">{chatsError}</span>
                  <Button size="sm" onClick={fetchChats}>Retry</Button>
                </div>
              ) : (
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{chatSessions.length}</p>
              )}
            </div>
            <div className="p-3 bg-green-100 dark:bg-green-900/20 rounded-lg">
              <MessageSquare className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
          </CardContent>
        </Card>
        {/* Insights Card */}
        <Card hoverable>
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Insights</p>
              {insightsLoading ? (
                <SkeletonLoader variant="text" className="h-8 w-16" />
              ) : insightsError ? (
                <div className="flex flex-col items-start">
                  <span className="text-red-600 dark:text-red-400 text-xs mb-1">{insightsError}</span>
                  <Button size="sm" onClick={fetchInsights}>Retry</Button>
                </div>
              ) : (
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{insights.length}</p>
              )}
            </div>
            <div className="p-3 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
              <TrendingUp className="h-6 w-6 text-purple-600 dark:text-purple-400" />
            </div>
          </CardContent>
        </Card>
        {/* Tasks Card */}
        <Card hoverable>
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Tasks</p>
              {tasksLoading ? (
                <SkeletonLoader variant="text" className="h-8 w-16" />
              ) : tasksError ? (
                <div className="flex flex-col items-start">
                  <span className="text-red-600 dark:text-red-400 text-xs mb-1">{tasksError}</span>
                  <Button size="sm" onClick={fetchTasks}>Retry</Button>
                </div>
              ) : (
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{tasks.filter(t => t.status !== 'completed').length}</p>
              )}
            </div>
            <div className="p-3 bg-orange-100 dark:bg-orange-900/20 rounded-lg">
              <CheckSquare className="h-6 w-6 text-orange-600 dark:text-orange-400" />
            </div>
          </CardContent>
        </Card>
      </div>
      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Documents */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Recent Documents
              </CardTitle>
              <Link href="/documents">
                <Button variant="ghost" size="sm">View All</Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            {documentsLoading ? (
              <SkeletonLoader variant="card" className="h-32" />
            ) : documentsError ? (
              <div className="flex flex-col items-center py-8">
                <span className="text-red-600 dark:text-red-400 mb-2">{documentsError}</span>
                <Button onClick={fetchDocuments}>Retry</Button>
              </div>
            ) : (
            <div className="space-y-3">
                {documents.map((doc) => (
                <div key={doc.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <FileText className="h-4 w-4 text-gray-500" />
                    <div>
                        <p className="font-medium text-gray-900 dark:text-white text-sm">{doc.filename}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{formatDate(doc.upload_date)}</p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(doc.status)}`}>
                    {doc.status}
                  </span>
                </div>
              ))}
            </div>
            )}
          </CardContent>
        </Card>
        {/* Recent Chat Sessions */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Recent Chats
              </CardTitle>
              <Link href="/chat">
                <Button variant="ghost" size="sm">View All</Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            {chatsLoading ? (
              <SkeletonLoader variant="card" className="h-32" />
            ) : chatsError ? (
              <div className="flex flex-col items-center py-8">
                <span className="text-red-600 dark:text-red-400 mb-2">{chatsError}</span>
                <Button onClick={fetchChats}>Retry</Button>
              </div>
            ) : (
            <div className="space-y-3">
                {chatSessions.map((session) => (
                <div key={session.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <MessageSquare className="h-4 w-4 text-gray-500" />
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white text-sm">{session.title}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                          {session.message_count || 0} messages • {formatDate(session.updated_at || session.created_at)}
                      </p>
                    </div>
                  </div>
                  <Clock className="h-4 w-4 text-gray-400" />
                </div>
              ))}
            </div>
            )}
          </CardContent>
        </Card>
        {/* Recent Insights */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Recent Insights
              </CardTitle>
              <Link href="/insights">
                <Button variant="ghost" size="sm">Generate Insight</Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            {insightsLoading ? (
              <SkeletonLoader variant="card" className="h-32" />
            ) : insightsError ? (
              <div className="flex flex-col items-center py-8">
                <span className="text-red-600 dark:text-red-400 mb-2">{insightsError}</span>
                <Button onClick={fetchInsights}>Retry</Button>
                  </div>
            ) : insights.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8">
                <Lightbulb className="h-12 w-12 text-blue-400 mb-4" />
                <p className="text-gray-600 dark:text-gray-400 mb-2 text-center">
                  No insights yet — generate insights from your data sources to see them here.
                </p>
                <Link href="/insights">
                  <Button variant="primary">Generate Insight</Button>
                </Link>
                </div>
            ) : (
              <div className="space-y-3">
                {/* When real insights are available, map and display them here */}
            </div>
            )}
          </CardContent>
        </Card>
        {/* Active Tasks */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <CheckSquare className="h-5 w-5" />
                Active Tasks
              </CardTitle>
              <Link href="/tasks">
                <Button variant="ghost" size="sm">View All</Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            {tasksLoading ? (
              <SkeletonLoader variant="card" className="h-32" />
            ) : tasksError ? (
              <div className="flex flex-col items-center py-8">
                <span className="text-red-600 dark:text-red-400 mb-2">{tasksError}</span>
                <Button onClick={fetchTasks}>Retry</Button>
              </div>
            ) : (
            <div className="space-y-3">
                {tasks.filter(t => t.status !== 'completed').map((task) => (
                <div key={task.id} className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <p className="font-medium text-gray-900 dark:text-white text-sm">{task.title}</p>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(task.priority)}`}>
                      {task.priority}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                      <Users className="h-3 w-3" />
                      {task.assignee}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                        {formatDate(task.due_date)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard; 