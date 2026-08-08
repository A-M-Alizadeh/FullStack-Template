"use client";

import {
  Alert,
  Box,
  Button,
  Skeleton,
  Typography,
} from "@mui/material";
import Link from "next/link";

import { getErrorMessage } from "@/lib/apiError";
import { useGetDashboardQuery } from "@/store/api/dashboardApi";
import type { DashboardSummary } from "@/types/dashboard";

const METRICS: { key: keyof DashboardSummary; label: string }[] = [
  { key: "total_products", label: "Total products" },
  { key: "published_passports", label: "Published passports" },
  { key: "generated_qr_codes", label: "Generated QR codes" },
  { key: "total_passport_views", label: "Passport views (QR scans)" },
];

export function DashboardView() {
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
      <Alert
        severity="error"
        action={
          <Button color="inherit" size="small" onClick={() => refetch()}>
            Retry
          </Button>
        }
      >
        {getErrorMessage(error, "Could not load dashboard")}
      </Alert>
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
        {METRICS.map(({ key, label }) => (
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
              {label}
            </Typography>
            <Typography variant="h4" component="p">
              {data[key]}
            </Typography>
          </Box>
        ))}
      </Box>

      <Box sx={{ display: "flex", gap: 1.5, flexWrap: "wrap" }}>
        <Button component={Link} href="/products" variant="contained">
          Manage products
        </Button>
        <Button component={Link} href="/analytics" variant="outlined">
          View analytics
        </Button>
      </Box>
    </Box>
  );
}
