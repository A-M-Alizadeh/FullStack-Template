import { getApiBaseUrl } from "./env";

/**
 * Turn API-relative asset paths (e.g. `/api/v1/passport/…/file`) into absolute
 * URLs against the FastAPI origin. Absolute http(s) URLs pass through.
 */
export function resolveApiAssetUrl(pathOrUrl: string): string {
  if (/^https?:\/\//i.test(pathOrUrl)) {
    return pathOrUrl;
  }
  const base = getApiBaseUrl();
  const origin = new URL(base).origin;
  if (pathOrUrl.startsWith("/")) {
    return `${origin}${pathOrUrl}`;
  }
  return `${base}/${pathOrUrl}`;
}
