import { describe, expect, it } from "vitest";

import { parseLocale, parseThemeMode } from "./preferences";

describe("parseThemeMode", () => {
  it("accepts dark, otherwise light", () => {
    expect(parseThemeMode("dark")).toBe("dark");
    expect(parseThemeMode("light")).toBe("light");
    expect(parseThemeMode(null)).toBe("light");
    expect(parseThemeMode("weird")).toBe("light");
  });
});

describe("parseLocale", () => {
  it("accepts it, otherwise en", () => {
    expect(parseLocale("it")).toBe("it");
    expect(parseLocale("en")).toBe("en");
    expect(parseLocale(null)).toBe("en");
    expect(parseLocale("fr")).toBe("en");
  });
});
