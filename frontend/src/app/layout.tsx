import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/Providers";
import { StickyHeader } from "@/components/StickyHeader";

const jakarta = Plus_Jakarta_Sans({
  variable: "--font-jakarta",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "AI Skin Health Monitor",
  description: "Non-diagnostic skin health awareness — capture or upload a photo for AI-driven analysis.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${jakarta.variable} font-sans`}>
        <Providers>
          <StickyHeader />
          {children}
        </Providers>
      </body>
    </html>
  );
}
