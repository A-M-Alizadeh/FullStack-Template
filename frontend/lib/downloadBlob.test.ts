import { describe, expect, it } from "vitest";

import { filenameFromContentDisposition } from "./downloadBlob";

describe("filenameFromContentDisposition", () => {
  it("uses fallback when header missing", () => {
    expect(filenameFromContentDisposition(null, "qr.png")).toBe("qr.png");
  });

  it("parses quoted filename", () => {
    expect(
      filenameFromContentDisposition(
        'attachment; filename="abc-123.png"',
        "qr.png",
      ),
    ).toBe("abc-123.png");
  });

  it("parses unquoted filename", () => {
    expect(
      filenameFromContentDisposition(
        "attachment; filename=passport.png",
        "qr.png",
      ),
    ).toBe("passport.png");
  });
});
