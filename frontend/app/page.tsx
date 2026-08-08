import { redirect } from "next/navigation";

import { DEFAULT_AUTHENTICATED_PATH } from "@/lib/navigation";

/** Entry → back-office; AuthGate sends anonymous users to /login. */
export default function HomePage() {
  redirect(DEFAULT_AUTHENTICATED_PATH);
}
