"use client";

import { Box, CircularProgress } from "@mui/material";
import { useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";

import { DEFAULT_AUTHENTICATED_PATH } from "@/lib/navigation";
import { selectUser } from "@/store/auth/authSlice";
import { useAppSelector } from "@/store/hooks";
import type { UserRole } from "@/types/auth";

type Props = {
  /** Allowed roles. Anyone else is redirected to the dashboard. */
  roles: UserRole[];
  children: ReactNode;
};

/**
 * Page-level role gate. Pair with nav `roles` and API `Require*` deps —
 * UI hide is not security; the API still enforces access.
 */
export function RoleGate({ roles, children }: Props) {
  const router = useRouter();
  const user = useAppSelector(selectUser);
  const allowed = user != null && roles.includes(user.role);

  useEffect(() => {
    if (user && !roles.includes(user.role)) {
      router.replace(DEFAULT_AUTHENTICATED_PATH);
    }
  }, [user, roles, router]);

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

  if (!allowed) {
    return null;
  }

  return children;
}
