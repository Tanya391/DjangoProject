import React from 'react';

export function Skeleton({ className = '' }) {
  return <div className={`animate-pulse bg-slate-200 dark:bg-slate-800/60 rounded-xl ${className}`} />;
}

export function CardSkeleton() {
  return (
    <div className="glass-card p-6 rounded-2xl space-y-4">
      <div className="flex justify-between items-center">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-9 w-9 rounded-xl" />
      </div>
      <Skeleton className="h-8 w-36" />
      <Skeleton className="h-4 w-28" />
    </div>
  );
}
