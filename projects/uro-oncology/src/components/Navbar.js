'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import ContactPopup from './ContactPopup';
import styles from './Navbar.module.css';

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const pathname = usePathname();

  let stripeText = "El pulso humano de la cirugía robótica contra el cáncer";
  if (pathname === '/diagnostico') stripeText = "Diagnóstico";
  else if (pathname === '/tipos-de-cirugia') stripeText = "Tipos de Cirugía";
  else if (pathname === '/equipo-medico') stripeText = "Dr. Adalberto Castro Alfaro | Urólogo";
  else if (pathname === '/preguntas-frecuentes') stripeText = "Preguntas Frecuentes";
  else if (pathname === '/aviso-de-privacidad') stripeText = "Aviso de Privacidad";
  else if (pathname === '/acerca-del-doctor') stripeText = "Dr. Adalberto Castro Alfaro";
  else if (pathname === '/cirugia-robotica') stripeText = "Cirugía Robótica";
  else if (pathname === '/cirugia-laparoscopica') stripeText = "Cirugía Laparoscópica";
  else if (pathname === '/cirugia-endourologica') stripeText = "Cirugía Endourológica";
  else if (pathname === '/diagnostico/cancer-de-prostata') stripeText = "Cáncer de Próstata";
  else if (pathname === '/diagnostico/cancer-de-rinon') stripeText = "Cáncer de Riñón";
  else if (pathname === '/diagnostico/cancer-de-testiculo') stripeText = "Cáncer de Testículo";
  else if (pathname === '/diagnostico/cancer-de-vejiga') stripeText = "Cáncer de Vejiga";
  else if (pathname === '/diagnostico/calculos-renales') stripeText = "Cálculos Renales";
  else if (pathname === '/diagnostico/crecimiento-de-prostata') stripeText = "Crecimiento de Próstata";
  else if (pathname === '/diagnostico/chekup-masculino') stripeText = "Checkup Masculino";
  else if (pathname === '/diagnostico/infertilidad-masculina') stripeText = "Infertilidad Masculina";
  else if (pathname === '/diagnostico/vasectomia') stripeText = "Vasectomía";

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header className={styles.header}>
      <nav className={styles.navbar}>
        <div className={styles.navContainer}>
          <Link href="/" className={styles.logo}>
            <Image src="/assets/logotipo/Logo light.svg" alt="Uro-oncology Logo" width={440} height={140} priority />
          </Link>

          <div className={`${styles.navLinks} ${menuOpen ? styles.open : ''}`}>
            <Link href="/" onClick={() => setMenuOpen(false)}>INICIO</Link>
            <Link href="/diagnostico" onClick={() => setMenuOpen(false)}>DIAGNÓSTICO</Link>
            <Link href="/tipos-de-cirugia" onClick={() => setMenuOpen(false)}>CIRUGÍAS</Link>
            <button 
              className={styles.contactNavLink} 
              onClick={(e) => {
                e.preventDefault();
                setMenuOpen(false);
                setIsPopupOpen(true);
              }}
            >
              CONTACTO
            </button>
          </div>

          <button 
            className={`${styles.mobileMenuBtn} ${menuOpen ? styles.menuBtnOpen : ''}`} 
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Toggle menu"
          >
            <span></span>
            <span></span>
            <span></span>
          </button>
        </div>
      </nav>
      <div className={styles.blueStripe}>
        <h1>{stripeText}</h1>
      </div>
      <ContactPopup isOpen={isPopupOpen} onClose={() => setIsPopupOpen(false)} />
    </header>
  );
}
