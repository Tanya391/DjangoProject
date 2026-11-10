import React from 'react';

export function KPICard({ title, value, subtitle, icon: Icon, trend, trendValue, color = 'indigo' }) {
  const colorMap = {
    indigo: {
      iconBg: 'bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border-indigo-200 dark:border-indigo-500/20',
      border: 'hover:border-indigo-400 dark:hover:border-indigo-500/30',
      badge: 'bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/20',
    },
    emerald: {
      iconBg: 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-500/20',
      border: 'hover:border-emerald-400 dark:hover:border-emerald-500/30',
      badge: 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20',
    },
    rose: {
      iconBg: 'bg-rose-50 dark:bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-200 dark:border-rose-500/20',
      border: 'hover:border-rose-400 dark:hover:border-rose-500/30',
      badge: 'bg-rose-50 dark:bg-rose-500/10 text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-500/20',
    },
    amber: {
      iconBg: 'bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-200 dark:border-amber-500/20',
      border: 'hover:border-amber-400 dark:hover:border-amber-500/30',
      badge: 'bg-amber-50 dark:bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-500/20',
    },
    cyan: {
      iconBg: 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border-cyan-200 dark:border-cyan-500/20',
      border: 'hover:border-cyan-400 dark:hover:border-cyan-500/30',
      badge: 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/20',
    },
  };

  const activeColor = colorMap[color] || colorMap.indigo;

  return (
    <div className={`glass-card p-6 rounded-2xl glass-card-hover ${activeColor.border} relative overflow-hidden group`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-400">{title}</span>
        {Icon && (
          <div className={`p-2.5 rounded-xl border ${activeColor.iconBg} transition-transform group-hover:scale-110`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      <div className="mt-4 flex items-baseline gap-2">
        <h3 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white font-mono-num">{value}</h3>
      </div>

      {(subtitle || trendValue) && (
        <div className="mt-3 flex items-center gap-2 text-xs text-slate-600 dark:text-slate-400">
          {trendValue && (
            <span
              className={`inline-flex items-center gap-0.5 px-2 py-0.5 rounded-md font-medium text-[11px] ${
                trend === 'up'
                  ? 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20'
                  : trend === 'down'
                  ? 'bg-rose-50 dark:bg-rose-500/10 text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-500/20'
                  : activeColor.badge
              }`}
            >
              {trend === 'up' && '↑ '}
              {trend === 'down' && '↓ '}
              {trendValue}
            </span>
          )}
          {subtitle && <span>{subtitle}</span>}
        </div>
      )}
    </div>
  );
}
