"use client";

import { Box, Button, Skeleton, Typography } from "@mui/material";
import Link from "next/link";

import { QueryError } from "@/components/feedback/QueryError";
import { useT } from "@/hooks/useT";
import type { MessageKey } from "@/lib/i18n";
import { useGetDashboardQuery } from "@/store/api/dashboardApi";
import type { DashboardSummary } from "@/types/dashboard";

const METRICS: { key: keyof DashboardSummary; labelKey: MessageKey }[] = [
  { key: "total_products", labelKey: "dashboard.totalProducts" },
  { key: "published_passports", labelKey: "dashboard.publishedPassports" },
  { key: "generated_qr_codes", labelKey: "dashboard.generatedQr" },
  { key: "total_passport_views", labelKey: "dashboard.passportViews" },
];

export function DashboardView() {
  const t = useT();
  const { data, isLoading, isError, error, refetch } = useGetDashboardQuery();

  if (isLoading) {
    return (
      <Box
        sx={{
          display: "grid",
          gap: 2,
          gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr" },
        }}
      >
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} variant="rounded" height={96} />
        ))}
      </Box>
    );
  }

  if (isError || !data) {
    return (
      <QueryError
        error={error}
        fallbackKey="dashboard.loadError"
        onRetry={() => refetch()}
      />
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <Box
        sx={{
          display: "grid",
          gap: 2,
          gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr" },
        }}
      >
        {METRICS.map(({ key, labelKey }) => (
          <Box
            key={key}
            sx={{
              p: 2.5,
              border: 1,
              borderColor: "divider",
              borderRadius: 1,
              bgcolor: "background.paper",
            }}
          >
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {t(labelKey)}
            </Typography>
            <Typography variant="h4" component="p">
              {data[key]}
            </Typography>
          </Box>
        ))}
      </Box>

      <Box sx={{ display: "flex", gap: 1.5, flexWrap: "wrap" }}>
        <Button component={Link} href="/products" variant="contained">
          {t("dashboard.manageProducts")}
        </Button>
        <Button component={Link} href="/analytics" variant="outlined">
          {t("dashboard.viewAnalytics")}
        </Button>
      </Box>
    </Box>
  );
}
