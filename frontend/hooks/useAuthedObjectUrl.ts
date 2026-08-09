"use client";

import { useEffect, useState } from "react";

import { resolveApiAssetUrl } from "@/lib/apiUrl";
import { selectAccessToken } from "@/store/auth/authSlice";
import { useAppSelector } from "@/store/hooks";

/** Fetch an auth-gated API file and expose a blob object URL. */
export function useAuthedObjectUrl(pathOrUrl: string | null | undefined) {
  const token = useAppSelector(selectAccessToken);
  const [src, setSrc] = useState<string | null>(null);

  useEffect(() => {
    if (!pathOrUrl || !token) {
      setSrc(null);
      return;
    }
    let objectUrl: string | null = null;
    let cancelled = false;

    (async () => {
      try {
        const res = await fetch(resolveApiAssetUrl(pathOrUrl), {
          headers: { Authorization: `Bearer ${token}` },
          credentials: "include",
        });
        if (!res.ok || cancelled) return;
        const blob = await res.blob();
        objectUrl = URL.createObjectURL(blob);
        if (!cancelled) setSrc(objectUrl);
      } catch {
        if (!cancelled) setSrc(null);
      }
    })();

    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [pathOrUrl, token]);

  return src;
}
