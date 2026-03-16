// src/api/client.ts
// ─────────────────────────────────────────────────────────────────────────────
// Central fetch wrapper that handles:
//   • Base URL (env-driven)
//   • JWT access token injection
//   • Automatic token refresh on 401
//   • Consistent error shape
// ─────────────────────────────────────────────────────────────────────────────

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// Token storage helpers
const TOKEN_KEY = "ardhitrust_access";
const REFRESH_KEY = "ardhitrust_refresh";

export const tokenStore = {
  getAccess: () => localStorage.getItem(TOKEN_KEY),
  getRefresh: () => localStorage.getItem(REFRESH_KEY),
  set: (access: string, refresh: string) => {
    localStorage.setItem(TOKEN_KEY, access);
    localStorage.setItem(REFRESH_KEY, refresh);
  },
  clear: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

// ─── Structured error ───────────────────────────────────────────────────────
export class APIError extends Error {
  constructor(
    public status: number,
    public detail: string,
    public raw?: unknown
  ) {
    super(detail);
    this.name = "APIError";
  }
}

// ─── Token refresh (called once on 401, then retries the original request) ──
let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  // Deduplicate: if multiple requests hit 401 simultaneously, share one refresh
  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    const refresh = tokenStore.getRefresh();
    if (!refresh) throw new APIError(401, "No refresh token. Please log in.");

    const res = await fetch(`${BASE_URL}/api/v1/auth/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });

    if (!res.ok) {
      tokenStore.clear();
      throw new APIError(401, "Session expired. Please log in again.");
    }

    const data = await res.json();
    tokenStore.set(data.access, refresh);
    return data.access as string;
  })().finally(() => {
    refreshPromise = null;
  });

  return refreshPromise;
}

// ─── Core fetch wrapper ──────────────────────────────────────────────────────
async function request<T>(
  path: string,
  options: RequestInit = {},
  retrying = false
): Promise<T> {
  const token = tokenStore.getAccess();

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  // ── 401: try to refresh, then retry once ────────────────────────────────
  if (res.status === 401 && !retrying) {
    const newToken = await refreshAccessToken();
    return request<T>(path, {
      ...options,
      headers: { ...headers, Authorization: `Bearer ${newToken}` },
    }, true);
  }

  // ── Parse response ──────────────────────────────────────────────────────
  let body: unknown;
  const contentType = res.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    body = await res.json();
  } else {
    body = await res.text();
  }

  if (!res.ok) {
    const detail =
      typeof body === "object" && body !== null
        ? (body as Record<string, unknown>).detail ?? JSON.stringify(body)
        : String(body);
    throw new APIError(res.status, detail as string, body);
  }

  return body as T;
}

// ─── Exported HTTP verbs ─────────────────────────────────────────────────────
export const api = {
  get: <T>(path: string) =>
    request<T>(path, { method: "GET" }),

  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "POST",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),

  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "PATCH",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),

  delete: <T>(path: string) =>
    request<T>(path, { method: "DELETE" }),
};
