import { describe, expect, it } from "vitest";

import { productSchema } from "./productSchema";

const valid = {
  name: "Demo",
  sku: "DEMO-1",
  serial_number: "SN-1",
  category: "electronics" as const,
  description: "",
  production_date: "2024-01-01",
  country_of_origin: "it",
};

describe("productSchema", () => {
  it("uppercases country and accepts valid product", () => {
    const result = productSchema.safeParse(valid);
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.country_of_origin).toBe("IT");
    }
  });

  it("rejects bad country codes", () => {
    const result = productSchema.safeParse({
      ...valid,
      country_of_origin: "ITA",
    });
    expect(result.success).toBe(false);
  });
});
