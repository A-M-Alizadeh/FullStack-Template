import { describe, expect, it } from "vitest";

import { loginSchema } from "./loginSchema";

describe("loginSchema", () => {
  it("accepts a valid payload", () => {
    const result = loginSchema.safeParse({
      email: "admin@example.com",
      password: "admin1234",
    });
    expect(result.success).toBe(true);
  });

  it("rejects empty password and bad email", () => {
    const result = loginSchema.safeParse({
      email: "not-an-email",
      password: "",
    });
    expect(result.success).toBe(false);
  });
});
