import { expect, test } from "@playwright/test";

const email = process.env.E2E_EMAIL ?? "admin@example.com";
const password = process.env.E2E_PASSWORD ?? "admin1234";

/**
 * Happy-path smoke: login → dashboard → products.
 * Requires API + DB with seed users (see backend README).
 */
test.describe("smoke", () => {
  test("login, open dashboard, browse products", async ({ page }) => {
    await page.goto("/login");

    await expect(page.getByRole("heading", { name: /sign in|accedi/i })).toBeVisible();

    await page.getByRole("textbox", { name: /email/i }).fill(email);
    await page.locator('input[name="password"]').fill(password);
    await page.getByRole("button", { name: /sign in|accedi/i }).click();

    await expect(page).toHaveURL(/\/dashboard/);
    await expect(
      page.getByRole("heading", { name: /dashboard/i }),
    ).toBeVisible();

    await page
      .getByRole("navigation")
      .getByRole("link", { name: /^(products|prodotti)$/i })
      .click();
    await expect(page).toHaveURL(/\/products/);
    await expect(
      page.getByRole("heading", { name: /^(products|prodotti)$/i }),
    ).toBeVisible();

    // List loaded (table or empty-state / new-product CTA).
    const hasTable = await page.getByRole("table").count();
    const hasCreate = await page
      .getByRole("link", { name: /^(new product|create product|nuovo prodotto|crea prodotto)$/i })
      .count();
    expect(hasTable + hasCreate).toBeGreaterThan(0);
  });
});
