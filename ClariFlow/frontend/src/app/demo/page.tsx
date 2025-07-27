"use client";

import Chat from '@/components/chat/Chat';
import MainLayout from '@/components/layout/MainLayout';

export default function DemoPage() {
  return (
    <MainLayout>
      <div className="h-full">
        <Chat />
      </div>
    </MainLayout>
  );
} 