"use client";

import { useEffect, useState } from "react";

import { bootstrapSession, type BootstrapResult } from "@/lib/authSession";
import { useLazyMeQuery, useRefreshMutation } from "@/store/api/authApi";
import { selectAccessToken } from "@/store/auth/authSlice";
import { useAppSelector } from "@/store/hooks";

export type AuthBootstrapState =
  | { status: "loading" }
  | { status: "ready"; result: BootstrapResult };

/**
 * Restores access via refresh cookie (if needed), then loads /me.
 */
export function useAuthBootstrap(): AuthBootstrapState {
  const accessToken = useAppSelector(selectAccessToken);
  const [refresh] = useRefreshMutation();
  const [loadMe] = useLazyMeQuery();
  const [state, setState] = useState<AuthBootstrapState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    (async () => {
      const result = await bootstrapSession({
        hasAccessToken: Boolean(accessToken),
        refresh: () => refresh().unwrap(),
        loadMe: () => loadMe().unwrap(),
      });
      if (!cancelled) {
        setState({ status: "ready", result });
      }
    })();

    return () => {
      cancelled = true;
    };
    // Run once on mount for the back-office shell.
    // eslint-disable-next-line react-hooks/exhaustive-deps -- bootstrap once per mount
  }, []);

  return state;
}
