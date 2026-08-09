import { describe, expect, it } from "vitest";

import { BACKOFFICE_NAV, navVisibleForRole } from "./navigation";

describe("navVisibleForRole", () => {
  const usersItem = BACKOFFICE_NAV.find((i) => i.href === "/users");
  const productsItem = BACKOFFICE_NAV.find((i) => i.href === "/products");

  it("marks Users as admin-only", () => {
    expect(usersItem?.roles).toEqual(["admin"]);
  });

  it("hides role-gated items from editors", () => {
    expect(navVisibleForRole(usersItem!, "editor")).toBe(false);
    expect(navVisibleForRole(usersItem!, "admin")).toBe(true);
  });

  it("shows open items to any authenticated role", () => {
    expect(navVisibleForRole(productsItem!, "editor")).toBe(true);
    expect(navVisibleForRole(productsItem!, "admin")).toBe(true);
  });

  it("hides gated items when role is unknown", () => {
    expect(navVisibleForRole(usersItem!, undefined)).toBe(false);
    expect(navVisibleForRole(productsItem!, undefined)).toBe(true);
  });
});
