"use client";

import { Box, Typography } from "@mui/material";

import { DashboardView } from "@/features/dashboard/DashboardView";
import { useT } from "@/hooks/useT";

export default function DashboardPage() {
  const t = useT();

  return (
    <Box>
      <Typography variant="h5" component="h1" gutterBottom>
        {t("dashboard.title")}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        {t("dashboard.subtitle")}
      </Typography>
      <DashboardView />
    </Box>
  );
}
