/**
 * Session bootstrap without React — unit-test with fake refresh/loadMe.
 */

export type BootstrapResult = "authenticated" | "anonymous";

export type BootstrapDeps = {
  hasAccessToken: boolean;
  refresh: () => Promise<unknown>;
  loadMe: () => Promise<unknown>;
};

export async function bootstrapSession(
  deps: BootstrapDeps,
): Promise<BootstrapResult> {
  try {
    if (!deps.hasAccessToken) {
      await deps.refresh();
    }
    await deps.loadMe();
    return "authenticated";
  } catch {
    return "anonymous";
  }
}
