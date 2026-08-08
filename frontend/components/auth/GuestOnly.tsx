"use client";

import { Box, CircularProgress } from "@mui/material";
import { useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";

import { useAuthBootstrap } from "@/hooks/useAuthBootstrap";
import { DEFAULT_AUTHENTICATED_PATH } from "@/lib/navigation";

type GuestOnlyProps = {
  children: ReactNode;
};

/** For login: if already authenticated, send to the app. */
export function GuestOnly({ children }: GuestOnlyProps) {
  const router = useRouter();
  const boot = useAuthBootstrap();

  useEffect(() => {
    if (boot.status === "ready" && boot.result === "authenticated") {
      router.replace(DEFAULT_AUTHENTICATED_PATH);
    }
  }, [boot, router]);

  if (boot.status === "loading") {
    return (
      <Box
        sx={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (boot.result === "authenticated") {
    return null;
  }

  return children;
}
