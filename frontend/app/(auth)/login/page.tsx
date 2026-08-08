"use client";

import { Paper } from "@mui/material";

import { GuestOnly } from "@/components/auth/GuestOnly";
import { LoginForm } from "@/features/auth/LoginForm";

export default function LoginPage() {
  return (
    <GuestOnly>
      <Paper sx={{ p: 4, width: "100%", maxWidth: 420 }}>
        <LoginForm />
      </Paper>
    </GuestOnly>
  );
}
