"use client";

import { Box, Typography } from "@mui/material";

import { DashboardView } from "@/features/dashboard/DashboardView";

export default function DashboardPage() {
  return (
    <Box>
      <Typography variant="h5" component="h1" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Overview of products, passports, and QR activity.
      </Typography>
      <DashboardView />
    </Box>
  );
}
