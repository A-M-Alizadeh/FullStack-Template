/** Public env helpers. Only `NEXT_PUBLIC_*` is available in the browser. */

export function getApiBaseUrl(): string {
  const value = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");
  if (!value) {
    throw new Error("NEXT_PUBLIC_API_URL is not set");
  }
  return value;
}

export function getAppName(): string {
  return process.env.NEXT_PUBLIC_APP_NAME?.trim() || "Digital Product Passport";
}
