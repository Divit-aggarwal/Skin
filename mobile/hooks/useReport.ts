import { useQuery } from '@tanstack/react-query';
import { analysisApi } from '../api/analysis';

export function useReport(sessionId: string) {
  return useQuery({
    queryKey: ['report', sessionId],
    queryFn: () => analysisApi.getSession(sessionId),
    staleTime: Infinity,
    enabled: !!sessionId,
  });
}
