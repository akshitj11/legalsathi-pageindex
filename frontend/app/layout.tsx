import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LegalSaathi - AI Legal Document Analyzer",
  description:
    "Understand your legal documents without any legal knowledge. Built for common Indians.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="hi">
      <body className="min-h-screen bg-background antialiased">
        {children}
      </body>
    </html>
  );
}
