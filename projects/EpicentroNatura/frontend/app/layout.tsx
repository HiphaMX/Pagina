import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Epicentro Natura | Ecosistema Hiperlocal Natura Bosque",
  description:
    "Directorio comercial, microemprendimientos en coto, agenda cultural de la Casa de la Cultura y tablero cívico para Natura Bosque Residencial (Zapopan).",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased selection:bg-natura-200 selection:text-natura-900">
        {children}
      </body>
    </html>
  );
}
