import { configureStore } from "@reduxjs/toolkit";
import { render, type RenderOptions } from "@testing-library/react";
import { Provider } from "react-redux";
import type { ReactElement, ReactNode } from "react";

import { PreferencesProvider } from "@/components/preferences/PreferencesProvider";
import { baseApi } from "@/store/api/baseApi";
import authReducer, { type AuthState } from "@/store/auth/authSlice";
import type { User } from "@/types/auth";

function PreferencesOnly({ children }: { children: ReactNode }) {
  return <PreferencesProvider>{children}</PreferencesProvider>;
}

/** RTL render wrapped with preferences (theme + locale). */
export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, "wrapper">,
) {
  return render(ui, { wrapper: PreferencesOnly, ...options });
}

type StoreOptions = {
  user?: User | null;
  accessToken?: string | null;
};

/** RTL render with Redux auth preloaded (for gates / role UI). */
export function renderWithStore(
  ui: ReactElement,
  storeOptions: StoreOptions = {},
  options?: Omit<RenderOptions, "wrapper">,
) {
  const user = storeOptions.user ?? null;
  const accessToken =
    storeOptions.accessToken !== undefined
      ? storeOptions.accessToken
      : user
        ? "test-token"
        : null;

  const preloadedAuth: AuthState = { accessToken, user };

  const store = configureStore({
    reducer: {
      auth: authReducer,
      [baseApi.reducerPath]: baseApi.reducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware({
        serializableCheck: false,
      }).concat(baseApi.middleware),
    preloadedState: { auth: preloadedAuth },
  });

  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <Provider store={store}>
        <PreferencesProvider>{children}</PreferencesProvider>
      </Provider>
    );
  }

  return {
    store,
    ...render(ui, { wrapper: Wrapper, ...options }),
  };
}
