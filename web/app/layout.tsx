import type { Metadata, Viewport } from "next";
import { Poppins } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import { GlobalProvider } from "@/context/GlobalContext";
import { AgentTraceProvider } from "@/context/AgentTraceContext";
import ThemeScript from "@/components/ThemeScript";
import ServiceWorkerRegistration from "@/components/ServiceWorkerRegistration";
import GlobalAgentTrace from "@/components/GlobalAgentTrace";

// Use Poppins font for modern, premium look
const font = Poppins({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
  display: "swap",
  fallback: ["system-ui", "sans-serif"],
});

export const viewport: Viewport = {
  themeColor: "#059669",
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export const metadata: Metadata = {
  title: "Synchore - AI Learning Companion",
  description: "Personalized learning through Agentic AI for Pakistani students. PCTB curriculum aligned with Urdu support.",
  manifest: "/manifest.json",
  applicationName: "Synchore",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "Synchore",
  },
  formatDetection: {
    telephone: false,
  },
  icons: {
    icon: [
      { url: "/icons/icon-192x192.svg", sizes: "192x192", type: "image/svg+xml" },
      { url: "/icons/icon-512x512.svg", sizes: "512x512", type: "image/svg+xml" },
    ],
    apple: [
      { url: "/icons/icon-source.svg", sizes: "any", type: "image/svg+xml" },
    ],
  },
  keywords: ["education", "AI tutor", "Pakistan", "PCTB", "learning", "Urdu", "offline learning"],
  authors: [{ name: "Synchore Team" }],
  category: "education",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning style={{ backgroundColor: '#050505' }}>
      <head>
        <ThemeScript />
        <link rel="apple-touch-icon" href="/icons/icon-source.svg" />
        <link rel="icon" type="image/svg+xml" href="/icons/icon-192x192.svg" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="Synchore" />
      </head>
      <body className={font.className} style={{ backgroundColor: '#050505', minHeight: '100vh' }}>
        <GlobalProvider>
          <AgentTraceProvider>
            <ServiceWorkerRegistration />
            <GlobalAgentTrace />
            <div className="flex h-screen overflow-hidden" style={{ backgroundColor: '#050505' }}>
              <Sidebar />
              <main className="flex-1 overflow-y-auto" style={{ backgroundColor: '#050505' }}>
                {children}
              </main>
            </div>
          </AgentTraceProvider>
        </GlobalProvider>
      </body>
    </html>
  );
}
