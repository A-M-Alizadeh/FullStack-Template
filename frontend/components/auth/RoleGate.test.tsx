import { cleanup, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithStore } from "@/test/render";
import type { User } from "@/types/auth";

import { RoleGate } from "./RoleGate";

const replace = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace, push: vi.fn() }),
}));

const admin: User = {
  id: "a1",
  email: "admin@example.com",
  role: "admin",
  created_at: "2024-01-01T00:00:00Z",
};

const editor: User = {
  id: "e1",
  email: "editor@example.com",
  role: "editor",
  created_at: "2024-01-01T00:00:00Z",
};

describe("RoleGate", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    replace.mockReset();
  });

  it("renders children when the user role is allowed", () => {
    renderWithStore(
      <RoleGate roles={["admin"]}>
        <div>admin only</div>
      </RoleGate>,
      { user: admin },
    );

    expect(screen.getByText("admin only")).toBeInTheDocument();
    expect(replace).not.toHaveBeenCalled();
  });

  it("allows either role when both are listed", () => {
    renderWithStore(
      <RoleGate roles={["admin", "editor"]}>
        <div>shared area</div>
      </RoleGate>,
      { user: editor },
    );

    expect(screen.getByText("shared area")).toBeInTheDocument();
    expect(replace).not.toHaveBeenCalled();
  });

  it("redirects when the role is not allowed", async () => {
    renderWithStore(
      <RoleGate roles={["admin"]}>
        <div>admin only</div>
      </RoleGate>,
      { user: editor },
    );

    expect(screen.queryByText("admin only")).not.toBeInTheDocument();
    await waitFor(() => {
      expect(replace).toHaveBeenCalledWith("/dashboard");
    });
  });
});
