import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "{{PROJECT_NAME_TITLE}}",
  description: "{{DESCRIPTION}}",
  openGraph: {
    title: "{{PROJECT_NAME_TITLE}}",
    description: "{{DESCRIPTION}}",
    url: "https://{{DOMAIN}}",
    siteName: "{{PROJECT_NAME_TITLE}}",
    locale: "it_IT",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="it">
      <body className="antialiased">{children}</body>
    </html>
  );
}
