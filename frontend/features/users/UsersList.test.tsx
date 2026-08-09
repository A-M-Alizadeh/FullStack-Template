import { cleanup, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithStore } from "@/test/render";
import type { User } from "@/types/auth";

import { UsersList } from "./UsersList";

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
  created_at: "2024-02-01T00:00:00Z",
};

const refetch = vi.fn();
const deleteUnwrap = vi.fn();
const deleteUser = vi.fn(() => ({ unwrap: deleteUnwrap }));

vi.mock("@/store/api/usersApi", async () => {
  const actual = await vi.importActual<typeof import("@/store/api/usersApi")>(
    "@/store/api/usersApi",
  );
  return {
    ...actual,
    useListUsersQuery: () => ({
      data: [admin, editor],
      isLoading: false,
      isError: false,
      error: undefined,
      refetch,
    }),
    useDeleteUserMutation: () => [deleteUser, { isLoading: false }],
    useCreateUserMutation: () => [vi.fn(() => ({ unwrap: vi.fn() })), { isLoading: false }],
    useUpdateUserMutation: () => [vi.fn(() => ({ unwrap: vi.fn() })), { isLoading: false }],
  };
});

describe("UsersList", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    localStorage.clear();
    refetch.mockReset();
    deleteUser.mockClear();
    deleteUnwrap.mockReset();
    deleteUnwrap.mockResolvedValue(undefined);
  });

  it("lists users and exposes create", () => {
    renderWithStore(<UsersList />, { user: admin });

    expect(screen.getByRole("button", { name: "Add user" })).toBeInTheDocument();
    expect(screen.getByText("admin@example.com")).toBeInTheDocument();
    expect(screen.getByText("editor@example.com")).toBeInTheDocument();
  });

  it("disables delete for the signed-in admin", () => {
    renderWithStore(<UsersList />, { user: admin });

    const rows = screen.getAllByRole("row");
    const adminRow = rows.find((row) =>
      within(row).queryByText("admin@example.com"),
    );
    expect(adminRow).toBeTruthy();
    expect(
      within(adminRow!).getByRole("button", { name: "Delete" }),
    ).toBeDisabled();
  });

  it("opens the create dialog", async () => {
    const user = userEvent.setup();
    renderWithStore(<UsersList />, { user: admin });

    await user.click(screen.getByRole("button", { name: "Add user" }));

    const dialog = await screen.findByRole("dialog");
    expect(
      within(dialog).getByRole("heading", { name: "Add user" }),
    ).toBeInTheDocument();
    expect(
      within(dialog).getByRole("textbox", { name: /email/i }),
    ).toBeInTheDocument();
    expect(within(dialog).getByRole("combobox")).toBeInTheDocument();
  });
});
