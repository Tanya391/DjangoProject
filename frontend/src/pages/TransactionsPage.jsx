import React, { useState } from 'react';
import { Search, Filter, Receipt, ArrowUpRight, ArrowDownLeft, Sparkles, RefreshCw } from 'lucide-react';
import { useTransactions } from '../hooks/useAnalytics';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';

export function TransactionsPage() {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');

  const { data, isLoading, isError, refetch } = useTransactions({ search, category });

  const transactions = data?.results || data?.transactions || [];
  const totalCount = data?.count || transactions.length;

  const categories = [
    { label: 'All Categories', value: '' },
    { label: 'Subscriptions', value: 'subscriptions' },
    { label: 'Shopping', value: 'shopping' },
    { label: 'Food Delivery', value: 'food_delivery' },
    { label: 'Groceries', value: 'groceries' },
    { label: 'Travel', value: 'travel' },
    { label: 'Internet / Recharges', value: 'internet' },
    { label: 'Rent', value: 'rent' },
    { label: 'Salary / Income', value: 'salary' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">Transaction Ledger</h2>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
            Search and filter transactions.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300">
            Total Records: <strong className="text-indigo-600 dark:text-indigo-400 font-mono-num">{totalCount}</strong>
          </span>
          <button
            onClick={() => refetch()}
            className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-900 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 transition"
            title="Refresh Transactions"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="glass-card p-4 rounded-2xl flex flex-col md:flex-row gap-4 items-center justify-between">
        {/* Search Input */}
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search merchant, description or amount..."
            className="w-full bg-slate-50 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
          />
        </div>

        {/* Category Dropdown */}
        <div className="flex items-center gap-3 w-full md:w-auto">
          <Filter className="w-4 h-4 text-slate-400 shrink-0" />
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full md:w-56 bg-slate-50 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:border-indigo-500 transition cursor-pointer"
          >
            {categories.map((c) => (
              <option key={c.value} value={c.value} className="bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100">
                {c.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Transactions Table */}
      <div className="glass-card rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-800">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800/80 bg-slate-100/70 dark:bg-slate-950/60 text-[11px] font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                <th className="py-3.5 px-6">Merchant / Receiver</th>
                <th className="py-3.5 px-4">Category</th>
                <th className="py-3.5 px-4">Date</th>
                <th className="py-3.5 px-4">Description</th>
                <th className="py-3.5 px-4 text-center">Type</th>
                <th className="py-3.5 px-6 text-right">Amount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800/60 text-xs">
              {isLoading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <tr key={i}>
                    <td className="py-4 px-6"><Skeleton className="h-4 w-32" /></td>
                    <td className="py-4 px-4"><Skeleton className="h-4 w-20" /></td>
                    <td className="py-4 px-4"><Skeleton className="h-4 w-24" /></td>
                    <td className="py-4 px-4"><Skeleton className="h-4 w-40" /></td>
                    <td className="py-4 px-4"><Skeleton className="h-4 w-12 mx-auto" /></td>
                    <td className="py-4 px-6"><Skeleton className="h-4 w-20 ml-auto" /></td>
                  </tr>
                ))
              ) : isError ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center">
                    <ErrorState onRetry={refetch} />
                  </td>
                </tr>
              ) : transactions.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center">
                    <div className="flex flex-col items-center justify-center space-y-2">
                      <Receipt className="w-8 h-8 text-slate-400 dark:text-slate-600" />
                      <p className="font-semibold text-slate-700 dark:text-slate-400">No matching transactions found</p>
                    </div>
                  </td>
                </tr>
              ) : (
                transactions.map((t) => (
                  <tr key={t.transaction_id} className="hover:bg-slate-100/60 dark:hover:bg-slate-900/50 transition">
                    <td className="py-3.5 px-6 font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold text-xs shrink-0">
                        {t.receiver?.[0] || 'T'}
                      </div>
                      <span className="truncate max-w-[180px]">{t.receiver}</span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-indigo-700 dark:text-indigo-300 capitalize">
                        {(t.category || '').replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 dark:text-slate-400 font-mono-num">{t.date}</td>
                    <td className="py-3.5 px-4 text-slate-700 dark:text-slate-300 truncate max-w-[220px]">{t.description}</td>
                    <td className="py-3.5 px-4 text-center">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold uppercase ${
                          t.transaction_type === 'credit'
                            ? 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20'
                            : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                        }`}
                      >
                        {t.transaction_type === 'credit' ? (
                          <ArrowDownLeft className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
                        ) : (
                          <ArrowUpRight className="w-3 h-3 text-slate-500 dark:text-slate-400" />
                        )}
                        {t.transaction_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-6 text-right font-mono-num font-bold">
                      <span className={t.transaction_type === 'credit' ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-900 dark:text-slate-100'}>
                        {t.transaction_type === 'credit' ? '+' : '-'}₹{t.amount?.toLocaleString('en-IN')}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
