"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { createClientFetch } from "@/lib/api";
import type { PriceAlert, PriceAlertCreate, AlertsSummary } from "@/types";

function useApiFetch() {
  const { getToken } = useAuth();
  return createClientFetch(getToken);
}

export function useAlerts() {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["alerts"],
    queryFn: () => fetchApi<PriceAlert[]>("/api/v1/alerts"),
  });
}

export function useAlertsSummary() {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["alerts", "summary"],
    queryFn: () => fetchApi<AlertsSummary>("/api/v1/alerts/summary"),
    refetchInterval: 60_000,
  });
}

export function useCreateAlert() {
  const fetchApi = useApiFetch();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: PriceAlertCreate) =>
      fetchApi<PriceAlert>("/api/v1/alerts", {
        method: "POST",
        body: data,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });
}

export function useDeleteAlert() {
  const fetchApi = useApiFetch();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      fetchApi<null>(`/api/v1/alerts/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });
}
