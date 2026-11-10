import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Receipt,
  BarChart3,
  Database,
  Bot,
  History,
  LogOut,
  Sparkles,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { useUIStore } from '../store/useUIStore';
import { useAuthStore } from '../store/useAuthStore';

export function Sidebar() {
  const { isSidebarOpen, toggleSidebar } = useUIStore();
  const { user, logout } = useAuthStore();

  const navItems = [
    { label: 'Dashboard', path: '/', icon: LayoutDashboard },
    { label: 'Transactions', path: '/transactions', icon: Receipt },
    { label: 'Analytics', path: '/analytics', icon: BarChart3 },
    { label: 'Data Management', path: '/data', icon: Database },
    { label: 'AI Assistant', path: '/chat', icon: Bot, badge: 'Gemini RAG' },
    { label: 'Query History', path: '/history', icon: History },
  ];

  return (
    <aside
      className={`fixed top-0 left-0 z-40 h-screen bg-white dark:bg-slate-950/90 border-r border-slate-200 dark:border-slate-800/80 backdrop-blur-xl transition-all duration-300 ease-in-out flex flex-col justify-between ${
        isSidebarOpen ? 'w-64' : 'w-20'
      }`}
    >
      {/* Top Header */}
      <div>
        <div className="h-16 px-5 flex items-center justify-between border-b border-slate-200 dark:border-slate-800/80">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-500 flex items-center justify-center text-white font-black text-lg shadow-lg shadow-indigo-500/20 shrink-0">
              F
            </div>
            {isSidebarOpen && (
              <div className="flex flex-col">
                <span className="font-extrabold text-slate-900 dark:text-white text-base tracking-tight leading-none">
                  FinAgent <span className="text-indigo-600 dark:text-indigo-400">AI</span>
                </span>
                {/* <span className="text-[10px] text-slate-600 dark:text-slate-400 font-medium tracking-wide uppercase mt-1">
                  Financial Intelligence
                </span> */}
              </div>
            )}
          </div>

          <button
            onClick={toggleSidebar}
            className="p-1.5 rounded-lg text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800/60 transition"
            title={isSidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
          >
            {isSidebarOpen ? <ChevronLeft className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1.5 mt-2">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all relative group ${
                  isActive
                    ? 'bg-indigo-50 dark:bg-gradient-to-r dark:from-indigo-600/20 dark:to-indigo-500/10 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/30 font-semibold'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-900/60'
                }`
              }
            >
              <item.icon className="w-5 h-5 shrink-0 transition-transform group-hover:scale-110" />
              {isSidebarOpen && (
                <span className="truncate flex-1">{item.label}</span>
              )}
              {isSidebarOpen && item.badge && (
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-500/20 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/30 flex items-center gap-1">
                  <Sparkles className="w-2.5 h-2.5 text-cyan-500 dark:text-cyan-400" />
                  {item.badge}
                </span>
              )}
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Footer User Info & Logout */}
      <div className="p-3 border-t border-slate-200 dark:border-slate-800/80">
        <div
          className={`flex items-center gap-3 p-2 rounded-xl bg-slate-100 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800/60 ${
            !isSidebarOpen && 'justify-center'
          }`}
        >
          <div className="w-8 h-8 rounded-full bg-indigo-600/10 dark:bg-indigo-500/20 border border-indigo-600/20 dark:border-indigo-500/40 text-indigo-600 dark:text-indigo-300 flex items-center justify-center font-bold text-xs uppercase shrink-0">
            {user?.username?.[0] || 'U'}
          </div>
          {isSidebarOpen && (
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-slate-900 dark:text-slate-200 truncate">{user?.username || 'User'}</p>
              <p className="text-[10px] text-slate-600 dark:text-slate-400 truncate">{user?.email || 'pro@finagent.ai'}</p>
            </div>
          )}
          {isSidebarOpen && (
            <button
              onClick={logout}
              className="p-1.5 rounded-lg text-slate-600 dark:text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-500/10 transition"
              title="Log out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </aside>
  );
}
