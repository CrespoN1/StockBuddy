/**
 * Client-side API client for communicating with the FastAPI backend.
 *
 * For server-side usage, import `apiFetch` from `@/lib/api.server` instead.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
};

/**
 * Client-side fetch factory. Pass `getToken` from Clerk's `useAuth()` hook.
 *
 * Usage:
 * ```tsx
 * const { getToken } = useAuth();
 * const fetchApi = createClientFetch(getToken);
 * const data = await fetchApi("/api/v1/portfolios");
 * ```
 */
export function createClientFetch(getToken: () => Promise<string | null>) {
  return async function clientFetch<T>(
    path: string,
    options: RequestOptions = {}
  ): Promise<T> {
    const { body, headers: customHeaders, ...rest } = options;
    const token = await getToken();

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(customHeaders as Record<string, string>),
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_URL}${path}`, {
      headers,
      body: body ? JSON.stringify(body) : undefined,
      ...rest,
    });

    if (res.status === 401) {
      throw new Error("Unauthorized — please sign in again");
    }

    if (res.status === 429) {
      throw new Error("Too many requests — please slow down");
    }

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail || `API Error: ${res.status}`);
    }

    if (res.status === 204) return null as T;
    return res.json();
  };
}
