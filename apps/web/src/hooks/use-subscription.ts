"use client";

import { useQuery, useMutation } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import { createClientFetch } from "@/lib/api";
import type {
  SubscriptionRead,
  UsageInfo,
  CheckoutSessionResponse,
  BillingPortalResponse,
} from "@/types";

function useApiFetch() {
  const { getToken } = useAuth();
  return createClientFetch(getToken);
}

export function useSubscription() {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["subscription"],
    queryFn: () => fetchApi<SubscriptionRead>("/api/v1/billing/subscription"),
    staleTime: 30_000,
  });
}

export function useUsage() {
  const fetchApi = useApiFetch();
  return useQuery({
    queryKey: ["usage"],
    queryFn: () => fetchApi<UsageInfo>("/api/v1/billing/usage"),
    staleTime: 30_000,
  });
}

export function useCreateCheckout() {
  const fetchApi = useApiFetch();
  return useMutation({
    mutationFn: () =>
      fetchApi<CheckoutSessionResponse>("/api/v1/billing/checkout", {
        method: "POST",
      }),
    onSuccess: (data) => {
      window.location.href = data.checkout_url;
    },
  });
}

export function useCreatePortal() {
  const fetchApi = useApiFetch();
  return useMutation({
    mutationFn: () =>
      fetchApi<BillingPortalResponse>("/api/v1/billing/portal", {
        method: "POST",
      }),
    onSuccess: (data) => {
      window.location.href = data.portal_url;
    },
  });
}
