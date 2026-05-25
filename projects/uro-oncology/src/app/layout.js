import { Inter, Barlow } from 'next/font/google';
import './globals.css';
import Navbar from '@/components/Navbar';
import PreFooter from '@/components/PreFooter';
import Footer from '@/components/Footer';
import { GoogleAnalytics } from '@next/third-parties/google';

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
});

const barlow = Barlow({
  weight: ['400', '500', '600', '700'],
  subsets: ['latin'],
  variable: '--font-barlow',
});

export const metadata = {
  title: 'Uro-Oncology | Dr. Adalberto Castro Alfaro',
  description: 'Atención médica integral en urología y oncología. Especialista en cirugía robótica Da Vinci. Centro Médico Real San José Valle Real.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body className={`${inter.variable} ${barlow.variable}`}>
        <Navbar />
        <main>{children}</main>
        <PreFooter />
        <Footer />
        <a 
          href="https://api.whatsapp.com/send?phone=523316013840" 
          className="whatsapp-btn" 
          target="_blank" 
          rel="noopener noreferrer"
          aria-label="Contactar por WhatsApp"
        >
          <img src="/assets/iconos/whatsapp.png" alt="WhatsApp" width="30" height="30" />
        </a>
        <GoogleAnalytics gaId="G-5E1RH7HVGD" />
      </body>
    </html>
  );
}
