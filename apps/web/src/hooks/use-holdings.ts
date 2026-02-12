"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { createClientFetch } from "@/lib/api";
import type { HoldingRead } from "@/types";

function useApiFetch() {
  const { getToken } = useAuth();
  return createClientFetch(getToken);
}

export function useHoldings(portfolioId: number) {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["portfolios", portfolioId, "holdings"],
    queryFn: () =>
      fetchApi<HoldingRead[]>(`/api/v1/portfolios/${portfolioId}/holdings`),
    enabled: portfolioId > 0,
  });
}

export function useAddHolding(portfolioId: number) {
  const fetchApi = useApiFetch();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { ticker: string; shares: number }) =>
      fetchApi<HoldingRead>(`/api/v1/portfolios/${portfolioId}/holdings`, {
        method: "POST",
        body: data,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["portfolios", portfolioId, "holdings"] });
      queryClient.invalidateQueries({ queryKey: ["portfolios", portfolioId] });
    },
  });
}

export function useUpdateHolding(portfolioId: number) {
  const fetchApi = useApiFetch();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ holdingId, data }: { holdingId: number; data: { shares: number } }) =>
      fetchApi<HoldingRead>(
        `/api/v1/portfolios/${portfolioId}/holdings/${holdingId}`,
        { method: "PUT", body: data }
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["portfolios", portfolioId, "holdings"] });
      queryClient.invalidateQueries({ queryKey: ["portfolios", portfolioId] });
    },
  });
}

export function useDeleteHolding(portfolioId: number) {
  const fetchApi = useApiFetch();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (holdingId: number) =>
      fetchApi<null>(
        `/api/v1/portfolios/${portfolioId}/holdings/${holdingId}`,
        { method: "DELETE" }
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["portfolios", portfolioId, "holdings"] });
      queryClient.invalidateQueries({ queryKey: ["portfolios", portfolioId] });
    },
  });
}
