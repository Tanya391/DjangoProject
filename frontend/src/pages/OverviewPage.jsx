import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  TrendingUp,
  TrendingDown,
  Wallet,
  Flame,
  PiggyBank,
  ArrowRight,
  Bot,
  Sparkles,
  Receipt,
  Building2,
  Calendar,
} from 'lucide-react';
import {
  useCashflow,
  useMonthlySummary,
  useCategoryBreakdown,
  useTopMerchants,
  useTransactions,
} from '../hooks/useAnalytics';
import { KPICard } from '../components/ui/KPICard';
import { CardSkeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { NetCashflowLine } from '../charts/NetCashflowLine';
import { CategoryPieChart } from '../charts/CategoryPieChart';

export function OverviewPage() {
  const navigate = useNavigate();

  const { data: cashflowData, isLoading: isCashflowLoading, isError: isCashflowError, refetch: refetchCashflow } = useCashflow();
  const { data: monthlyData } = useMonthlySummary();
  const { data: categoryData } = useCategoryBreakdown();
  const { data: merchantData } = useTopMerchants(5);
  const { data: txData } = useTransactions({ limit: 5 });

  const cashflow = cashflowData?.cashflow || {};
  const monthlyList = monthlyData?.monthly_summary || [];
  const categoryList = categoryData?.category_breakdown || [];
  const merchantList = merchantData?.top_merchants || [];
  const recentTxs = txData?.results || txData?.transactions || [];

  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl p-8 bg-gradient-to-r from-indigo-700 via-indigo-800 to-slate-900 text-white shadow-2xl">
        <div className="absolute top-0 right-0 w-80 h-80 bg-white/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-white/10 text-cyan-200 border border-white/20">
              <Sparkles className="w-3.5 h-3.5 text-cyan-300" />
              Financial Overview
            </div>
            <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Financial Overview & Intelligence
            </h2>
            <p className="text-sm text-indigo-100">
              Overview of your cashflow, subscriptions, and financial metrics.
            </p>
          </div>

          <button
            onClick={() => navigate('/chat')}
            className="px-5 py-3 rounded-2xl bg-white text-indigo-900 hover:bg-slate-100 font-bold text-sm shadow-xl transition flex items-center gap-2.5 shrink-0"
          >
            <Bot className="w-4 h-4 text-indigo-600" />
            Ask AI Assistant
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      {isCashflowLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
      ) : isCashflowError ? (
        <ErrorState onRetry={refetchCashflow} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          <KPICard
            title="Total Income"
            value={`₹${(cashflow.income || 0).toLocaleString('en-IN')}`}
            subtitle="Verified Credits"
            icon={TrendingUp}
            color="emerald"
            trend="up"
            trendValue="Income"
          />
          <KPICard
            title="Total Expenses"
            value={`₹${(cashflow.expense || 0).toLocaleString('en-IN')}`}
            subtitle="Verified Debits"
            icon={TrendingDown}
            color="rose"
            trend="down"
            trendValue="Expense"
          />
          <KPICard
            title="Net Cashflow"
            value={`₹${(cashflow.net || 0).toLocaleString('en-IN')}`}
            subtitle={`${cashflow.income ? Math.round((cashflow.net / cashflow.income) * 100) : 0}% Savings Rate`}
            icon={Wallet}
            color="indigo"
          />
          <KPICard
            title="Monthly Burn Rate"
            value={`₹${(cashflow.expense ? Math.round(cashflow.expense / 6) : 0).toLocaleString('en-IN')}`}
            subtitle="Estimated Monthly Outflow"
            icon={Flame}
            color="amber"
          />
        </div>
      )}

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Cashflow Trends */}
        <div className="lg:col-span-2 glass-card p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800/80 pb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Monthly Cashflow Velocity</h3>
              <p className="text-xs text-slate-600 dark:text-slate-400">Income vs. Expense over previous months</p>
            </div>
            <button
              onClick={() => navigate('/analytics')}
              className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 flex items-center gap-1"
            >
              Deep Analytics <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
          <NetCashflowLine data={monthlyList} />
        </div>

        {/* Category Spending Breakdown */}
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <div className="border-b border-slate-200 dark:border-slate-800/80 pb-4">
            <h3 className="text-base font-bold text-slate-900 dark:text-white">Spending by Category</h3>
            <p className="text-xs text-slate-600 dark:text-slate-400">Top category allocation</p>
          </div>
          <CategoryPieChart data={categoryList} />
        </div>
      </div>

      {/* Bottom Row: Top Merchants + Recent Transactions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Merchants */}
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800/80 pb-4">
            <div className="flex items-center gap-2">
              <Building2 className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Top Merchants</h3>
            </div>
            <span className="text-xs text-slate-600 dark:text-slate-400">By total spend</span>
          </div>

          <div className="space-y-3">
            {merchantList.length === 0 ? (
              <p className="text-xs text-slate-600 dark:text-slate-400 text-center py-4">No merchant data available.</p>
            ) : (
              merchantList.map((m) => (
                <div
                  key={m.merchant}
                  className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/60 hover:border-slate-300 dark:hover:border-slate-700 transition"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold text-xs uppercase">
                      {m.merchant?.[0] || 'M'}
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-slate-900 dark:text-slate-200">{m.merchant}</p>
                      <p className="text-[11px] text-slate-600 dark:text-slate-400 capitalize">{(m.category || 'General').replace('_', ' ')} • {m.count} txs</p>
                    </div>
                  </div>
                  <span className="font-mono-num font-bold text-sm text-slate-900 dark:text-slate-100">
                    ₹{m.total?.toLocaleString('en-IN')}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800/80 pb-4">
            <div className="flex items-center gap-2">
              <Receipt className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Recent Transactions</h3>
            </div>
            <button
              onClick={() => navigate('/transactions')}
              className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 flex items-center gap-1"
            >
              View Register <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3">
            {recentTxs.length === 0 ? (
              <p className="text-xs text-slate-600 dark:text-slate-400 text-center py-4">No recent transactions.</p>
            ) : (
              recentTxs.map((t) => (
                <div
                  key={t.transaction_id}
                  className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/60"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs ${
                        t.transaction_type === 'credit'
                          ? 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20'
                          : 'bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300'
                      }`}
                    >
                      {t.transaction_type === 'credit' ? '+' : '-'}
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-slate-900 dark:text-slate-200">{t.receiver}</p>
                      <p className="text-[11px] text-slate-600 dark:text-slate-400">{t.date} • {t.description}</p>
                    </div>
                  </div>
                  <span
                    className={`font-mono-num font-bold text-sm ${
                      t.transaction_type === 'credit' ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-900 dark:text-slate-100'
                    }`}
                  >
                    {t.transaction_type === 'credit' ? '+' : '-'}₹{t.amount?.toLocaleString('en-IN')}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
