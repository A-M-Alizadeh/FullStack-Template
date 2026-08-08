import type { Metadata } from "next";

import { AppProviders } from "@/components/AppProviders";
import { getAppName } from "@/lib/env";

import "./globals.css";

export const metadata: Metadata = {
  title: getAppName(),
  description: "Manage and publish digital product passports",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
