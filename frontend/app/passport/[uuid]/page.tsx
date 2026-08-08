import { Suspense } from "react";

import { PublicPassportView } from "@/features/passport/PublicPassportView";

type PassportPageProps = {
  params: Promise<{ uuid: string }>;
};

/** Public route — no AuthGate. Forwards ?src=qr to the API for scan tracking. */
export default async function PublicPassportPage({ params }: PassportPageProps) {
  const { uuid } = await params;

  return (
    <Suspense fallback={null}>
      <PublicPassportView uuid={uuid} />
    </Suspense>
  );
}
