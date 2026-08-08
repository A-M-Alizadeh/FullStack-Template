/** Pull a human message from RTK Query / FastAPI errors (no React). */

export function getErrorMessage(
  error: unknown,
  fallback = "Something went wrong",
): string {
  if (!error || typeof error !== "object") {
    return fallback;
  }

  const data = "data" in error ? (error as { data?: unknown }).data : undefined;
  if (data && typeof data === "object" && data !== null && "detail" in data) {
    const detail = (data as { detail: unknown }).detail;
    if (typeof detail === "string" && detail.trim()) {
      return detail;
    }
  }

  if ("error" in error && typeof (error as { error: unknown }).error === "string") {
    return (error as { error: string }).error;
  }

  return fallback;
}
