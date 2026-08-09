"use client";

import { Box, CircularProgress } from "@mui/material";
import { useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";

import { DEFAULT_AUTHENTICATED_PATH } from "@/lib/navigation";
import { selectUser } from "@/store/auth/authSlice";
import { useAppSelector } from "@/store/hooks";

type Props = { children: ReactNode };

/** Admin-only pages — editors are sent back to the dashboard. */
export function AdminGate({ children }: Props) {
  const router = useRouter();
  const user = useAppSelector(selectUser);

  useEffect(() => {
    if (user && user.role !== "admin") {
      router.replace(DEFAULT_AUTHENTICATED_PATH);
    }
  }, [user, router]);

  if (!user) {
    return (
      <Box
        sx={{
          minHeight: 240,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (user.role !== "admin") {
    return null;
  }

  return children;
}
