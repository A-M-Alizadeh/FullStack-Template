"use client";

import { Box, Typography } from "@mui/material";

import { AnalyticsView } from "@/features/analytics/AnalyticsView";

export default function AnalyticsPage() {
  return (
    <Box>
      <Typography variant="h5" component="h1" gutterBottom>
        Analytics
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        QR scan activity from passport links with <code>?src=qr</code>.
      </Typography>
      <AnalyticsView />
    </Box>
  );
}
