import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ContextMed — Globally Informed, Locally Accurate",
  description:
    "AI-powered clinical decision support. Right guideline, right geography, right drug, right source.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
