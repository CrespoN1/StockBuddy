"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { createClientFetch } from "@/lib/api";
import type {
  PortfolioRead,
  PortfolioDetail,
  PortfolioSnapshotRead,
  SectorAllocation,
  EarningsInsights,
  NewsArticle,
  RedditPost,
  HoldingRead,
  DashboardSummary,
} from "@/types";

function useApiFetch() {
  const { getToken } = useAuth();
  return createClientFetch(getToken);
}

export function usePortfolios() {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["portfolios"],
    queryFn: () => fetchApi<PortfolioRead[]>("/api/v1/portfolios"),
  });
}

export function usePortfolio(id: number) {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["portfolios", id],
    queryFn: () => fetchApi<PortfolioDetail>(`/api/v1/portfolios/${id}`),
    enabled: id > 0,
  });
}

export function usePortfolioHistory(id: number, days = 90) {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["portfolios", id, "history", days],
    queryFn: () =>
      fetchApi<PortfolioSnapshotRead[]>(
        `/api/v1/portfolios/${id}/history?days=${days}`
      ),
    enabled: id > 0,
  });
}

export function usePortfolioSnapshot(id: number, enabled = true) {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["portfolios", id, "snapshot"],
    queryFn: () => fetchApi<PortfolioSnapshotRead>(`/api/v1/portfolios/${id}/snapshot`),
    enabled: id > 0 && enabled,
  });
}

export function usePortfolioSectors(id: number) {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["portfolios", id, "sectors"],
    queryFn: () => fetchApi<SectorAllocation[]>(`/api/v1/portfolios/${id}/sectors`),
    enabled: id > 0,
  });
}

export function usePortfolioEarningsInsights(id: number) {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["portfolios", id, "earnings-insights"],
    queryFn: () => fetchApi<EarningsInsights>(`/api/v1/portfolios/${id}/earnings-insights`),
    enabled: id > 0,
  });
}

export function usePortfolioNews(id: number) {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["portfolios", id, "news"],
    queryFn: () => fetchApi<NewsArticle[]>(`/api/v1/portfolios/${id}/news`),
    enabled: id > 0,
    staleTime: 5 * 60 * 1000,
  });
}

export function usePortfolioReddit(id: number) {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["portfolios", id, "reddit"],
    queryFn: () => fetchApi<RedditPost[]>(`/api/v1/portfolios/${id}/reddit`),
    enabled: id > 0,
    staleTime: 10 * 60 * 1000, // 10 minutes — longer cache to respect Reddit rate limits
  });
}

export function useEarningsCalendar() {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["earnings-calendar"],
    queryFn: () =>
      fetchApi<HoldingRead[]>("/api/v1/portfolios/earnings-calendar"),
  });
}

export function useDashboardSummary() {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: () =>
      fetchApi<DashboardSummary>("/api/v1/portfolios/dashboard-summary"),
  });
}

export function useCreatePortfolio() {
  const fetchApi = useApiFetch();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { name: string }) =>
      fetchApi<PortfolioRead>("/api/v1/portfolios", {
        method: "POST",
        body: data,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["portfolios"] });
    },
  });
}

export function useUpdatePortfolio() {
  const fetchApi = useApiFetch();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: { name?: string } }) =>
      fetchApi<PortfolioRead>(`/api/v1/portfolios/${id}`, {
        method: "PUT",
        body: data,
      }),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["portfolios"] });
      queryClient.invalidateQueries({ queryKey: ["portfolios", id] });
    },
  });
}

export function useDeletePortfolio() {
  const fetchApi = useApiFetch();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      fetchApi<null>(`/api/v1/portfolios/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["portfolios"] });
    },
  });
}
