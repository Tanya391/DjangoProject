import React from 'react';
import { useLocation } from 'react-router-dom';
import { Sun, Moon, ShieldCheck } from 'lucide-react';
import { useStatus } from '../hooks/useAnalytics';
import { useAuthStore } from '../store/useAuthStore';
import { useUIStore } from '../store/useUIStore';

const PAGE_TITLES = {
  '/': 'Financial Overview Dashboard',
  '/transactions': 'Transactions Register',
  '/analytics': 'Deep Financial Analytics',
  '/data': 'Data Management & Demo Tools',
  '/chat': 'AI Financial Assistant',
  '/history': 'RAG Query History',
};

export function Topbar() {
  const location = useLocation();
  const { data: statusData } = useStatus();
  const { user } = useAuthStore();
  const { theme, toggleTheme } = useUIStore();

  const title = PAGE_TITLES[location.pathname] || 'FinAgent AI';
  const isConnected = statusData?.status === 'ok';

  return (
    <header className="h-16 border-b border-slate-200 dark:border-slate-800/80 bg-white/80 dark:bg-slate-950/60 backdrop-blur-xl sticky top-0 z-30 px-6 flex items-center justify-between transition-colors">
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-bold text-slate-900 dark:text-slate-100 tracking-tight">{title}</h1>
      </div>

      <div className="flex items-center gap-3 sm:gap-4">
        {/* Status Indicator */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300">
          <span className="relative flex h-2 w-2">
            <span
              className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                isConnected ? 'bg-emerald-400' : 'bg-rose-400'
              }`}
            />
            <span
              className={`relative inline-flex rounded-full h-2 w-2 ${
                isConnected ? 'bg-emerald-500' : 'bg-rose-500'
              }`}
            />
          </span>
          <span className="font-medium text-[11px] hidden sm:inline">
            {isConnected ? 'System Online' : 'Connecting...'}
          </span>
        </div>

        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-900 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 transition flex items-center gap-1.5 text-xs font-semibold"
          title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
        >
          {theme === 'light' ? (
            <>
              <Moon className="w-4 h-4 text-indigo-600" />
              <span className="hidden md:inline text-[11px]">Dark Mode</span>
            </>
          ) : (
            <>
              <Sun className="w-4 h-4 text-amber-400" />
              <span className="hidden md:inline text-[11px]">Light Mode</span>
            </>
          )}
        </button>

        {/* User Pill */}
        <div className="flex items-center gap-2 pl-3 border-l border-slate-200 dark:border-slate-800">
          <div className="w-7 h-7 rounded-full bg-indigo-600/10 dark:bg-indigo-600/30 border border-indigo-600/20 dark:border-indigo-500/40 text-indigo-600 dark:text-indigo-300 flex items-center justify-center font-bold text-xs">
            {user?.username?.[0] || 'U'}
          </div>
          <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 hidden md:inline">
            {user?.username || 'User'}
          </span>
        </div>
      </div>
    </header>
  );
}
