import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

export function ErrorState({ title = 'Failed to load data', message = 'Please check your connection or try again.', onRetry }) {
  return (
    <div className="glass-card p-8 rounded-2xl text-center flex flex-col items-center justify-center space-y-4 border border-rose-200 dark:border-rose-500/20 bg-rose-50/50 dark:bg-rose-950/10">
      <div className="p-3 bg-rose-100 dark:bg-rose-500/10 text-rose-600 dark:text-rose-400 rounded-2xl border border-rose-200 dark:border-rose-500/20">
        <AlertCircle className="w-8 h-8" />
      </div>
      <div>
        <h4 className="text-lg font-bold text-slate-900 dark:text-slate-100">{title}</h4>
        <p className="text-sm text-slate-600 dark:text-slate-400 mt-1 max-w-md">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-sm font-semibold rounded-xl transition border border-slate-200 dark:border-slate-700"
        >
          <RefreshCw className="w-4 h-4" />
          Retry Request
        </button>
      )}
    </div>
  );
}
