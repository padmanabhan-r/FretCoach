import { useQuery } from '@tanstack/react-query';
import { fetchSessions, type SessionsResponse } from '@/lib/api';

export interface DateRangeFilter {
  startDate?: string;
  endDate?: string;
}

export function useSessions(
  userId: string = 'default_user',
  limit: number = 10,
  dateRange?: DateRangeFilter
) {
  return useQuery<SessionsResponse>({
    queryKey: ['sessions', userId, limit, dateRange?.startDate, dateRange?.endDate],
    queryFn: () => fetchSessions(userId, limit, true, dateRange?.startDate, dateRange?.endDate),
    staleTime: 30000, // Consider data fresh for 30 seconds
    refetchInterval: 60000, // Refetch every minute
  });
}

export function useSessionAggregates(userId: string = 'default_user', dateRange?: DateRangeFilter) {
  const { data, isLoading, error } = useSessions(userId, 10, dateRange);

  return {
    aggregates: data?.aggregates || null,
    isLoading,
    error,
  };
}
