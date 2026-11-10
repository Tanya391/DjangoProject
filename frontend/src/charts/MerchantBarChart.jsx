import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export function MerchantBarChart({ data = [] }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-600 dark:text-slate-400 text-sm">
        No merchant data available.
      </div>
    );
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="glass-card p-3 rounded-xl border border-slate-200 dark:border-slate-700/80 shadow-xl text-xs space-y-1">
          <p className="font-bold text-slate-900 dark:text-slate-100">{item.merchant}</p>
          <p className="text-cyan-600 dark:text-cyan-400 font-mono-num font-semibold">
            Spent: ₹{item.total?.toLocaleString('en-IN')}
          </p>
          <p className="text-slate-600 dark:text-slate-400 text-[11px]">{item.count} transactions</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.2)" horizontal={false} />
          <XAxis type="number" stroke="#64748b" fontSize={11} axisLine={false} tickLine={false} tickFormatter={(v) => `₹${v/1000}k`} />
          <YAxis dataKey="merchant" type="category" stroke="#64748b" fontSize={12} width={100} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="total" radius={[0, 6, 6, 0]}>
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#6366f1' : '#06b6d4'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
