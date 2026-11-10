import React from 'react';
import { useNavigate } from 'react-router-dom';
import { History, Play, Clock, Sparkles, Layers, ArrowRight } from 'lucide-react';
import { useQueryHistory } from '../hooks/useAnalytics';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';

export function HistoryPage() {
  const navigate = useNavigate();
  const { data, isLoading, isError, refetch } = useQueryHistory();

  const historyItems = data?.history || data?.results || [];

  const handleRerun = (questionText) => {
    navigate('/chat', { state: { autoQuery: questionText } });
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">Query History</h2>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
            Audit previous financial queries and answers.
          </p>
        </div>
        <button
          onClick={() => navigate('/chat')}
          className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg transition flex items-center gap-2"
        >
          <Sparkles className="w-3.5 h-3.5 text-cyan-200" />
          New AI Query
        </button>
      </div>

      {/* History List */}
      <div className="space-y-4">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-32 w-full rounded-2xl" />)
        ) : isError ? (
          <ErrorState onRetry={refetch} />
        ) : historyItems.length === 0 ? (
          <div className="glass-card p-12 rounded-2xl text-center space-y-3 border border-slate-200 dark:border-slate-800">
            <History className="w-10 h-10 text-slate-400 dark:text-slate-600 mx-auto" />
            <h4 className="text-base font-bold text-slate-700 dark:text-slate-300">No Query History Recorded</h4>
            <p className="text-xs text-slate-600 dark:text-slate-400 max-w-sm mx-auto">
              Ask your first question in the AI Assistant to log financial queries here.
            </p>
            <button
              onClick={() => navigate('/chat')}
              className="mt-2 inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-xs font-bold rounded-xl shadow"
            >
              Ask AI Assistant <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        ) : (
          historyItems.map((item) => (
            <div
              key={item.id}
              className="glass-card p-6 rounded-2xl border border-slate-200 dark:border-slate-800 hover:border-indigo-400 dark:hover:border-indigo-500/30 transition space-y-3"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-[11px] text-slate-600 dark:text-slate-400">
                    <Clock className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
                    <span>{new Date(item.timestamp).toLocaleString()}</span>
                    {item.source_count !== undefined && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-[10px] text-slate-700 dark:text-slate-300 font-medium ml-2">
                        <Layers className="w-3 h-3 text-cyan-600 dark:text-cyan-400" />
                        {item.source_count} source records
                      </span>
                    )}
                  </div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">{item.question}</h3>
                </div>

                <button
                  onClick={() => handleRerun(item.question)}
                  className="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-900 dark:hover:bg-slate-800 text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 border border-slate-200 dark:border-slate-800 hover:border-indigo-400 text-xs font-semibold transition flex items-center gap-1.5 shrink-0"
                >
                  <Play className="w-3 h-3 fill-indigo-600 dark:fill-indigo-400" />
                  Re-run Query
                </button>
              </div>

              {/* Synthesized Answer Preview */}
              <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 text-xs text-slate-800 dark:text-slate-300 leading-relaxed">
                <p className="font-medium">{item.answer}</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
