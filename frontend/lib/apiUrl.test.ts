import { afterEach, describe, expect, it } from "vitest";

import { resolveApiAssetUrl } from "./apiUrl";

describe("resolveApiAssetUrl", () => {
  afterEach(() => {
    delete process.env.NEXT_PUBLIC_API_URL;
  });

  it("passes through absolute http(s) URLs", () => {
    process.env.NEXT_PUBLIC_API_URL = "http://localhost:8000/api/v1";
    expect(resolveApiAssetUrl("https://cdn.example/x.png")).toBe(
      "https://cdn.example/x.png",
    );
  });

  it("prefixes API origin for absolute paths", () => {
    process.env.NEXT_PUBLIC_API_URL = "http://localhost:8000/api/v1";
    expect(
      resolveApiAssetUrl("/api/v1/passport/u/images/i/file"),
    ).toBe("http://localhost:8000/api/v1/passport/u/images/i/file");
  });

  it("joins relative paths onto the API base", () => {
    process.env.NEXT_PUBLIC_API_URL = "http://localhost:8000/api/v1";
    expect(resolveApiAssetUrl("passport/u/file")).toBe(
      "http://localhost:8000/api/v1/passport/u/file",
    );
  });
});
