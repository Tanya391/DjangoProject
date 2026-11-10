import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function MonthlyAreaChart({ data = [] }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-600 dark:text-slate-400 text-sm">
        No monthly trends available.
      </div>
    );
  }

  return (
    <div className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="netGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.5} />
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.2)" vertical={false} />
          <XAxis dataKey="month" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
          <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(val) => `₹${val / 1000}k`} />
          <Tooltip
            content={({ active, payload, label }) => {
              if (active && payload && payload.length) {
                return (
                  <div className="glass-card p-3 rounded-xl border border-slate-200 dark:border-slate-700/80 shadow-xl text-xs space-y-1">
                    <p className="font-semibold text-slate-900 dark:text-slate-200">{label}</p>
                    <p className="text-indigo-600 dark:text-indigo-400 font-mono-num font-bold">
                      Net Flow: ₹{payload[0].value?.toLocaleString('en-IN')}
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Area type="monotone" dataKey="net" stroke="#6366f1" strokeWidth={3} fillOpacity={1} fill="url(#netGrad)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
