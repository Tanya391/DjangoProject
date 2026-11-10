import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const COLORS = [
  '#6366f1', // Indigo
  '#06b6d4', // Cyan
  '#f59e0b', // Amber
  '#10b981', // Emerald
  '#ec4899', // Pink
  '#8b5cf6', // Purple
  '#3b82f6', // Blue
  '#f43f5e', // Rose
];

export function CategoryPieChart({ data = [] }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-600 dark:text-slate-400 text-sm">
        No category breakdown available.
      </div>
    );
  }

  const totalSum = data.reduce((sum, item) => sum + (item.total || 0), 0);
  const chartData = data.map(item => ({
    ...item,
    computedPercentage: totalSum > 0 ? Math.round(((item.total || 0) / totalSum) * 100) : 0,
    safeCategory: item.category || 'General'
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="glass-card p-3 rounded-xl border border-slate-200 dark:border-slate-700/80 shadow-xl text-xs space-y-1">
          <p className="font-bold text-slate-900 dark:text-slate-100 capitalize">{item.safeCategory}</p>
          <p className="text-indigo-600 dark:text-indigo-400 font-mono-num font-semibold">
            ₹{item.total?.toLocaleString('en-IN')} ({item.computedPercentage}%)
          </p>
          <p className="text-slate-600 dark:text-slate-400 text-[11px]">{item.count} transactions</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full flex flex-col md:flex-row items-center justify-between gap-6">
      <div className="w-full md:w-1/2 h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius="60%"
              outerRadius="80%"
              paddingAngle={3}
              dataKey="total"
              nameKey="safeCategory"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="transparent" strokeWidth={2} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="w-full md:w-1/2 space-y-2 max-h-60 overflow-y-auto pr-1">
        {chartData.map((item, index) => (
          <div
            key={index}
            className="flex items-center justify-between p-2 rounded-xl bg-slate-100/80 dark:bg-slate-900/40 hover:bg-slate-200/80 dark:hover:bg-slate-800/50 transition text-xs border border-slate-200 dark:border-slate-800/60"
          >
            <div className="flex items-center gap-2">
              <span
                className="w-2.5 h-2.5 rounded-full"
                style={{ backgroundColor: COLORS[index % COLORS.length] }}
              />
              <span className="font-semibold text-slate-800 dark:text-slate-200 capitalize">{item.safeCategory.replace('_', ' ')}</span>
            </div>
            <div className="text-right">
              <span className="font-mono-num font-bold text-slate-900 dark:text-slate-100">₹{item.total?.toLocaleString('en-IN')}</span>
              <span className="text-slate-600 dark:text-slate-400 ml-2 text-[11px]">{item.computedPercentage}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
