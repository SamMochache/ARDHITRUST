// src/hooks/useApi.ts
// ─────────────────────────────────────────────────────────────────────────────
// Generic hook: useQuery for fetching, useMutation for writing.
// Both surface loading / error state.  No external library needed.
// ─────────────────────────────────────────────────────────────────────────────

import { useState, useEffect, useCallback, useRef } from "react";
import { APIError } from "../api/client";

// ─── useQuery ────────────────────────────────────────────────────────────────
// Fires on mount (and whenever `key` changes).  Pass key=null to skip.
export function useQuery<T>(
  fetcher: () => Promise<T>,
  key: unknown // changing this re-fetches; null skips
) {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(key !== null);
  const [error, setError] = useState<string | null>(null);
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  const refetch = useCallback(() => {
    if (key === null) return;
    setIsLoading(true);
    setError(null);
    fetcherRef
      .current()
      .then(setData)
      .catch((err: unknown) => {
        setError(err instanceof APIError ? err.detail : "Something went wrong.");
      })
      .finally(() => setIsLoading(false));
  }, [key]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { data, isLoading, error, refetch };
}

// ─── useMutation ─────────────────────────────────────────────────────────────
// Returns [mutate, { isLoading, error, data }]
export function useMutation<TInput, TOutput>(
  mutator: (input: TInput) => Promise<TOutput>
) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<TOutput | null>(null);
  const mutatorRef = useRef(mutator);
  mutatorRef.current = mutator;

  const mutate = useCallback(
    async (input: TInput): Promise<TOutput | null> => {
      setIsLoading(true);
      setError(null);
      try {
        const result = await mutatorRef.current(input);
        setData(result);
        return result;
      } catch (err: unknown) {
        const msg =
          err instanceof APIError ? err.detail : "Something went wrong.";
        setError(msg);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return [mutate, { isLoading, error, data }] as const;
}

// ─────────────────────────────────────────────────────────────────────────────
// Domain-specific convenience hooks
// ─────────────────────────────────────────────────────────────────────────────

import { propertyApi, agentApi, verificationApi, Property } from "../api/endpoints";

/** Fetch paginated public property listings with optional filters */
export function useProperties(filters?: Record<string, string | number>) {
  const key = JSON.stringify(filters ?? {});
  return useQuery(() => propertyApi.list(filters), key);
}

/** Fetch a single property detail */
export function useProperty(id: string | null) {
  return useQuery(() => propertyApi.detail(id!), id);
}

/** Get Ardhisasa verification result for a property */
export function useVerification(propertyId: string | null) {
  return useQuery(() => verificationApi.status(propertyId!), propertyId);
}

/** Run AI valuation on a property */
export function useValuation(propertyId: string | null) {
  return useQuery(() => agentApi.valuation(propertyId!), propertyId);
}
