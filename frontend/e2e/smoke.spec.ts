import { expect, test, type Page } from "@playwright/test";

const adminEmail = process.env.E2E_EMAIL ?? "admin@example.com";
const adminPassword = process.env.E2E_PASSWORD ?? "admin1234";
const editorEmail = process.env.E2E_EDITOR_EMAIL ?? "editor@example.com";
const editorPassword = process.env.E2E_EDITOR_PASSWORD ?? "editor1234";

async function login(page: Page, email: string, password: string) {
  await page.goto("/login");
  await expect(page.getByRole("heading", { name: /sign in|accedi/i })).toBeVisible();
  await page.getByRole("textbox", { name: /email/i }).fill(email);
  await page.locator('input[name="password"]').fill(password);
  await page.getByRole("button", { name: /sign in|accedi/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);
}

/**
 * Happy-path smoke + role nav checks.
 * Requires API + DB with seed users (see backend README).
 */
test.describe("smoke", () => {
  test("login, open dashboard, browse products", async ({ page }) => {
    await login(page, adminEmail, adminPassword);

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

  test("admin sees Users nav and can open the page", async ({ page }) => {
    await login(page, adminEmail, adminPassword);

    const usersLink = page
      .getByRole("navigation")
      .getByRole("link", { name: /^(users|utenti)$/i });
    await expect(usersLink).toBeVisible();
    await usersLink.click();
    await expect(page).toHaveURL(/\/users/);
    await expect(
      page.getByRole("heading", { name: /^(users|utenti)$/i }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: /^(add user|aggiungi utente)$/i }),
    ).toBeVisible();
  });

  test("editor does not see Users nav", async ({ page }) => {
    await login(page, editorEmail, editorPassword);

    await expect(
      page
        .getByRole("navigation")
        .getByRole("link", { name: /^(users|utenti)$/i }),
    ).toHaveCount(0);

    await page.goto("/users");
    await expect(page).toHaveURL(/\/dashboard/);
  });
});
