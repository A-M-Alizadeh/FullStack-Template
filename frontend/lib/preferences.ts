/** Theme + locale prefs in localStorage (no React). */

export type ThemeMode = "light" | "dark";
export type Locale = "en" | "it";

export const THEME_STORAGE_KEY = "dpp:theme";
export const LOCALE_STORAGE_KEY = "dpp:locale";

export function parseThemeMode(value: string | null): ThemeMode {
  return value === "dark" ? "dark" : "light";
}

export function parseLocale(value: string | null): Locale {
  return value === "it" ? "it" : "en";
}

export function readStoredThemeMode(): ThemeMode {
  if (typeof window === "undefined") return "light";
  return parseThemeMode(localStorage.getItem(THEME_STORAGE_KEY));
}

export function readStoredLocale(): Locale {
  if (typeof window === "undefined") return "en";
  return parseLocale(localStorage.getItem(LOCALE_STORAGE_KEY));
}
