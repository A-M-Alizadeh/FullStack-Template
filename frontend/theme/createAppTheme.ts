"use client";

import { createTheme, type Theme } from "@mui/material/styles";

import type { ThemeMode } from "@/lib/preferences";

export function createAppTheme(mode: ThemeMode): Theme {
  const dark = mode === "dark";

  return createTheme({
    palette: {
      mode,
      primary: {
        main: dark ? "#6ea8e8" : "#1a56a0",
      },
      background: dark
        ? { default: "#121418", paper: "#1a1d24" }
        : { default: "#f5f7fa", paper: "#ffffff" },
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
}
