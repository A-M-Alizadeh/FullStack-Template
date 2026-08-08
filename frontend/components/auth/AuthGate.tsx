"use client";

import { Box, CircularProgress } from "@mui/material";
import { useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";

import { useAuthBootstrap } from "@/hooks/useAuthBootstrap";
import { LOGIN_PATH } from "@/lib/navigation";

type AuthGateProps = {
  children: ReactNode;
};

/** Blocks back-office UI until session bootstrap finishes; redirects if anonymous. */
export function AuthGate({ children }: AuthGateProps) {
  const router = useRouter();
  const boot = useAuthBootstrap();

  useEffect(() => {
    if (boot.status === "ready" && boot.result === "anonymous") {
      router.replace(LOGIN_PATH);
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

  if (boot.result === "anonymous") {
    return null;
  }

  return children;
}
