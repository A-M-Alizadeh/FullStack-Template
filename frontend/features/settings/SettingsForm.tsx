"use client";

import {
  Box,
  FormControl,
  FormLabel,
  MenuItem,
  Select,
  Typography,
} from "@mui/material";

import { usePreferences } from "@/components/preferences/PreferencesProvider";
import { useT } from "@/hooks/useT";
import type { Locale, ThemeMode } from "@/lib/preferences";

export function SettingsForm() {
  const t = useT();
  const { mode, locale, setMode, setLocale } = usePreferences();

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3, maxWidth: 420 }}>
      <FormControl fullWidth>
        <FormLabel sx={{ mb: 1 }}>{t("settings.theme")}</FormLabel>
        <Select
          value={mode}
          onChange={(e) => setMode(e.target.value as ThemeMode)}
          size="small"
          aria-label={t("settings.theme")}
        >
          <MenuItem value="light">{t("settings.themeLight")}</MenuItem>
          <MenuItem value="dark">{t("settings.themeDark")}</MenuItem>
        </Select>
      </FormControl>

      <FormControl fullWidth>
        <FormLabel sx={{ mb: 1 }}>{t("settings.language")}</FormLabel>
        <Select
          value={locale}
          onChange={(e) => setLocale(e.target.value as Locale)}
          size="small"
          aria-label={t("settings.language")}
        >
          <MenuItem value="en">{t("settings.languageEn")}</MenuItem>
          <MenuItem value="it">{t("settings.languageIt")}</MenuItem>
        </Select>
      </FormControl>

      <Typography variant="body2" color="text.secondary">
        {t("settings.subtitle")}
      </Typography>
    </Box>
  );
}
