"use client";

import { createTheme } from "@mui/material/styles";

/** Single MUI theme — extend palette / typography here as the app grows. */
export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1a56a0",
    },
    background: {
      default: "#f5f7fa",
      paper: "#ffffff",
    },
  },
  shape: {
    borderRadius: 8,
  },
  typography: {
    fontFamily: [
      "Segoe UI",
      "Roboto",
      "Helvetica",
      "Arial",
      "sans-serif",
    ].join(","),
    h4: {
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      defaultProps: {
        variant: "contained",
      },
    },
  },
});
