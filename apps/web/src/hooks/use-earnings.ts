"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { createClientFetch } from "@/lib/api";
import type { EarningsCallRead, JobStatus } from "@/types";

function useApiFetch() {
  const { getToken } = useAuth();
  return createClientFetch(getToken);
}

export function useEarnings(ticker: string) {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["earnings", ticker],
    queryFn: () =>
      fetchApi<EarningsCallRead[]>(`/api/v1/stocks/${ticker}/earnings`),
    enabled: ticker.length > 0,
  });
}

export function useAnalyzeEarnings() {
  const fetchApi = useApiFetch();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ ticker, transcript }: { ticker: string; transcript?: string }) =>
      fetchApi<JobStatus>(`/api/v1/stocks/${ticker}/earnings/analyze`, {
        method: "POST",
        body: { transcript },
      }),
    onSuccess: (_, { ticker }) => {
      queryClient.invalidateQueries({ queryKey: ["earnings", ticker] });
    },
  });
}
