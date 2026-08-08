"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  TextField,
  Typography,
} from "@mui/material";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { getErrorMessage } from "@/lib/apiError";
import { getAppName } from "@/lib/env";
import { DEFAULT_AUTHENTICATED_PATH } from "@/lib/navigation";
import { useLazyMeQuery, useLoginMutation } from "@/store/api/authApi";

import { loginSchema, type LoginFormValues } from "./loginSchema";

export function LoginForm() {
  const router = useRouter();
  const [login, { isLoading: loggingIn }] = useLoginMutation();
  const [loadMe] = useLazyMeQuery();
  const [submitError, setSubmitError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  const busy = loggingIn;

  async function onSubmit(values: LoginFormValues) {
    setSubmitError(null);
    try {
      await login(values).unwrap();
      await loadMe().unwrap();
      router.replace(DEFAULT_AUTHENTICATED_PATH);
    } catch (error) {
      setSubmitError(getErrorMessage(error, "Invalid email or password"));
    }
  }

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(onSubmit)}
      noValidate
      sx={{ display: "flex", flexDirection: "column", gap: 2 }}
    >
      <Box>
        <Typography variant="h5" component="h1" gutterBottom>
          Sign in
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {getAppName()}
        </Typography>
      </Box>

      {submitError ? <Alert severity="error">{submitError}</Alert> : null}

      <TextField
        label="Email"
        type="email"
        autoComplete="email"
        autoFocus
        fullWidth
        error={Boolean(errors.email)}
        helperText={errors.email?.message}
        {...register("email")}
      />

      <TextField
        label="Password"
        type="password"
        autoComplete="current-password"
        fullWidth
        error={Boolean(errors.password)}
        helperText={errors.password?.message}
        {...register("password")}
      />

      <Button type="submit" disabled={busy} fullWidth size="large">
        {busy ? <CircularProgress size={22} color="inherit" /> : "Sign in"}
      </Button>
    </Box>
  );
}
