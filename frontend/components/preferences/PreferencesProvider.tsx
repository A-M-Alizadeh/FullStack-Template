"use client";

import { CssBaseline, ThemeProvider } from "@mui/material";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  LOCALE_STORAGE_KEY,
  THEME_STORAGE_KEY,
  parseLocale,
  parseThemeMode,
  type Locale,
  type ThemeMode,
} from "@/lib/preferences";
import { createAppTheme } from "@/theme/createAppTheme";

type PreferencesContextValue = {
  mode: ThemeMode;
  locale: Locale;
  setMode: (mode: ThemeMode) => void;
  setLocale: (locale: Locale) => void;
};

const PreferencesContext = createContext<PreferencesContextValue | null>(null);

export function PreferencesProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<ThemeMode>("light");
  const [locale, setLocaleState] = useState<Locale>("en");
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setModeState(parseThemeMode(localStorage.getItem(THEME_STORAGE_KEY)));
    setLocaleState(parseLocale(localStorage.getItem(LOCALE_STORAGE_KEY)));
    setHydrated(true);
  }, []);

  const setMode = useCallback((next: ThemeMode) => {
    setModeState(next);
    localStorage.setItem(THEME_STORAGE_KEY, next);
  }, []);

  const setLocale = useCallback((next: Locale) => {
    setLocaleState(next);
    localStorage.setItem(LOCALE_STORAGE_KEY, next);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    document.documentElement.lang = locale;
    document.documentElement.dataset.colorScheme = mode;
  }, [hydrated, locale, mode]);

  const theme = useMemo(() => createAppTheme(mode), [mode]);

  const value = useMemo(
    () => ({ mode, locale, setMode, setLocale }),
    [mode, locale, setMode, setLocale],
  );

  return (
    <PreferencesContext.Provider value={value}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </PreferencesContext.Provider>
  );
}

export function usePreferences(): PreferencesContextValue {
  const ctx = useContext(PreferencesContext);
  if (!ctx) {
    throw new Error("usePreferences must be used within PreferencesProvider");
  }
  return ctx;
}
