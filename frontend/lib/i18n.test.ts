import { describe, expect, it } from "vitest";

import { t } from "./i18n";

describe("t", () => {
  it("returns English by default", () => {
    expect(t("common.retry")).toBe("Retry");
    expect(t("nav.settings", "en")).toBe("Settings");
  });

  it("returns Italian for it locale", () => {
    expect(t("common.retry", "it")).toBe("Riprova");
    expect(t("nav.settings", "it")).toBe("Impostazioni");
    expect(t("settings.themeDark", "it")).toBe("Scuro");
  });
});
