import { cleanup, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithStore } from "@/test/render";
import type { User } from "@/types/auth";

import { AdminGate } from "./AdminGate";

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

describe("AdminGate", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    replace.mockReset();
  });

  it("renders children for admins", () => {
    renderWithStore(
      <AdminGate>
        <div>secret admin area</div>
      </AdminGate>,
      { user: admin },
    );

    expect(screen.getByText("secret admin area")).toBeInTheDocument();
    expect(replace).not.toHaveBeenCalled();
  });

  it("redirects editors to the dashboard", async () => {
    renderWithStore(
      <AdminGate>
        <div>secret admin area</div>
      </AdminGate>,
      { user: editor },
    );

    expect(screen.queryByText("secret admin area")).not.toBeInTheDocument();
    await waitFor(() => {
      expect(replace).toHaveBeenCalledWith("/dashboard");
    });
  });
});
