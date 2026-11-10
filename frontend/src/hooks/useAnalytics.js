import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';

export function useCashflow() {
  return useQuery({
    queryKey: ['cashflow'],
    queryFn: api.getCashflow,
    staleTime: 60000,
  });
}

export function useMonthlySummary(year) {
  return useQuery({
    queryKey: ['monthlySummary', year],
    queryFn: () => api.getMonthlySummary(year),
    staleTime: 60000,
  });
}

export function useCategoryBreakdown() {
  return useQuery({
    queryKey: ['categoryBreakdown'],
    queryFn: api.getCategoryBreakdown,
    staleTime: 60000,
  });
}

export function useTopMerchants(limit = 10) {
  return useQuery({
    queryKey: ['topMerchants', limit],
    queryFn: () => api.getTopMerchants(limit),
    staleTime: 60000,
  });
}

export function useSubscriptions() {
  return useQuery({
    queryKey: ['subscriptions'],
    queryFn: api.getSubscriptions,
    staleTime: 60000,
  });
}

export function useTransactions(params) {
  return useQuery({
    queryKey: ['transactions', params],
    queryFn: () => api.getTransactions(params),
    staleTime: 30000,
  });
}

export function useQueryHistory() {
  return useQuery({
    queryKey: ['queryHistory'],
    queryFn: api.getQueryHistory,
    staleTime: 15000,
  });
}

export function useStatus() {
  return useQuery({
    queryKey: ['status'],
    queryFn: api.getStatus,
    refetchInterval: 30000,
  });
}
