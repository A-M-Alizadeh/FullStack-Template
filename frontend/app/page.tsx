"use client";

import { Box, Typography } from "@mui/material";

export default function Home() {
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
        {process.env.NEXT_PUBLIC_APP_NAME}
      </Typography>
    </Box>
  );
}
