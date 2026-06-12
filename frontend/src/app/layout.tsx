import type { Metadata } from "next";
import { Ubuntu, Inter } from "next/font/google";
import { Header } from '@/components';
import { ThemeRegistry } from '@/lib/mui';
import { getSessionUser } from '@/lib/auth/getSessionUser';
import "./globals.css";

const ubuntu = Ubuntu({
  weight: ['300', '400', '500', '700'],
  style: ['normal', 'italic'],
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-ubuntu',
});

const inter = Inter({
  weight: ['300', '400', '500', '600', '700', '800', '900'],
  style: ['normal', 'italic'],
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter'
})



export const metadata: Metadata = {
  title: "CrunchiStore",
  description: "Encontrá al Otaku que hay en vos.",
  icons: "/logo.png"
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const user = await getSessionUser();

  return (
    <html
      lang="es"
      className={`${ubuntu.variable} ${inter.variable} bg-background h-full antialiased`}
      suppressHydrationWarning
    >
      <body className={`${ubuntu.className} ${inter.className}`}>
        <ThemeRegistry>
          <Header isAuthenticated={!!user} />
          {children}
        </ThemeRegistry>
      </body>
    </html>
  );
}
