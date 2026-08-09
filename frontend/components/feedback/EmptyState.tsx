"use client";

import { Box, Button, Typography } from "@mui/material";
import Link from "next/link";
import type { ReactNode } from "react";

type Props = {
  message: string;
  actionHref?: string;
  actionLabel?: string;
  children?: ReactNode;
};

/** Quiet empty placeholder for lists / tables. */
export function EmptyState({
  message,
  actionHref,
  actionLabel,
  children,
}: Props) {
  return (
    <Box sx={{ py: 4 }}>
      <Typography color="text.secondary" gutterBottom>
        {message}
      </Typography>
      {actionHref && actionLabel ? (
        <Button component={Link} href={actionHref} variant="contained">
          {actionLabel}
        </Button>
      ) : null}
      {children}
    </Box>
  );
}
