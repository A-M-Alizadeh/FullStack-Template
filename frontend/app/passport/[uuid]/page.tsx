type PassportPageProps = {
  params: Promise<{ uuid: string }>;
};

/** Public route (no AuthGate). Data wiring in a later step. */
export default async function PublicPassportPage({ params }: PassportPageProps) {
  const { uuid } = await params;

  return (
    <main style={{ padding: 24, maxWidth: 720, margin: "0 auto" }}>
      <h1>Product passport</h1>
      <p>Passport id: {uuid}</p>
    </main>
  );
}
