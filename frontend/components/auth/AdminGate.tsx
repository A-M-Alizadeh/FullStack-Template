"use client";

import type { ReactNode } from "react";

import { RoleGate } from "./RoleGate";

type Props = { children: ReactNode };

/** Convenience wrapper — admin-only pages. Prefer RoleGate for new code. */
export function AdminGate({ children }: Props) {
  return <RoleGate roles={["admin"]}>{children}</RoleGate>;
}
