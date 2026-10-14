import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { AuthProvider } from "@/lib/auth";
import { ThemeProvider } from "@/lib/theme";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "Research Assistant",
  description: "AI-powered personal research assistant",
};

const THEME_INIT_SCRIPT = `
(function() {
  try {
    var stored = localStorage.getItem('theme');
    var theme = stored || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    if (theme === 'dark') document.documentElement.classList.add('dark');
  } catch (e) {}
})();
`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
      </head>
      <body className="font-sans">
        <ThemeProvider>
          <AuthProvider>{children}</AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
