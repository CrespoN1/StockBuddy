import "server-only";
import { auth } from "@clerk/nextjs/server";

/**
 * Server-side fetch with Clerk JWT attached.
 * Use in Server Components and Route Handlers only.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
};

export async function apiFetch<T>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const { body, headers: customHeaders, ...rest } = options;

  const { getToken } = await auth();
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

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API Error: ${res.status}`);
  }

  if (res.status === 204) return null as T;
  return res.json();
}
