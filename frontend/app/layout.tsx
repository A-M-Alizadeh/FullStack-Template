import type { Metadata } from "next";
import { AppProviders } from "@/components/AppProviders";
import "./globals.css";

const appName = process.env.NEXT_PUBLIC_APP_NAME;

export const metadata: Metadata = {
  title: appName,
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
