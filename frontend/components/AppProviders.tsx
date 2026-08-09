"use client";

import { AppRouterCacheProvider } from "@mui/material-nextjs/v16-appRouter";
import type { ReactNode } from "react";

import { PreferencesProvider } from "@/components/preferences/PreferencesProvider";
import { StoreProvider } from "@/store/StoreProvider";

export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <AppRouterCacheProvider>
      <StoreProvider>
        <PreferencesProvider>{children}</PreferencesProvider>
      </StoreProvider>
    </AppRouterCacheProvider>
  );
}
