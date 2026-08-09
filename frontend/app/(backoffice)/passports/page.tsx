"use client";

import { Box, Typography } from "@mui/material";

import { PassportsList } from "@/features/passports/PassportsList";
import { useT } from "@/hooks/useT";

export default function PassportsPage() {
  const t = useT();

  return (
    <Box>
      <Typography variant="h5" component="h1" gutterBottom>
        {t("passports.title")}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        {t("passports.subtitle")}
      </Typography>
      <PassportsList />
    </Box>
  );
}
