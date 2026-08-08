"use client";

import { Box, Typography } from "@mui/material";

import { getAppName } from "@/lib/env";

/** Temporary home — replaced by auth redirect / dashboard in later steps. */
export default function HomePage() {
  return (
    <Box
      component="main"
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        px: 2,
      }}
    >
      <Typography variant="h4" component="h1">
        {getAppName()}
      </Typography>
    </Box>
  );
}
