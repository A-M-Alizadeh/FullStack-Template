import { useCallback } from "react";

import { usePreferences } from "@/components/preferences/PreferencesProvider";
import { t, type MessageKey } from "@/lib/i18n";

/** Translate with the active locale from preferences. */
export function useT() {
  const { locale } = usePreferences();
  return useCallback((key: MessageKey) => t(key, locale), [locale]);
}

export type { MessageKey };
