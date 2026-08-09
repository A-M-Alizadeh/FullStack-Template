/** Back-office nav — single source for shell + tests. */

import type { MessageKey } from "@/lib/i18n";

export type NavItem = {
  labelKey: MessageKey;
  href: string;
};

export const BACKOFFICE_NAV: NavItem[] = [
  { labelKey: "nav.dashboard", href: "/dashboard" },
  { labelKey: "nav.products", href: "/products" },
  { labelKey: "nav.analytics", href: "/analytics" },
  { labelKey: "nav.settings", href: "/settings" },
];

export const LOGIN_PATH = "/login";
export const DEFAULT_AUTHENTICATED_PATH = "/dashboard";
