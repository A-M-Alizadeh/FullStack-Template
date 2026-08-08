/** Back-office nav — single source for shell + tests. */

export type NavItem = {
  label: string;
  href: string;
};

export const BACKOFFICE_NAV: NavItem[] = [
  { label: "Dashboard", href: "/dashboard" },
  { label: "Products", href: "/products" },
  { label: "Analytics", href: "/analytics" },
];

export const LOGIN_PATH = "/login";
export const DEFAULT_AUTHENTICATED_PATH = "/dashboard";
