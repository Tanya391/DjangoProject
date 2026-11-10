import React, { useEffect } from 'react';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { useUIStore } from '../store/useUIStore';

export function AppShell({ children }) {
  const { isSidebarOpen, theme } = useUIStore();

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#0b0f19] text-slate-900 dark:text-slate-100 flex transition-colors duration-200">
      <Sidebar />
      <div
        className={`flex-1 transition-all duration-300 flex flex-col min-w-0 ${
          isSidebarOpen ? 'ml-64' : 'ml-20'
        }`}
      >
        <Topbar />
        <main className="p-6 md:p-8 flex-1 max-w-7xl w-full mx-auto space-y-8">{children}</main>
      </div>
    </div>
  );
}
