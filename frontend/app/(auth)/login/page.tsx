"use client";

import { Paper, Typography } from "@mui/material";

import { GuestOnly } from "@/components/auth/GuestOnly";
import { getAppName } from "@/lib/env";

/** Shell only — form + session wiring in the next step. */
export default function LoginPage() {
  return (
    <GuestOnly>
      <Paper sx={{ p: 4, width: "100%", maxWidth: 420 }}>
        <Typography variant="h5" component="h1" gutterBottom>
          Sign in
        </Typography>
        <Typography color="text.secondary">
          {getAppName()} — login form comes next.
        </Typography>
      </Paper>
    </GuestOnly>
  );
}
