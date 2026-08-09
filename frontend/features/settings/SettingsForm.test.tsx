import { cleanup, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import {
  LOCALE_STORAGE_KEY,
  THEME_STORAGE_KEY,
} from "@/lib/preferences";
import { renderWithProviders } from "@/test/render";

import { SettingsForm } from "./SettingsForm";

describe("SettingsForm", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    localStorage.clear();
  });

  it("renders theme and language controls", () => {
    renderWithProviders(<SettingsForm />);

    expect(screen.getByText("Theme")).toBeInTheDocument();
    expect(screen.getByText("Language")).toBeInTheDocument();
    expect(
      screen.getByText("Appearance and language for this browser."),
    ).toBeInTheDocument();
  });

  it("switches language to Italian and persists", async () => {
    const user = userEvent.setup();
    renderWithProviders(<SettingsForm />);

    const languageSelect = screen.getByLabelText("Language");
    await user.click(languageSelect);

    const listbox = await screen.findByRole("listbox");
    await user.click(within(listbox).getByText("Italiano"));

    expect(await screen.findByText("Tema")).toBeInTheDocument();
    expect(screen.getByText("Lingua")).toBeInTheDocument();
    expect(localStorage.getItem(LOCALE_STORAGE_KEY)).toBe("it");
  });

  it("switches theme to dark and persists", async () => {
    const user = userEvent.setup();
    localStorage.setItem(LOCALE_STORAGE_KEY, "en");
    renderWithProviders(<SettingsForm />);

    // Wait for hydration from localStorage (en).
    expect(await screen.findByText("Theme")).toBeInTheDocument();

    const themeSelect = screen.getByLabelText("Theme");
    await user.click(themeSelect);

    const listbox = await screen.findByRole("listbox");
    await user.click(within(listbox).getByRole("option", { name: /Dark|Scuro/ }));

    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe("dark");
  });
});
