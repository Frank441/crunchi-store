import type { Metadata } from "next";
import { Ubuntu, Inter } from "next/font/google";
import { Header } from '@/components';
import { ThemeRegistry } from '@/lib/mui';
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

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="es"
      className={`${ubuntu.variable} ${inter.variable} bg-background h-full antialiased`}
      data-scroll-behavior="smooth"
    >
      <body className={`${ubuntu.className} ${inter.className}`}>
        <ThemeRegistry>
          <Header />
          {children}
        </ThemeRegistry>
      </body>
    </html>
  );
}
