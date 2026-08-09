import { cleanup, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "@/test/render";

import { LoginForm } from "./LoginForm";

const replace = vi.fn();
const loginUnwrap = vi.fn();
const login = vi.fn(() => ({ unwrap: loginUnwrap }));
const loadMeUnwrap = vi.fn();
const loadMe = vi.fn(() => ({ unwrap: loadMeUnwrap }));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace, push: vi.fn() }),
}));

vi.mock("@/store/api/authApi", () => ({
  useLoginMutation: () => [login, { isLoading: false }],
  useLazyMeQuery: () => [loadMe],
}));

vi.mock("@/lib/env", () => ({
  getAppName: () => "Test DPP",
}));

describe("LoginForm", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    localStorage.clear();
    replace.mockReset();
    login.mockClear();
    loginUnwrap.mockReset();
    loadMe.mockClear();
    loadMeUnwrap.mockReset();
    loginUnwrap.mockResolvedValue({ access_token: "token" });
    loadMeUnwrap.mockResolvedValue({
      id: "1",
      email: "admin@example.com",
      role: "admin",
    });
  });

  it("renders sign-in fields", () => {
    const { container } = renderWithProviders(<LoginForm />);
    const view = within(container);

    expect(view.getByRole("heading", { name: "Sign in" })).toBeInTheDocument();
    expect(view.getByRole("textbox", { name: "Email" })).toBeInTheDocument();
    expect(container.querySelector('input[name="password"]')).toBeTruthy();
    expect(view.getByText("Test DPP")).toBeInTheDocument();
  });

  it("shows validation errors when submitted empty", async () => {
    const user = userEvent.setup();
    const { container } = renderWithProviders(<LoginForm />);
    const view = within(container);

    await user.click(view.getByRole("button", { name: "Sign in" }));

    expect(await view.findByText("Enter a valid email")).toBeInTheDocument();
    expect(view.getByText("Password is required")).toBeInTheDocument();
    expect(login).not.toHaveBeenCalled();
  });

  it("logs in and redirects on valid submit", async () => {
    const user = userEvent.setup();
    const { container } = renderWithProviders(<LoginForm />);
    const view = within(container);

    await user.type(view.getByRole("textbox", { name: "Email" }), "admin@example.com");
    await user.type(
      container.querySelector('input[name="password"]') as HTMLElement,
      "admin1234",
    );
    await user.click(view.getByRole("button", { name: "Sign in" }));

    await waitFor(() => {
      expect(login).toHaveBeenCalledWith({
        email: "admin@example.com",
        password: "admin1234",
      });
    });
    expect(loadMe).toHaveBeenCalled();
    expect(replace).toHaveBeenCalledWith("/dashboard");
  });

  it("shows API error on failed login", async () => {
    loginUnwrap.mockRejectedValue({ data: { detail: "Invalid credentials" } });
    const user = userEvent.setup();
    const { container } = renderWithProviders(<LoginForm />);
    const view = within(container);

    await user.type(view.getByRole("textbox", { name: "Email" }), "admin@example.com");
    await user.type(
      container.querySelector('input[name="password"]') as HTMLElement,
      "wrong",
    );
    await user.click(view.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByText("Invalid credentials")).toBeInTheDocument();
    expect(replace).not.toHaveBeenCalled();
  });
});
