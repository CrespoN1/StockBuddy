"use client";

import { useEffect, useRef, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { createClientFetch } from "@/lib/api";
import type { JobStatus } from "@/types";

const POLL_INTERVAL_MS = 2000;

/**
 * Polls GET /api/v1/analysis/jobs/{jobId} every 2 seconds until the job
 * reaches a terminal status ("completed" or "failed").
 *
 * Usage:
 * ```tsx
 * const { job, isPolling, startPolling } = useJobPolling();
 *
 * // In your mutation onSuccess:
 * onSuccess: (pendingJob) => startPolling(pendingJob),
 * ```
 */
export function useJobPolling() {
  const { getToken } = useAuth();

  const [job, setJob] = useState<JobStatus | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  function stopPolling() {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsPolling(false);
  }

  function startPolling(pendingJob: JobStatus) {
    // If job was already terminal (edge case), just set it
    if (pendingJob.status === "completed" || pendingJob.status === "failed") {
      setJob(pendingJob);
      return;
    }

    // Stop any previous polling first
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    setJob(pendingJob);
    setIsPolling(true);

    intervalRef.current = setInterval(async () => {
      try {
        const freshFetch = createClientFetch(getToken);
        const updated = await freshFetch<JobStatus>(
          `/api/v1/analysis/jobs/${pendingJob.id}`
        );
        setJob(updated);

        if (updated.status === "completed" || updated.status === "failed") {
          stopPolling();
        }
      } catch {
        stopPolling();
      }
    }, POLL_INTERVAL_MS);
  }

  function reset() {
    stopPolling();
    setJob(null);
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return { job, isPolling, startPolling, reset };
}
