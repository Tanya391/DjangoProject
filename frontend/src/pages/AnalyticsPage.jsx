import React from 'react';
import { BarChart3, Repeat, Calendar, Building2, Layers, AlertCircle, ShieldCheck } from 'lucide-react';
import {
  useSubscriptions,
  useTopMerchants,
  useMonthlySummary,
  useCategoryBreakdown,
} from '../hooks/useAnalytics';
import { MerchantBarChart } from '../charts/MerchantBarChart';
import { MonthlyAreaChart } from '../charts/MonthlyAreaChart';
import { CategoryPieChart } from '../charts/CategoryPieChart';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';

export function AnalyticsPage() {
  const { data: subData, isLoading: isSubLoading, isError: isSubError, refetch: refetchSubs } = useSubscriptions();
  const { data: merchantData } = useTopMerchants(10);
  const { data: monthlyData } = useMonthlySummary();
  const { data: categoryData } = useCategoryBreakdown();

  const subscriptions = subData?.subscriptions || [];
  const totalSubSpend = subscriptions.reduce((sum, s) => sum + (s.avg_amount || s.amount || 0), 0);

  const topMerchants = merchantData?.top_merchants || [];
  const monthlyList = monthlyData?.monthly_summary || [];
  const categoryList = categoryData?.category_breakdown || [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">Financial Intelligence Analytics</h2>
        <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
          Subscriptions, top merchants, category distribution, and historical trends.
        </p>
      </div>

      {/* Subscriptions Card Cluster */}
      <div className="glass-card p-6 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800/80 pb-4">
          <div className="flex items-center gap-2">
            <Repeat className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Detected Active Subscriptions & Recurring Bills</h3>
              <p className="text-xs text-slate-600 dark:text-slate-400">Detected recurring payment commitments</p>
            </div>
          </div>
          <div className="text-right">
            <span className="text-xs text-slate-600 dark:text-slate-400 block">Monthly Recurring Commitment</span>
            <span className="text-lg font-bold text-indigo-600 dark:text-indigo-400 font-mono-num">
              ₹{totalSubSpend.toLocaleString('en-IN')} / mo
            </span>
          </div>
        </div>

        {isSubLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-24 w-full" />
          </div>
        ) : isSubError ? (
          <ErrorState onRetry={refetchSubs} />
        ) : subscriptions.length === 0 ? (
          <p className="text-xs text-slate-400 dark:text-slate-500 py-4 text-center">No recurring subscriptions detected.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {subscriptions.map((sub, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 flex items-center justify-between hover:border-indigo-400 dark:hover:border-indigo-500/30 transition"
              >
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold text-sm">
                    {sub.merchant?.[0] || 'S'}
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100">{sub.merchant}</h4>
                    <p className="text-[11px] text-slate-600 dark:text-slate-400 capitalize">
                      {sub.category || 'Recurring'} • <span className="text-indigo-600 dark:text-indigo-400 font-medium">{sub.frequency || 'Monthly'}</span>
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-sm font-bold text-slate-900 dark:text-slate-100 font-mono-num">
                    ₹{(sub.avg_amount || sub.amount || 0).toLocaleString('en-IN')}
                  </span>
                  <p className="text-[10px] text-slate-600 dark:text-slate-400">Last: {sub.last_date || sub.last_charged}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Merchants Chart */}
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800/80 pb-4">
            <div className="flex items-center gap-2">
              <Building2 className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Top 10 Merchants by Outflow</h3>
            </div>
            <span className="text-xs text-slate-600 dark:text-slate-400">Total debit volume</span>
          </div>
          <MerchantBarChart data={topMerchants} />
        </div>

        {/* Monthly Net Trends Chart */}
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800/80 pb-4">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Monthly Net Cashflow Trajectory</h3>
            </div>
            <span className="text-xs text-slate-600 dark:text-slate-400">Historical Net</span>
          </div>
          <MonthlyAreaChart data={monthlyList} />
        </div>
      </div>

      {/* Category Distribution */}
      <div className="glass-card p-6 rounded-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800/80 pb-4">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            <h3 className="text-base font-bold text-slate-900 dark:text-white">Category Expenditure Share</h3>
          </div>
          <span className="text-xs text-slate-600 dark:text-slate-400">Overall Expense Proportion</span>
        </div>
        <CategoryPieChart data={categoryList} />
      </div>
    </div>
  );
}
