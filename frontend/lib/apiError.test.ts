import { describe, expect, it } from "vitest";

import { getErrorMessage } from "./apiError";

describe("getErrorMessage", () => {
  it("returns fallback for non-objects", () => {
    expect(getErrorMessage(null, "fallback")).toBe("fallback");
    expect(getErrorMessage("x", "fallback")).toBe("fallback");
  });

  it("reads string detail from FastAPI payload", () => {
    expect(
      getErrorMessage({ data: { detail: "Invalid credentials" } }, "fallback"),
    ).toBe("Invalid credentials");
  });

  it("joins validation detail messages", () => {
    expect(
      getErrorMessage(
        {
          data: {
            detail: [
              { loc: ["body", "sku"], msg: "Field required", type: "missing" },
              { loc: ["body", "name"], msg: "String too short", type: "value" },
            ],
          },
        },
        "fallback",
      ),
    ).toBe("Field required; String too short");
  });

  it("reads FetchBaseQuery error string", () => {
    expect(getErrorMessage({ error: "Network Error" }, "fallback")).toBe(
      "Network Error",
    );
  });

  it("maps 404 status", () => {
    expect(getErrorMessage({ status: 404 }, "fallback")).toBe("Not found");
  });
});
