"use client";

import { Box, Typography } from "@mui/material";

import { SettingsForm } from "@/features/settings/SettingsForm";
import { useT } from "@/hooks/useT";

export default function SettingsPage() {
  const t = useT();

  return (
    <Box>
      <Typography variant="h5" component="h1" gutterBottom>
        {t("settings.title")}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        {t("settings.subtitle")}
      </Typography>
      <SettingsForm />
    </Box>
  );
}
