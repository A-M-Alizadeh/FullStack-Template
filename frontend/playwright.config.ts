import { defineConfig, devices } from "@playwright/test";

/**
 * E2E smoke against a running stack:
 * - Postgres + API on :8000 (seeded users)
 * - Next on :3000 (started here if not already up)
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: "list",
  timeout: 60_000,
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    headless: process.env.PLAYWRIGHT_HEADED === "1" ? false : undefined,
    launchOptions: {
      // Watch the run: PLAYWRIGHT_HEADED=1 PLAYWRIGHT_SLOW_MO=500 npm run test:e2e
      slowMo: Number(process.env.PLAYWRIGHT_SLOW_MO || 0) || 0,
    },
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
