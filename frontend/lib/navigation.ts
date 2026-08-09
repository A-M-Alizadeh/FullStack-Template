/** Back-office nav — single source for shell + tests. */

import type { MessageKey } from "@/lib/i18n";
import type { UserRole } from "@/types/auth";

export type NavItem = {
  labelKey: MessageKey;
  href: string;
  /** If set, only these roles see the item. Omit = all authenticated. */
  roles?: UserRole[];
};

export const BACKOFFICE_NAV: NavItem[] = [
  { labelKey: "nav.dashboard", href: "/dashboard" },
  { labelKey: "nav.products", href: "/products" },
  { labelKey: "nav.passports", href: "/passports" },
  { labelKey: "nav.analytics", href: "/analytics" },
  { labelKey: "nav.users", href: "/users", roles: ["admin"] },
  { labelKey: "nav.audit", href: "/audit", roles: ["admin"] },
  { labelKey: "nav.settings", href: "/settings" },
];

export const LOGIN_PATH = "/login";
export const DEFAULT_AUTHENTICATED_PATH = "/dashboard";

export function navVisibleForRole(
  item: NavItem,
  role: UserRole | undefined,
): boolean {
  if (!item.roles?.length) return true;
  return role != null && item.roles.includes(role);
}
