"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { createClientFetch } from "@/lib/api";
import type { JobStatus } from "@/types";

function useApiFetch() {
  const { getToken } = useAuth();
  return createClientFetch(getToken);
}

export function useAnalyzePortfolio() {
  const fetchApi = useApiFetch();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (portfolioId: number) =>
      fetchApi<JobStatus>(`/api/v1/analysis/portfolios/${portfolioId}/analyze`, {
        method: "POST",
      }),
    onSuccess: (_, portfolioId) => {
      queryClient.invalidateQueries({ queryKey: ["portfolios", portfolioId, "snapshot"] });
      queryClient.invalidateQueries({ queryKey: ["portfolios", portfolioId] });
    },
  });
}

export function useCompare() {
  const fetchApi = useApiFetch();
  return useMutation({
    mutationFn: (tickers: string[]) =>
      fetchApi<JobStatus>("/api/v1/analysis/compare", {
        method: "POST",
        body: { tickers },
      }),
  });
}

export function usePastComparisons() {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["comparisons"],
    queryFn: () => fetchApi<JobStatus[]>("/api/v1/analysis/comparisons"),
  });
}
