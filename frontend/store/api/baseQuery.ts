/**
 * HTTP base query + single-flight refresh on 401.
 * Pure-ish module: no React — easy to unit-test with a mock fetch.
 */

import {
  type BaseQueryFn,
  type FetchArgs,
  type FetchBaseQueryError,
  fetchBaseQuery,
} from "@reduxjs/toolkit/query";

import { getApiBaseUrl } from "@/lib/env";
import type { AccessTokenResponse } from "@/types/auth";

import { clearAuth, selectAccessToken, setAccessToken } from "../auth/authSlice";

type AppBaseQuery = BaseQueryFn<
  string | FetchArgs,
  unknown,
  FetchBaseQueryError
>;

/** Lazy so importing the store during SSR/build does not require env yet. */
function getRawBaseQuery(): AppBaseQuery {
  return fetchBaseQuery({
    baseUrl: getApiBaseUrl(),
    credentials: "include",
    prepareHeaders: (headers, { getState }) => {
      const token = selectAccessToken(
        getState() as { auth: { accessToken: string | null } },
      );
      if (token) {
        headers.set("Authorization", `Bearer ${token}`);
      }
      return headers;
    },
  });
}

function requestUrl(args: string | FetchArgs): string {
  return typeof args === "string" ? args : args.url;
}

/** Endpoints that must not trigger a refresh retry. */
export function shouldSkipReauth(url: string): boolean {
  return (
    url.includes("/auth/login") ||
    url.includes("/auth/refresh") ||
    url.includes("/auth/logout")
  );
}

let refreshInFlight: Promise<boolean> | null = null;

async function refreshAccessToken(
  api: Parameters<AppBaseQuery>[1],
  extraOptions: Parameters<AppBaseQuery>[2],
): Promise<boolean> {
  if (!refreshInFlight) {
    refreshInFlight = (async () => {
      const result = await getRawBaseQuery()(
        { url: "/auth/refresh", method: "POST" },
        api,
        extraOptions,
      );
      if (result.data && typeof result.data === "object") {
        const data = result.data as AccessTokenResponse;
        if (data.access_token) {
          api.dispatch(setAccessToken(data.access_token));
          return true;
        }
      }
      api.dispatch(clearAuth());
      return false;
    })().finally(() => {
      refreshInFlight = null;
    });
  }
  return refreshInFlight;
}

export const baseQueryWithReauth: AppBaseQuery = async (
  args,
  api,
  extraOptions,
) => {
  const rawBaseQuery = getRawBaseQuery();
  let result = await rawBaseQuery(args, api, extraOptions);
  const url = requestUrl(args);

  if (result.error?.status === 401 && !shouldSkipReauth(url)) {
    const refreshed = await refreshAccessToken(api, extraOptions);
    if (refreshed) {
      result = await rawBaseQuery(args, api, extraOptions);
    }
  }

  return result;
};
