"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { createClientFetch } from "@/lib/api";
import type { WatchlistItem } from "@/types";

function useApiFetch() {
  const { getToken } = useAuth();
  return createClientFetch(getToken);
}

export function useWatchlist() {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["watchlist"],
    queryFn: () => fetchApi<WatchlistItem[]>("/api/v1/watchlist"),
  });
}

export function useAddToWatchlist() {
  const fetchApi = useApiFetch();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (ticker: string) =>
      fetchApi<WatchlistItem>("/api/v1/watchlist", {
        method: "POST",
        body: { ticker },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["watchlist"] });
    },
  });
}

export function useRemoveFromWatchlist() {
  const fetchApi = useApiFetch();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (itemId: number) =>
      fetchApi<null>(`/api/v1/watchlist/${itemId}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["watchlist"] });
    },
  });
}

export function useRefreshWatchlist() {
  const fetchApi = useApiFetch();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () =>
      fetchApi<WatchlistItem[]>("/api/v1/watchlist/refresh", { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["watchlist"] });
    },
  });
}
