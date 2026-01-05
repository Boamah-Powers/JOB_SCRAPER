import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "Job Scraper - Your Intelligent Job Market Tracking System",
  description: "Discover and track job opportunities from multiple sources. Browse thousands of job postings, save your favorites, and manage your job applications all in one place. Features advanced filtering, application status tracking, and personalized dashboard.",
  keywords: ["job search", "job tracking", "application tracker", "job board", "career management", "job listings"],
  authors: [{ name: "Kwaaku Boamah-Powers" }],
  openGraph: {
    title: "Job Scraper - Your Intelligent Job Market Tracking System",
    description: "Discover and track job opportunities from multiple sources. Browse, save, and manage your job applications efficiently.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
