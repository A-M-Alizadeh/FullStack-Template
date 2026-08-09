"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  FormControl,
  MenuItem,
  Select,
  TextField,
  Typography,
} from "@mui/material";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { usePreferences } from "@/components/preferences/PreferencesProvider";
import { useT } from "@/hooks/useT";
import { getErrorMessage } from "@/lib/apiError";
import { getAppName } from "@/lib/env";
import { DEFAULT_AUTHENTICATED_PATH } from "@/lib/navigation";
import type { Locale, ThemeMode } from "@/lib/preferences";
import { useLazyMeQuery, useLoginMutation } from "@/store/api/authApi";

import { loginSchema, type LoginFormValues } from "./loginSchema";

export function LoginForm() {
  const t = useT();
  const { mode, locale, setMode, setLocale } = usePreferences();
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
      setSubmitError(getErrorMessage(error, t("auth.invalidCredentials")));
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
          {t("auth.signIn")}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {getAppName()}
        </Typography>
      </Box>

      {submitError ? <Alert severity="error">{submitError}</Alert> : null}

      <TextField
        label={t("auth.email")}
        type="email"
        autoComplete="email"
        autoFocus
        fullWidth
        error={Boolean(errors.email)}
        helperText={errors.email?.message}
        {...register("email")}
      />

      <TextField
        label={t("auth.password")}
        type="password"
        autoComplete="current-password"
        fullWidth
        error={Boolean(errors.password)}
        helperText={errors.password?.message}
        {...register("password")}
      />

      <Button type="submit" disabled={busy} fullWidth size="large">
        {busy ? <CircularProgress size={22} color="inherit" /> : t("auth.signIn")}
      </Button>

      <Box sx={{ display: "flex", gap: 1.5, pt: 1 }}>
        <FormControl size="small" fullWidth>
          <Select
            value={locale}
            onChange={(e) => setLocale(e.target.value as Locale)}
            aria-label={t("settings.language")}
          >
            <MenuItem value="en">{t("settings.languageEn")}</MenuItem>
            <MenuItem value="it">{t("settings.languageIt")}</MenuItem>
          </Select>
        </FormControl>
        <FormControl size="small" fullWidth>
          <Select
            value={mode}
            onChange={(e) => setMode(e.target.value as ThemeMode)}
            aria-label={t("settings.theme")}
          >
            <MenuItem value="light">{t("settings.themeLight")}</MenuItem>
            <MenuItem value="dark">{t("settings.themeDark")}</MenuItem>
          </Select>
        </FormControl>
      </Box>
    </Box>
  );
}
