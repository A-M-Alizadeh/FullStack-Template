/** Pull a human message from RTK Query / FastAPI errors (no React). */

function detailFromPayload(detail: unknown): string | null {
  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }
  // FastAPI / Pydantic validation: [{ loc, msg, type }, ...]
  if (Array.isArray(detail) && detail.length > 0) {
    const parts = detail
      .map((item) => {
        if (!item || typeof item !== "object") return null;
        const msg = "msg" in item ? (item as { msg: unknown }).msg : null;
        return typeof msg === "string" && msg.trim() ? msg : null;
      })
      .filter((m): m is string => Boolean(m));
    if (parts.length) {
      return parts.slice(0, 3).join("; ");
    }
  }
  return null;
}

export function getErrorMessage(
  error: unknown,
  fallback = "Something went wrong",
): string {
  if (!error || typeof error !== "object") {
    return fallback;
  }

  const data = "data" in error ? (error as { data?: unknown }).data : undefined;
  if (data && typeof data === "object" && data !== null && "detail" in data) {
    const fromDetail = detailFromPayload((data as { detail: unknown }).detail);
    if (fromDetail) {
      return fromDetail;
    }
  }

  if ("error" in error && typeof (error as { error: unknown }).error === "string") {
    return (error as { error: string }).error;
  }

  if ("status" in error && (error as { status: unknown }).status === 404) {
    return "Not found";
  }

  return fallback;
}
